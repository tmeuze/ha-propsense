"""Built-in action: apply a label to the entities a rule selects.

Labels become an output of rules instead of something to maintain by hand: every
battery sensor gets ``Needs battery``, everything in the garage gets ``Outdoor``.
The rules are the single source of truth for that label: it is added to selected
entities and removed from entities that are no longer selected, including ones
someone labelled by hand. The label is created if it does not exist.

Only the entity's own labels are changed (not labels it inherits from its device
or area). Entities without a registry entry cannot carry labels and are skipped.
Because other rules can select on the label, one rule can feed another.
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, label_registry as lr, selector

from .api import ActionType

LABEL = "label"


class ApplyLabelAction(ActionType):
    type_id = LABEL
    name = "Apply a label"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def config_schema(self) -> vol.Schema:
        return vol.Schema({vol.Required("name"): selector.TextSelector()})

    def validate(self, config: dict[str, Any]) -> None:
        if not str(config.get("name") or "").strip():
            raise vol.Invalid("Give the label a name")

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        name = str(config.get("name") or "").strip()
        return frozenset({name}) if name else frozenset()

    def target_label(self, target: str) -> str:
        return f"label “{target}”"

    def size_limit(self, target: str, settings: Any) -> int:
        return 0  # labels are cheap to undo; no cap

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        if er.async_get(self._hass).async_get(entity_id) is None:
            return "has no registry entry, so it cannot carry labels"
        return None

    async def async_current(self, target: str) -> set[str]:
        label = lr.async_get(self._hass).async_get_label_by_name(target)
        if label is None:
            return set()
        return {
            e.entity_id
            for e in er.async_get(self._hass).entities.values()
            if label.label_id in e.labels
        }

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        labels = lr.async_get(self._hass)
        label = labels.async_get_label_by_name(target)
        if label is None:
            if not add:
                return
            label = labels.async_create(target)
        registry = er.async_get(self._hass)
        for entity_id in sorted(add):
            if (entry := registry.async_get(entity_id)) is not None:
                registry.async_update_entity(entity_id, labels=set(entry.labels) | {label.label_id})
        for entity_id in sorted(remove):
            if (entry := registry.async_get(entity_id)) is not None:
                registry.async_update_entity(entity_id, labels=set(entry.labels) - {label.label_id})
