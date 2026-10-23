"""The PropSense rules engine: pure policy, no Home Assistant imports.

Everything that decides *what* should be exposed lives here, so it can be
tested exhaustively without a running Home Assistant. The glue that reads
Home Assistant's registries and applies the result lives in ``snapshot.py``
and ``manager.py``.

The model, in one paragraph. A **rule** has an **include** selector, an
optional **exclude** selector, and an **action** (today: expose the matching
entities to one or more assistants). A selector is a set of optional fields
(labels, areas, floors, domains, device classes, entities, devices, groups).
Within one field a list means "any of these"; across fields every non-empty
field must match ("and"). A selector with no fields matches nothing: rules
fail closed. Rules are additive (an entity is wanted if any enabled rule
includes it and none of that rule's excludes match), and the result is the
**single source of truth**: for every managed assistant, anything not wanted
is not exposed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping

# Rough prompt cost of one exposed entity for an LLM conversation agent, from
# a measured deployment (303 exposed entities produced a ~9,050 token request
# against a ~1,300 token base). Advisory only: it drives warnings, not logic.
TOKENS_PER_ENTITY = 26

SELECTOR_FIELDS = (
    "labels",
    "areas",
    "floors",
    "domains",
    "device_classes",
    "entities",
    "devices",
    "groups",
    "capabilities",
)

# Capability tags derived from an entity's state (see snapshot.py). Matching is
# any-of, like labels.
CAPABILITIES = (
    # light
    "onoff", "brightness", "color_temp", "color", "white",
    # cover
    "position", "tilt",
    # fan
    "speed", "oscillate", "direction", "preset",
    # climate
    "heat", "cool", "heat_cool", "auto", "dry", "fan_only", "target_temp",
)


def _fset(value: Any) -> frozenset[str]:
    if not value:
        return frozenset()
    if isinstance(value, str):
        return frozenset({value})
    return frozenset(str(v) for v in value)


@dataclass(frozen=True)
class EntityFacts:
    """Everything the engine may know about one entity, already resolved.

    Label inheritance, area fallback to the device, and floor lookup are done
    by the caller (``snapshot.py``); the engine only compares.
    """

    entity_id: str
    labels: frozenset[str] = frozenset()
    area_id: str | None = None
    floor_id: str | None = None
    device_id: str | None = None
    device_class: str | None = None
    groups: frozenset[str] = frozenset()
    capabilities: frozenset[str] = frozenset()

    @property
    def domain(self) -> str:
        return self.entity_id.split(".", 1)[0]


@dataclass(frozen=True)
class Selector:
    labels: frozenset[str] = frozenset()
    areas: frozenset[str] = frozenset()
    floors: frozenset[str] = frozenset()
    domains: frozenset[str] = frozenset()
    device_classes: frozenset[str] = frozenset()
    entities: frozenset[str] = frozenset()
    devices: frozenset[str] = frozenset()
    groups: frozenset[str] = frozenset()
    capabilities: frozenset[str] = frozenset()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Selector":
        data = data or {}
        return cls(**{name: _fset(data.get(name)) for name in SELECTOR_FIELDS})

    def to_dict(self) -> dict[str, list[str]]:
        return {name: sorted(getattr(self, name)) for name in SELECTOR_FIELDS}

    @property
    def is_empty(self) -> bool:
        return not any(getattr(self, name) for name in SELECTOR_FIELDS)

    def matches(self, facts: EntityFacts) -> bool:
        """All non-empty fields must match; within a field, any value will do.

        An empty selector matches nothing, so a half-edited rule can never
        expose everything.
        """
        if self.is_empty:
            return False
        if self.labels and not (self.labels & facts.labels):
            return False
        if self.areas and facts.area_id not in self.areas:
            return False
        if self.floors and facts.floor_id not in self.floors:
            return False
        if self.domains and facts.domain not in self.domains:
            return False
        if self.device_classes and facts.device_class not in self.device_classes:
            return False
        if self.entities and facts.entity_id not in self.entities:
            return False
        if self.devices and facts.device_id not in self.devices:
            return False
        if self.groups and not (self.groups & facts.groups):
            return False
        if self.capabilities and not (self.capabilities & facts.capabilities):
            return False
        return True


EXPOSE = "expose"
DEFAULT_ASSISTANTS = frozenset({"conversation"})


@dataclass(frozen=True)
class Action:
    """One thing a rule does to the entities it selects.

    ``type`` names an action type (``expose`` is built in, others are
    registered by other integrations); ``config`` is that type's own options.
    """

    type: str
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Action":
        return cls(type=str(data["type"]), config=dict(data.get("config") or {}))

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "config": dict(self.config)}


@dataclass(frozen=True)
class ActionSpec:
    """What the pure engine needs to know about an action type.

    ``mode`` is ``state`` (reconciled: unselected entities are removed from
    each target) or ``edge`` (fires when an entity enters or leaves a target's
    selection). ``targets`` maps an action's config to the targets it addresses,
    for example assistants or child instances.
    """

    type_id: str
    targets: Callable[[dict[str, Any]], frozenset[str]]
    mode: str = "state"
    respects_blocked_domains: bool = True
    # Optional filter: can this entity be a member of the target? Entities it
    # refuses are skipped and reported like blocked ones.
    accepts: Callable[[dict[str, Any], str], str | None] | None = None


def _expose_targets(config: dict[str, Any]) -> frozenset[str]:
    return _fset(config.get("assistants")) or DEFAULT_ASSISTANTS


EXPOSE_SPEC = ActionSpec(type_id=EXPOSE, targets=_expose_targets)


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    enabled: bool = True
    include: Selector = field(default_factory=Selector)
    exclude: Selector = field(default_factory=Selector)
    actions: tuple[Action, ...] = (Action(EXPOSE, {"assistants": ["conversation"]}),)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        if "actions" in data:
            actions = tuple(Action.from_dict(a) for a in data["actions"] or [])
        else:
            # 0.1 rules carried only `assistants`: an implicit expose action.
            assistants = _fset(data.get("assistants")) or DEFAULT_ASSISTANTS
            actions = (Action(EXPOSE, {"assistants": sorted(assistants)}),)
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            enabled=bool(data.get("enabled", True)),
            include=Selector.from_dict(data.get("include")),
            exclude=Selector.from_dict(data.get("exclude")),
            actions=actions,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "include": self.include.to_dict(),
            "exclude": self.exclude.to_dict(),
            "actions": [a.to_dict() for a in self.actions],
        }

    @property
    def assistants(self) -> frozenset[str]:
        """Assistants this rule exposes to (its ``expose`` actions)."""
        out: set[str] = set()
        for a in self.actions:
            if a.type == EXPOSE:
                out |= _expose_targets(a.config)
        return frozenset(out)

    def selects(self, facts: EntityFacts) -> bool:
        return self.include.matches(facts) and not self.exclude.matches(facts)


@dataclass(frozen=True)
class Settings:
    # Assistants whose exposure PropSense owns even when no rule currently
    # targets them, so removing the last rule un-exposes what it exposed.
    managed_assistants: frozenset[str] = frozenset({"conversation"})
    # Domains that are never exposed, whatever a rule says (fail closed).
    blocked_domains: frozenset[str] = frozenset(
        {"lock", "alarm_control_panel", "camera"}
    )
    # Refuse to apply a plan that would expose more than this many entities
    # to one assistant. 0 disables the guard.
    max_exposed: int = 100
    inherit_device_labels: bool = True
    inherit_area_labels: bool = False
    dry_run: bool = False
    # Third-party action types (registered by other integrations) stay dormant
    # until this is on, because they can do more than change exposure.
    allow_third_party_actions: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Settings":
        data = data or {}
        defaults = cls()
        return cls(
            managed_assistants=_fset(data.get("managed_assistants"))
            or defaults.managed_assistants,
            blocked_domains=(
                _fset(data["blocked_domains"])
                if "blocked_domains" in data
                else defaults.blocked_domains
            ),
            max_exposed=int(data.get("max_exposed", defaults.max_exposed)),
            inherit_device_labels=bool(
                data.get("inherit_device_labels", defaults.inherit_device_labels)
            ),
            inherit_area_labels=bool(
                data.get("inherit_area_labels", defaults.inherit_area_labels)
            ),
            dry_run=bool(data.get("dry_run", defaults.dry_run)),
            allow_third_party_actions=bool(
                data.get(
                    "allow_third_party_actions", defaults.allow_third_party_actions
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "managed_assistants": sorted(self.managed_assistants),
            "blocked_domains": sorted(self.blocked_domains),
            "max_exposed": self.max_exposed,
            "inherit_device_labels": self.inherit_device_labels,
            "inherit_area_labels": self.inherit_area_labels,
            "dry_run": self.dry_run,
            "allow_third_party_actions": self.allow_third_party_actions,
        }


@dataclass
class Plan:
    """What the rules want, before anything is applied."""

    # action type -> target -> entity ids the target should have
    targets: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    # action type -> targets PropSense manages (rule targets, the setting for
    # expose, and targets remembered from earlier runs)
    managed_targets: dict[str, set[str]] = field(default_factory=dict)
    # rule id -> entity ids it selected (after excludes and the block list)
    by_rule: dict[str, set[str]] = field(default_factory=dict)
    # entity id -> why a selected entity was dropped
    blocked: dict[str, str] = field(default_factory=dict)
    # rule id -> action types that could not be evaluated (no provider, or
    # third-party actions are not allowed)
    dormant: dict[str, set[str]] = field(default_factory=dict)

    @property
    def desired(self) -> dict[str, set[str]]:
        """assistant -> entity ids to expose (the built-in action)."""
        return self.targets.get(EXPOSE, {})

    @property
    def managed(self) -> set[str]:
        """Assistants PropSense manages."""
        return self.managed_targets.get(EXPOSE, set())


def evaluate(
    rules: Iterable[Rule],
    facts: Iterable[EntityFacts],
    settings: Settings,
    specs: Mapping[str, ActionSpec] | None = None,
    extra_managed: Mapping[str, Iterable[str]] | None = None,
) -> Plan:
    """Compute what should happen. Pure: same inputs, same plan.

    ``specs`` are the action types that may run; actions of any other type are
    reported as dormant and never touch anything.
    """
    specs = {EXPOSE: EXPOSE_SPEC} if specs is None else specs
    rules = [r for r in rules if r.enabled]
    facts = list(facts)

    plan = Plan()
    plan.managed_targets[EXPOSE] = set(settings.managed_assistants)
    for type_id, targets in (extra_managed or {}).items():
        if type_id in specs:
            plan.managed_targets.setdefault(type_id, set()).update(targets)

    # (rule, spec, config, targets) for every runnable action
    runnable: list[tuple[Rule, ActionSpec, dict[str, Any], frozenset[str]]] = []
    for rule in rules:
        plan.by_rule[rule.id] = set()
        for action in rule.actions:
            spec = specs.get(action.type)
            if spec is None:
                plan.dormant.setdefault(rule.id, set()).add(action.type)
                continue
            targets = spec.targets(action.config)
            plan.managed_targets.setdefault(spec.type_id, set()).update(targets)
            runnable.append((rule, spec, action.config, targets))

    for type_id, managed in plan.managed_targets.items():
        plan.targets[type_id] = {target: set() for target in managed}

    for f in facts:
        for rule, spec, config, targets in runnable:
            if not rule.selects(f):
                continue
            if spec.respects_blocked_domains and f.domain in settings.blocked_domains:
                plan.blocked[f.entity_id] = f"domain '{f.domain}' is blocked"
                continue
            if spec.accepts is not None and (
                why := spec.accepts(config, f.entity_id)
            ):
                plan.blocked[f.entity_id] = why
                continue
            plan.by_rule[rule.id].add(f.entity_id)
            for target in targets:
                plan.targets[spec.type_id][target].add(f.entity_id)
    return plan


@dataclass(frozen=True)
class Changes:
    """The difference between what is exposed now and what is wanted."""

    add: frozenset[str]
    remove: frozenset[str]
    # Set when the plan was refused by the max_exposed guard; nothing is
    # changed for that assistant in that case.
    refused: bool = False
    desired_count: int = 0


def plan_changes(current: set[str], desired: set[str], max_exposed: int) -> Changes:
    """Diff current exposure against the plan, honouring the size guard."""
    if max_exposed and len(desired) > max_exposed:
        return Changes(frozenset(), frozenset(), True, len(desired))
    return Changes(
        add=frozenset(desired - current),
        remove=frozenset(current - desired),
        refused=False,
        desired_count=len(desired),
    )


def estimated_tokens(count: int) -> int:
    return count * TOKENS_PER_ENTITY


def explain(
    rules: Iterable[Rule],
    f: EntityFacts,
    settings: Settings,
    specs: Mapping[str, ActionSpec] | None = None,
) -> list[dict[str, Any]]:
    """Why is (or isn't) one entity selected? One entry per rule."""
    specs = {EXPOSE: EXPOSE_SPEC} if specs is None else specs
    out: list[dict[str, Any]] = []
    for rule in rules:
        included = rule.include.matches(f)
        excluded = rule.exclude.matches(f)
        actions = []
        for action in rule.actions:
            spec = specs.get(action.type)
            if spec is None:
                status, targets = "dormant", []
            else:
                targets = sorted(spec.targets(action.config))
                if not (rule.enabled and included and not excluded):
                    status = "not selected"
                elif spec.respects_blocked_domains and f.domain in settings.blocked_domains:
                    status = "blocked"
                else:
                    status = "applies"
            actions.append({"type": action.type, "targets": targets, "status": status})
        out.append(
            {
                "rule_id": rule.id,
                "name": rule.name,
                "enabled": rule.enabled,
                "included": included,
                "excluded": excluded,
                "actions": actions,
            }
        )
    return out
