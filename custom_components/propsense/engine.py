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
from fnmatch import fnmatchcase
from functools import lru_cache
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
    "integrations",
    "manufacturers",
    "models",
    "entity_categories",
    "name_patterns",
    "label_patterns",
    "states",
    "conditions",
)

# Values of ``entity_categories``: Home Assistant's two categories, plus
# "primary" for entities that have none.
ENTITY_CATEGORIES = ("primary", "config", "diagnostic")

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


def _glob(patterns: frozenset[str], value: str | None) -> bool:
    """Case-insensitive shell-style match (``*`` and ``?``) of any pattern."""
    if not value:
        return False
    folded = value.casefold()
    return any(fnmatchcase(folded, p.casefold()) for p in patterns)


# ---------------------------------------------------------- conditions
#
# A condition reads the entity's own state or one of its attributes:
#   state < 20            attr:battery_level <= 15
#   state = on            attr:hvac_action != idle
#   state between 10 20   attr:brightness > 200
# Ordering and ``between`` need numbers on both sides; ``=`` and ``!=`` compare
# numbers numerically and anything else as text, ignoring case. A missing value
# never satisfies a condition.

CONDITION_OPS = ("between", "<=", ">=", "!=", "=", "<", ">")


@dataclass(frozen=True)
class Condition:
    source: str  # "state" or an attribute name
    op: str
    a: str
    b: str | None = None


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out and out not in (float("inf"), float("-inf")) else None


@lru_cache(maxsize=512)
def parse_condition(text: str) -> Condition:
    """Parse ``<source> <op> <value>``; raises ValueError if it makes no sense."""
    parts = str(text).strip().split(None, 2)
    if len(parts) < 3:
        raise ValueError(f"Expected '<state or attr:name> <operator> <value>', got {text!r}")
    source, op, rest = parts
    if source != "state" and not (source.startswith("attr:") and len(source) > 5):
        raise ValueError(f"The left side must be 'state' or 'attr:<attribute>', got {source!r}")
    if op not in CONDITION_OPS:
        raise ValueError(f"Unknown operator {op!r}; use one of {', '.join(CONDITION_OPS)}")
    name = "state" if source == "state" else source[5:]
    if op == "between":
        bounds = rest.split()
        if len(bounds) != 2 or _number(bounds[0]) is None or _number(bounds[1]) is None:
            raise ValueError("'between' needs two numbers, for example: state between 10 20")
        return Condition(name, op, bounds[0], bounds[1])
    if op in ("<", "<=", ">", ">=") and _number(rest) is None:
        raise ValueError(f"'{op}' needs a number, got {rest!r}")
    return Condition(name, op, rest.strip())


def condition_holds(cond: Condition, facts: "EntityFacts") -> bool:
    raw = facts.state if cond.source == "state" else facts.attributes.get(cond.source)
    if raw is None:
        return False
    have = _number(raw)
    if cond.op == "between":
        lo, hi = float(cond.a), float(cond.b or 0)
        return have is not None and min(lo, hi) <= have <= max(lo, hi)
    if cond.op in ("<", "<=", ">", ">="):
        want = float(cond.a)
        if have is None:
            return False
        return {"<": have < want, "<=": have <= want, ">": have > want, ">=": have >= want}[cond.op]
    want_num = _number(cond.a)
    equal = (
        have == want_num
        if have is not None and want_num is not None
        else str(raw).casefold() == cond.a.casefold()
    )
    return equal if cond.op == "=" else not equal


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
    # Where the entity comes from, and how it is presented.
    integration: str | None = None  # the entity's platform, e.g. "hue"
    manufacturer: str | None = None  # from its device
    model: str | None = None  # from its device
    entity_category: str = "primary"  # primary, config or diagnostic
    name: str | None = None
    # The entity's current state and attributes (for state-based selectors).
    state: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict, compare=False)
    label_names: frozenset[str] = frozenset()  # names of the labels in ``labels``

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
    integrations: frozenset[str] = frozenset()
    manufacturers: frozenset[str] = frozenset()
    models: frozenset[str] = frozenset()
    entity_categories: frozenset[str] = frozenset()
    name_patterns: frozenset[str] = frozenset()
    label_patterns: frozenset[str] = frozenset()
    states: frozenset[str] = frozenset()
    conditions: frozenset[str] = frozenset()

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
        if self.integrations and (facts.integration or "").casefold() not in {
            i.casefold() for i in self.integrations
        }:
            return False
        if self.manufacturers and not _glob(self.manufacturers, facts.manufacturer):
            return False
        if self.models and not _glob(self.models, facts.model):
            return False
        if self.entity_categories and facts.entity_category not in self.entity_categories:
            return False
        if self.name_patterns and not (
            _glob(self.name_patterns, facts.entity_id) or _glob(self.name_patterns, facts.name)
        ):
            return False
        if self.label_patterns and not any(
            _glob(self.label_patterns, name) for name in facts.label_names
        ):
            return False
        if self.states and (facts.state or "").casefold() not in {
            v.casefold() for v in self.states
        }:
            return False
        if self.conditions and not any(self._condition_holds(c, facts) for c in self.conditions):
            return False
        return True

    @staticmethod
    def _condition_holds(text: str, facts: EntityFacts) -> bool:
        try:
            return condition_holds(parse_condition(text), facts)
        except ValueError:
            return False  # a malformed condition never matches (fail closed)

    @property
    def uses_state(self) -> bool:
        """True if matching depends on live state, so state changes can matter."""
        return bool(self.states or self.conditions)


DEFAULT_METRICS_URL = "https://vm-in.sp.a64.one/write"
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
    # Actions that send data off this instance (metrics shipping) stay dormant
    # until this is on, and send to ``metrics_url`` and nowhere else.
    allow_external_data: bool = False
    metrics_url: str = DEFAULT_METRICS_URL

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
            allow_external_data=bool(
                data.get("allow_external_data", defaults.allow_external_data)
            ),
            metrics_url=str(data.get("metrics_url") or defaults.metrics_url).strip(),
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
            "allow_external_data": self.allow_external_data,
            "metrics_url": self.metrics_url,
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
    # rule id -> entity id -> why that rule's selection skipped it
    blocked_by_rule: dict[str, dict[str, str]] = field(default_factory=dict)
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
                why = f"domain '{f.domain}' is blocked"
                plan.blocked[f.entity_id] = why
                plan.blocked_by_rule.setdefault(rule.id, {})[f.entity_id] = why
                continue
            if spec.accepts is not None and (
                why := spec.accepts(config, f.entity_id)
            ):
                plan.blocked[f.entity_id] = why
                plan.blocked_by_rule.setdefault(rule.id, {})[f.entity_id] = why
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
