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

from homeassistant.components.homeassistant.exposed_entities import (
    async_expose_entity,
    async_get_assistant_settings,
)
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
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

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
class AssistantResult:
    assistant: str
    desired: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    refused: bool = False
    # What is actually exposed once this run finished (differs from `desired`
    # when the plan was refused or this was a dry run).
    exposed: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.desired)


@dataclass
class ApplyResult:
    dry_run: bool
    at: datetime
    assistants: dict[str, AssistantResult] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    rule_names: dict[str, str] = field(default_factory=dict)
    blocked: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "at": self.at.isoformat(),
            "assistants": {
                a: {
                    "count": r.count,
                    "estimated_tokens": estimated_tokens(r.count),
                    "refused": r.refused,
                    "added": r.added,
                    "removed": r.removed,
                    "entities": r.desired,
                    "exposed_now": r.exposed,
                }
                for a, r in self.assistants.items()
            },
            "rules": {
                self.rule_names.get(rid, rid): count
                for rid, count in self.by_rule.items()
            },
            "blocked": self.blocked,
        }


class ExposureManager:
    """Keeps assistant exposure equal to what the rules say."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.last: ApplyResult | None = None
        self._lock = asyncio.Lock()
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

    def _current_exposed(self, assistant: str) -> set[str]:
        return {
            entity_id
            for entity_id, options in async_get_assistant_settings(
                self.hass, assistant
            ).items()
            if options.get("should_expose")
        }

    def compute_plan(self) -> tuple[Plan, list[Rule], Settings]:
        rules = self.rules
        settings = self.settings
        facts = build_facts(self.hass, settings, self._group_ids(rules))
        return evaluate(rules, facts, settings), rules, settings

    async def async_apply(self, dry_run: bool | None = None) -> ApplyResult:
        """Recompute the plan and make exposure match it."""
        async with self._lock:
            plan, rules, settings = self.compute_plan()
            dry = settings.dry_run if dry_run is None else dry_run

            result = ApplyResult(
                dry_run=dry,
                at=datetime.now(timezone.utc),
                by_rule={rid: len(ids) for rid, ids in plan.by_rule.items()},
                rule_names={r.id: r.name for r in rules},
                blocked=dict(plan.blocked),
            )

            for assistant in sorted(plan.managed):
                desired = plan.desired.get(assistant, set())
                current = self._current_exposed(assistant)
                changes = plan_changes(current, desired, settings.max_exposed)
                ares = AssistantResult(
                    assistant=assistant,
                    desired=sorted(desired),
                    added=sorted(changes.add),
                    removed=sorted(changes.remove),
                    refused=changes.refused,
                    exposed=sorted(current),
                )
                result.assistants[assistant] = ares

                issue_id = f"{ISSUE_TOO_MANY}_{assistant}"
                if changes.refused:
                    # Fail safe: leave exposure as it is rather than blow past
                    # the size a small model can hold.
                    ares.added, ares.removed = [], []
                    if not dry:
                        ir.async_create_issue(
                            self.hass,
                            DOMAIN,
                            issue_id,
                            is_fixable=False,
                            severity=ir.IssueSeverity.WARNING,
                            translation_key=ISSUE_TOO_MANY,
                            translation_placeholders={
                                "assistant": ASSISTANT_LABELS.get(assistant, assistant),
                                "count": str(changes.desired_count),
                                "max": str(settings.max_exposed),
                            },
                        )
                    _LOGGER.warning(
                        "PropSense refused to expose %d entities to %s (limit %d); "
                        "exposure left unchanged",
                        changes.desired_count,
                        assistant,
                        settings.max_exposed,
                    )
                    continue

                if not dry:
                    ir.async_delete_issue(self.hass, DOMAIN, issue_id)
                    for entity_id in ares.added:
                        async_expose_entity(self.hass, assistant, entity_id, True)
                    for entity_id in ares.removed:
                        async_expose_entity(self.hass, assistant, entity_id, False)
                    ares.exposed = sorted(desired)
                    if ares.added or ares.removed:
                        _LOGGER.info(
                            "PropSense %s: +%d -%d (now %d exposed)",
                            assistant,
                            len(ares.added),
                            len(ares.removed),
                            len(desired),
                        )

            if not dry:
                self.last = result
                async_dispatcher_send(self.hass, SIGNAL_UPDATED)
            return result
