"""Apply the rules to Home Assistant's assistant exposure.

The manager owns the lifecycle: it listens for anything that could change
what a rule selects (registry events, group state, a periodic safety resync),
recomputes the plan with the pure engine, and applies the difference to
Home Assistant's exposure settings. The rules are the single source of truth
for every managed assistant: anything not wanted is un-exposed, including
what someone ticked by hand in Settings.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    floor_registry as fr,
    issue_registry as ir,
    label_registry as lr,
)
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .api import ActionRegistry, async_get_registry
from .const import (
    ASSISTANT_LABELS,
    CONF_RULES,
    CONF_SETTINGS,
    DEBOUNCE_SECONDS,
    DOMAIN,
    ISSUE_TOO_MANY,
    RESYNC_INTERVAL,
    SIGNAL_UPDATED,
)
from .engine import (
    ActionSpec,
    EXPOSE,
    Plan,
    Rule,
    Settings,
    estimated_tokens,
    evaluate,
    plan_changes,
)
from .snapshot import build_facts

_LOGGER = logging.getLogger(__name__)

_REGISTRY_EVENTS = (
    er.EVENT_ENTITY_REGISTRY_UPDATED,
    dr.EVENT_DEVICE_REGISTRY_UPDATED,
    ar.EVENT_AREA_REGISTRY_UPDATED,
    fr.EVENT_FLOOR_REGISTRY_UPDATED,
    lr.EVENT_LABEL_REGISTRY_UPDATED,
)


@dataclass
class TargetResult:
    """The outcome for one target of one action type (an assistant for expose)."""

    target: str
    desired: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    refused: bool = False
    # What the target actually has once this run finished (differs from
    # `desired` when the plan was refused or this was a dry run).
    exposed: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def count(self) -> int:
        return len(self.desired)


# 0.1 name, kept for readers of the old code.
AssistantResult = TargetResult


@dataclass
class ApplyResult:
    dry_run: bool
    at: datetime
    # action type -> target -> result. ``assistants`` is the expose entry.
    actions: dict[str, dict[str, TargetResult]] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    rule_names: dict[str, str] = field(default_factory=dict)
    blocked: dict[str, str] = field(default_factory=dict)
    dormant: dict[str, list[str]] = field(default_factory=dict)

    @property
    def assistants(self) -> dict[str, TargetResult]:
        return self.actions.setdefault(EXPOSE, {})

    def to_dict(self) -> dict[str, Any]:
        def target_dict(r: TargetResult) -> dict[str, Any]:
            return {
                "count": r.count,
                "estimated_tokens": estimated_tokens(r.count),
                "refused": r.refused,
                "added": r.added,
                "removed": r.removed,
                "entities": r.desired,
                "exposed_now": r.exposed,
                "error": r.error,
            }

        return {
            "dry_run": self.dry_run,
            "at": self.at.isoformat(),
            "assistants": {a: target_dict(r) for a, r in self.assistants.items()},
            "actions": {
                type_id: {t: target_dict(r) for t, r in targets.items()}
                for type_id, targets in self.actions.items()
                if type_id != EXPOSE
            },
            "rules": {
                self.rule_names.get(rid, rid): count
                for rid, count in self.by_rule.items()
            },
            "blocked": self.blocked,
            "dormant": {
                self.rule_names.get(rid, rid): types
                for rid, types in self.dormant.items()
            },
        }


class ExposureManager:
    """Keeps assistant exposure equal to what the rules say."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.last: ApplyResult | None = None
        self._lock = asyncio.Lock()
        self.registry: ActionRegistry = async_get_registry(hass)
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.state")
        # Remembered between runs: the last selection of edge targets, and
        # state targets we have applied, so removing the last rule that named
        # a target still cleans it up.
        self._edge: dict[str, dict[str, list[str]]] = {}
        self._seen: dict[str, list[str]] = {}
        self._unsubs: list[Callable[[], None]] = []
        self._state_unsub: Callable[[], None] | None = None
        self._debouncer = Debouncer(
            hass,
            _LOGGER,
            cooldown=DEBOUNCE_SECONDS,
            immediate=False,
            function=self._debounced_apply,
        )

    # ------------------------------------------------------------- config

    @property
    def rules(self) -> list[Rule]:
        out = []
        for raw in self.entry.options.get(CONF_RULES, []):
            try:
                out.append(Rule.from_dict(raw))
            except (KeyError, TypeError, ValueError):
                _LOGGER.warning("Ignoring malformed PropSense rule: %s", raw)
        return out

    @property
    def settings(self) -> Settings:
        return Settings.from_dict(self.entry.options.get(CONF_SETTINGS))

    # ---------------------------------------------------------- lifecycle

    async def async_start(self) -> None:
        saved = await self._store.async_load() or {}
        self._edge = saved.get("edge", {})
        self._seen = saved.get("seen", {})
        self._unsubs.append(self.registry.async_add_listener(self._on_registry_change))
        for event_type in _REGISTRY_EVENTS:
            self._unsubs.append(
                self.hass.bus.async_listen(event_type, self._on_registry_event)
            )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._on_interval, RESYNC_INTERVAL)
        )
        self._track_group_states()

        if self.hass.state is CoreState.running:
            self._debouncer.async_schedule_call()
        else:
            self._unsubs.append(
                self.hass.bus.async_listen_once(
                    EVENT_HOMEASSISTANT_STARTED, self._on_started
                )
            )

    async def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None
        self._debouncer.async_cancel()

    # ------------------------------------------------------------ triggers

    @callback
    def _on_registry_change(self) -> None:
        self._debouncer.async_schedule_call()

    @callback
    def _on_started(self, _event: Event) -> None:
        self._debouncer.async_schedule_call()

    @callback
    def _on_interval(self, _now: datetime) -> None:
        self._debouncer.async_schedule_call()

    @callback
    def _on_registry_event(self, event: Event) -> None:
        # Applying exposure writes the entity's options, which itself fires an
        # entity-registry update. Ignore updates that only touch options so we
        # do not chase our own tail.
        data = event.data
        if (
            event.event_type == er.EVENT_ENTITY_REGISTRY_UPDATED
            and data.get("action") == "update"
            and set(data.get("changes", {})) <= {"options"}
        ):
            return
        self._debouncer.async_schedule_call()

    @callback
    def _on_group_state(self, _event: Event) -> None:
        self._debouncer.async_schedule_call()

    def _track_group_states(self) -> None:
        """Re-evaluate when a group a rule refers to changes its members."""
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None
        group_ids = self._group_ids(self.rules)
        if group_ids:
            self._state_unsub = async_track_state_change_event(
                self.hass, list(group_ids), self._on_group_state
            )

    @staticmethod
    def _group_ids(rules: list[Rule]) -> set[str]:
        return {
            g
            for r in rules
            if r.enabled
            for sel in (r.include, r.exclude)
            for g in sel.groups
        }

    async def _debounced_apply(self) -> None:
        await self.async_apply()

    # --------------------------------------------------------------- apply

    def _specs(self, settings: Settings) -> dict[str, ActionSpec]:
        """Action types that may run: built in, or third-party when allowed."""
        return {
            type_id: action.spec()
            for type_id, action in self.registry.types.items()
            if self.registry.is_builtin(type_id) or settings.allow_third_party_actions
        }

    def compute_plan(self) -> tuple[Plan, list[Rule], Settings]:
        rules = self.rules
        settings = self.settings
        facts = build_facts(self.hass, settings, self._group_ids(rules))
        plan = evaluate(
            rules,
            facts,
            settings,
            specs=self._specs(settings),
            extra_managed=self._seen,
        )
        return plan, rules, settings

    async def _save_state(self) -> None:
        await self._store.async_save({"edge": self._edge, "seen": self._seen})

    async def async_apply(self, dry_run: bool | None = None) -> ApplyResult:
        """Recompute the plan and make every action's targets match it."""
        async with self._lock:
            plan, rules, settings = self.compute_plan()
            dry = settings.dry_run if dry_run is None else dry_run

            result = ApplyResult(
                dry_run=dry,
                at=datetime.now(timezone.utc),
                by_rule={rid: len(ids) for rid, ids in plan.by_rule.items()},
                rule_names={r.id: r.name for r in rules},
                blocked=dict(plan.blocked),
                dormant={rid: sorted(t) for rid, t in plan.dormant.items()},
            )
            _ = result.assistants  # expose is always reported, even when empty

            state_changed = False
            for type_id in sorted(plan.managed_targets):
                action = self.registry.get(type_id)
                if action is None:
                    continue
                results = result.actions.setdefault(type_id, {})
                for target in sorted(plan.managed_targets[type_id]):
                    desired = plan.targets[type_id].get(target, set())
                    try:
                        tres, changed = await self._apply_target(
                            action, target, desired, settings, dry
                        )
                    except Exception as err:  # a provider must not break the rest
                        _LOGGER.exception(
                            "PropSense action %s failed for target %s", type_id, target
                        )
                        tres = TargetResult(
                            target=target, desired=sorted(desired), error=str(err)
                        )
                        changed = False
                    results[target] = tres
                    state_changed |= changed

            if not dry:
                if state_changed:
                    await self._save_state()
                self.last = result
                async_dispatcher_send(self.hass, SIGNAL_UPDATED)
            return result

    async def _apply_target(
        self,
        action,
        target: str,
        desired: set[str],
        settings: Settings,
        dry: bool,
    ) -> tuple[TargetResult, bool]:
        """Apply one target. Returns its result and whether stored state changed."""
        type_id = action.type_id

        if action.mode == "edge":
            previous = self._edge.get(type_id, {}).get(target)
            if previous is None:
                # First sight: record the selection, fire nothing.
                add, remove = set(), set()
            else:
                add, remove = desired - set(previous), set(previous) - desired
            tres = TargetResult(
                target=target,
                desired=sorted(desired),
                added=sorted(add),
                removed=sorted(remove),
                exposed=sorted(desired if previous is not None else []),
            )
            if dry:
                return tres, False
            if add or remove:
                await action.async_apply(target, add, remove)
            self._edge.setdefault(type_id, {})[target] = sorted(desired)
            tres.exposed = sorted(desired)
            return tres, previous is None or bool(add or remove)

        current = await action.async_current(target)
        changes = plan_changes(current, desired, settings.max_exposed)
        tres = TargetResult(
            target=target,
            desired=sorted(desired),
            added=sorted(changes.add),
            removed=sorted(changes.remove),
            refused=changes.refused,
            exposed=sorted(current),
        )

        issue_id = (
            f"{ISSUE_TOO_MANY}_{target}"
            if type_id == EXPOSE
            else f"{ISSUE_TOO_MANY}_{type_id}_{target}"
        )
        label = action.target_label(target)
        if changes.refused:
            # Fail safe: leave the target as it is rather than blow past the
            # size a small model can hold.
            tres.added, tres.removed = [], []
            if not dry:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    issue_id,
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key=ISSUE_TOO_MANY,
                    translation_placeholders={
                        "assistant": label,
                        "count": str(changes.desired_count),
                        "max": str(settings.max_exposed),
                    },
                )
            _LOGGER.warning(
                "PropSense refused to apply %d entities to %s (limit %d); "
                "left unchanged",
                changes.desired_count,
                label,
                settings.max_exposed,
            )
            return tres, False

        if dry:
            return tres, False

        ir.async_delete_issue(self.hass, DOMAIN, issue_id)
        if changes.add or changes.remove:
            await action.async_apply(target, set(changes.add), set(changes.remove))
            _LOGGER.info(
                "PropSense %s %s: +%d -%d (now %d)",
                type_id,
                label,
                len(changes.add),
                len(changes.remove),
                len(desired),
            )
        tres.exposed = sorted(desired)

        changed = False
        if type_id != EXPOSE:
            # Remember the target while it has anything, so deleting the last
            # rule that names it still removes what we added.
            seen = set(self._seen.get(type_id, []))
            new = seen | {target} if desired else seen - {target}
            if new != seen:
                self._seen[type_id] = sorted(new)
                changed = True
        return tres, changed
