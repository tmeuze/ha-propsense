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
from typing import Any, Iterable

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
        return True


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    enabled: bool = True
    include: Selector = field(default_factory=Selector)
    exclude: Selector = field(default_factory=Selector)
    # Action: expose matching entities to these assistants (for example
    # "conversation", "cloud.alexa", "cloud.google_assistant").
    assistants: frozenset[str] = frozenset({"conversation"})

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            enabled=bool(data.get("enabled", True)),
            include=Selector.from_dict(data.get("include")),
            exclude=Selector.from_dict(data.get("exclude")),
            assistants=_fset(data.get("assistants")) or frozenset({"conversation"}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "include": self.include.to_dict(),
            "exclude": self.exclude.to_dict(),
            "assistants": sorted(self.assistants),
        }

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
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "managed_assistants": sorted(self.managed_assistants),
            "blocked_domains": sorted(self.blocked_domains),
            "max_exposed": self.max_exposed,
            "inherit_device_labels": self.inherit_device_labels,
            "inherit_area_labels": self.inherit_area_labels,
            "dry_run": self.dry_run,
        }


@dataclass
class Plan:
    """What the rules want, before anything is applied."""

    # assistant -> entity ids that should be exposed
    desired: dict[str, set[str]] = field(default_factory=dict)
    # rule id -> entity ids it selected (after excludes and the block list)
    by_rule: dict[str, set[str]] = field(default_factory=dict)
    # entity id -> why a selected entity was dropped
    blocked: dict[str, str] = field(default_factory=dict)
    # assistants PropSense manages (rule targets plus the setting)
    managed: set[str] = field(default_factory=set)


def evaluate(
    rules: Iterable[Rule], facts: Iterable[EntityFacts], settings: Settings
) -> Plan:
    """Compute what should be exposed. Pure: same inputs, same plan."""
    rules = [r for r in rules if r.enabled]
    facts = list(facts)

    plan = Plan(managed=set(settings.managed_assistants))
    for rule in rules:
        plan.managed |= set(rule.assistants)
        plan.by_rule[rule.id] = set()

    for assistant in plan.managed:
        plan.desired[assistant] = set()

    for f in facts:
        for rule in rules:
            if not rule.selects(f):
                continue
            if f.domain in settings.blocked_domains:
                plan.blocked[f.entity_id] = f"domain '{f.domain}' is blocked"
                continue
            plan.by_rule[rule.id].add(f.entity_id)
            for assistant in rule.assistants:
                plan.desired[assistant].add(f.entity_id)
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
