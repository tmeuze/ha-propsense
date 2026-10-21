"""Built-in action types."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.homeassistant.exposed_entities import (
    async_expose_entity,
    async_get_assistant_settings,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .api import ActionType
from .const import ASSISTANT_LABELS, ASSISTANTS
from .engine import EXPOSE, EXPOSE_SPEC


class ExposeAction(ActionType):
    """Expose the selected entities to voice assistants."""

    type_id = EXPOSE
    name = "Expose to voice assistants"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("assistants", default=["conversation"]): (
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=a, label=ASSISTANT_LABELS.get(a, a)
                                )
                                for a in ASSISTANTS
                            ],
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                )
            }
        )

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        return EXPOSE_SPEC.targets(config)

    def target_label(self, target: str) -> str:
        return ASSISTANT_LABELS.get(target, target)

    async def async_current(self, target: str) -> set[str]:
        return {
            entity_id
            for entity_id, options in async_get_assistant_settings(
                self._hass, target
            ).items()
            if options.get("should_expose")
        }

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        for entity_id in sorted(add):
            async_expose_entity(self._hass, target, entity_id, True)
        for entity_id in sorted(remove):
            async_expose_entity(self._hass, target, entity_id, False)
