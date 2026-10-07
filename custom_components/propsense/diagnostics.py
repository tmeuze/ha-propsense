"""Diagnostics: rules, settings and the last result (no secrets involved)."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import PropSenseConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PropSenseConfigEntry
) -> dict[str, Any]:
    manager = entry.runtime_data
    return {
        "rules": [r.to_dict() for r in manager.rules],
        "settings": manager.settings.to_dict(),
        "last": manager.last.to_dict() if manager.last else None,
    }
