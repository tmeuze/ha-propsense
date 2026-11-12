"""Built-in action: flag the selected entities in Home Assistant's Repairs.

A hygiene check: write a rule that selects what *should not* exist (lights with
no label, sensors from an integration you retired, entities nobody named) and
PropSense lists them in a Repairs issue with your title. The issue disappears when
nothing matches. It changes no entity.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir, selector

from .api import ActionType
from .const import DOMAIN

FLAG = "flag"
SHOWN = 15


class FlagAction(ActionType):
    type_id = FLAG
    name = "Flag in Repairs"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._members: dict[str, set[str]] = {}

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("title"): selector.TextSelector(),
                vol.Optional("message"): selector.TextSelector(
                    selector.TextSelectorConfig(multiline=True)
                ),
            }
        )

    def validate(self, config: dict[str, Any]) -> None:
        if not str(config.get("title") or "").strip():
            raise vol.Invalid("Give the check a title")

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        cfg = {"title": str(config.get("title") or "").strip(),
               "message": str(config.get("message") or "").strip()}
        return frozenset({json.dumps(cfg, sort_keys=True)}) if cfg["title"] else frozenset()

    def target_label(self, target: str) -> str:
        try:
            return f"flag “{json.loads(target)['title']}”"
        except (ValueError, KeyError):
            return target

    def size_limit(self, target: str, settings: Any) -> int:
        return 0

    @staticmethod
    def _issue_id(target: str) -> str:
        return "flagged_" + hashlib.sha256(target.encode()).hexdigest()[:12]

    async def async_stop(self) -> None:
        for target in list(self._members):
            ir.async_delete_issue(self._hass, DOMAIN, self._issue_id(target))
        self._members.clear()

    async def async_current(self, target: str) -> set[str]:
        return set(self._members.get(target, set()))

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        members = self._members.setdefault(target, set())
        members |= add
        members -= remove
        issue_id = self._issue_id(target)
        if not members:
            self._members.pop(target, None)
            ir.async_delete_issue(self._hass, DOMAIN, issue_id)
            return
        cfg = json.loads(target)
        listed = sorted(members)
        more = f" and {len(listed) - SHOWN} more" if len(listed) > SHOWN else ""
        ir.async_create_issue(
            self._hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="flagged",
            translation_placeholders={
                "title": cfg["title"],
                "count": str(len(listed)),
                "entities": ", ".join(listed[:SHOWN]) + more,
                "message": cfg["message"] or "Nothing to fix automatically.",
            },
        )
