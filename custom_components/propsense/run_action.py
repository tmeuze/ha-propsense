"""Built-in action: run Home Assistant actions when entities enter or leave a selection.

Home Assistant has no trigger for "a label was added". This one fires when an
entity *starts* matching a rule (it got the label, its battery dropped below 20,
it was moved to the garage) and when it *stops*, and runs the actions you give
for each entity. They are ordinary Home Assistant actions (services, notifications,
scripts, delays, conditions), with these variables available in templates:

* ``entity_id``: the entity that entered or left
* ``event``: ``enter`` or ``leave``
* ``name``: the entity's name

The first time PropSense sees a rule it only records what is selected and fires
nothing, so adding a rule never fires for entities that already match. At most
``max_per_run`` entities fire per evaluation (default 20), and a restart does not
re-fire: the last selection is stored. Locks, alarm panels and cameras are blocked
by default like every action.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.script import Script

from .api import ActionType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

RUN = "run"
DEFAULT_MAX = 20


def _sequence(config: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return list(config.get(key) or [])


class RunActionsAction(ActionType):
    type_id = RUN
    name = "Run actions when an entity enters or leaves"
    mode = "edge"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._scripts: dict[tuple[str, str], Script] = {}

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional("on_enter"): selector.ActionSelector(),
                vol.Optional("on_leave"): selector.ActionSelector(),
                vol.Optional("max_per_run", default=DEFAULT_MAX): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=200, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

    def validate(self, config: dict[str, Any]) -> None:
        enter, leave = _sequence(config, "on_enter"), _sequence(config, "on_leave")
        if not enter and not leave:
            raise vol.Invalid("Add at least one action for entering or for leaving")
        for key in ("on_enter", "on_leave"):
            try:
                cv.SCRIPT_SCHEMA(_sequence(config, key))
            except vol.Invalid as err:
                raise vol.Invalid(f"{key}: {err}") from err

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        cfg = {
            "on_enter": _sequence(config, "on_enter"),
            "on_leave": _sequence(config, "on_leave"),
            "max": int(config.get("max_per_run") or DEFAULT_MAX),
        }
        return frozenset({json.dumps(cfg, sort_keys=True)})

    def target_label(self, target: str) -> str:
        try:
            cfg = json.loads(target)
        except ValueError:
            return target
        parts = []
        if cfg["on_enter"]:
            parts.append(f"{len(cfg['on_enter'])} step(s) on enter")
        if cfg["on_leave"]:
            parts.append(f"{len(cfg['on_leave'])} step(s) on leave")
        return "Run " + " and ".join(parts)

    def _script(self, target: str, key: str, sequence: list[dict[str, Any]]) -> Script:
        cached = self._scripts.get((target, key))
        if cached is None:
            cached = self._scripts[(target, key)] = Script(
                self._hass, cv.SCRIPT_SCHEMA(sequence), f"PropSense {key}", DOMAIN
            )
        return cached

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        cfg = json.loads(target)
        for key, entities, event in (
            ("on_enter", sorted(add), "enter"),
            ("on_leave", sorted(remove), "leave"),
        ):
            if not cfg[key] or not entities:
                continue
            if len(entities) > cfg["max"]:
                _LOGGER.warning(
                    "PropSense ran %s for %d of %d entities (limit %d); the rest were skipped",
                    key, cfg["max"], len(entities), cfg["max"],
                )
                entities = entities[: cfg["max"]]
            script = self._script(target, key, cfg[key])
            for entity_id in entities:
                state = self._hass.states.get(entity_id)
                try:
                    await script.async_run(
                        {
                            "entity_id": entity_id,
                            "event": event,
                            "name": state.name if state else entity_id,
                        },
                        Context(),
                    )
                except Exception:  # one failing run must not stop the others
                    _LOGGER.exception("PropSense %s failed for %s", key, entity_id)
