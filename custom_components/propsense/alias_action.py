"""Built-in action: give the selected entities a voice alias.

Voice assistants (Assist, Alexa, Google) match what you say against an entity's
name and its aliases. This keeps an alias on exactly the entities a rule selects:
added to selected entities, removed from ones no longer selected, including ones
that had it added by hand. Other aliases on an entity are never touched.
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, selector

from .api import ActionType

ALIASES = "aliases"


class AliasAction(ActionType):
    type_id = ALIASES
    name = "Give a voice alias"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("aliases"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=[], multiple=True, custom_value=True)
                )
            }
        )

    @staticmethod
    def _names(config: dict[str, Any]) -> list[str]:
        return [a.strip() for a in config.get("aliases") or [] if str(a).strip()]

    def validate(self, config: dict[str, Any]) -> None:
        if not self._names(config):
            raise vol.Invalid("Give at least one alias")

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        return frozenset(self._names(config))

    def target_label(self, target: str) -> str:
        return f"alias “{target}”"

    def size_limit(self, target: str, settings: Any) -> int:
        return 0

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        if er.async_get(self._hass).async_get(entity_id) is None:
            return "has no registry entry, so it cannot have aliases"
        return None

    async def async_current(self, target: str) -> set[str]:
        return {
            e.entity_id
            for e in er.async_get(self._hass).entities.values()
            if target in e.aliases
        }

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        registry = er.async_get(self._hass)
        for entity_id in sorted(add):
            if (entry := registry.async_get(entity_id)) is not None:
                registry.async_update_entity(entity_id, aliases=set(entry.aliases) | {target})
        for entity_id in sorted(remove):
            if (entry := registry.async_get(entity_id)) is not None:
                registry.async_update_entity(entity_id, aliases=set(entry.aliases) - {target})
