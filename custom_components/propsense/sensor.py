"""Status sensors: how many entities each managed assistant can see."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PropSenseConfigEntry
from .const import ASSISTANT_LABELS, DOMAIN, SIGNAL_UPDATED
from .engine import estimated_tokens
from .manager import ExposureManager

_MAX_LISTED = 300


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PropSenseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    manager = entry.runtime_data
    plan, _rules, _settings = manager.compute_plan()
    async_add_entities(
        ExposedCountSensor(entry, manager, assistant)
        for assistant in sorted(plan.managed)
    )


class ExposedCountSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:microphone-message"
    _attr_native_unit_of_measurement = "entities"

    def __init__(
        self, entry: PropSenseConfigEntry, manager: ExposureManager, assistant: str
    ) -> None:
        self._manager = manager
        self._assistant = assistant
        label = ASSISTANT_LABELS.get(assistant, assistant)
        self._attr_unique_id = f"{entry.entry_id}_{assistant}"
        self._attr_name = f"Exposed to {label}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="PropSense",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATED, self._refresh)
        )

    @callback
    def _refresh(self) -> None:
        self.async_write_ha_state()

    @property
    def _result(self):
        last = self._manager.last
        return last.assistants.get(self._assistant) if last else None

    @property
    def native_value(self) -> int | None:
        result = self._result
        return len(result.exposed) if result else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self._manager.last
        result = self._result
        if last is None or result is None:
            return {}
        return {
            "estimated_tokens": estimated_tokens(len(result.exposed)),
            "refused": result.refused,
            "wanted": len(result.desired),
            "rules": {
                last.rule_names.get(rid, rid): count
                for rid, count in last.by_rule.items()
            },
            "blocked": last.blocked,
            "last_applied": last.at.isoformat(),
            "entities": result.exposed[:_MAX_LISTED],
        }
