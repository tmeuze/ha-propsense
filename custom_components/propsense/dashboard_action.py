"""Built-in action: show the selected entities on a dashboard.

Rules decide which entities appear in a named section of a named dashboard.
Nothing is written to Home Assistant's dashboard storage: a live dashboard
strategy (``propsense-strategy.js``) asks :meth:`DashboardAction.resolve` for the
current sections every time the dashboard loads, so the dashboard can never drift
from the rules.

An *audience* limits who is shown a section: ``everyone`` (the default),
``admins``, ``non-admins``, or specific user ids. This is a presentation filter,
not a security boundary: every logged-in user can still read every state through
the API.
"""
from __future__ import annotations

import json
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    floor_registry as fr,
    selector,
)

from .api import ActionType

DASHBOARD = "dashboard"
GROUP_BY = ("area", "floor", "domain", "none")
AUDIENCE_KEYWORDS = ("everyone", "admins", "non-admins")
NO_AREA = "No area"
NO_FLOOR = "No floor"


def _slug(value: Any) -> str:
    out = "".join(c if c.isalnum() else "-" for c in str(value or "").strip().lower())
    return "-".join(p for p in out.split("-") if p)


def audience_matches(audience: list[str], user_id: str | None, is_admin: bool) -> bool:
    """Whether a section with this audience is shown to this user."""
    if not audience or "everyone" in audience:
        return True
    if "admins" in audience and is_admin:
        return True
    if "non-admins" in audience and not is_admin:
        return True
    return user_id is not None and user_id in audience


class DashboardAction(ActionType):
    type_id = DASHBOARD
    name = "Show on a dashboard"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._members: dict[str, set[str]] = {}

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("dashboard"): selector.TextSelector(),
                vol.Required("title"): selector.TextSelector(),
                vol.Optional("group_by", default="area"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=list(GROUP_BY))
                ),
                vol.Optional("audience", default=["everyone"]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(AUDIENCE_KEYWORDS),
                        multiple=True,
                        custom_value=True,
                    )
                ),
            }
        )

    @staticmethod
    def _normalise(config: dict[str, Any]) -> dict[str, Any] | None:
        dashboard = _slug(config.get("dashboard"))
        title = str(config.get("title") or "").strip()
        if not dashboard or not title:
            return None
        group_by = config.get("group_by") or "area"
        audience = sorted({str(a).strip() for a in (config.get("audience") or []) if str(a).strip()})
        return {
            "dashboard": dashboard,
            "title": title,
            "group_by": group_by if group_by in GROUP_BY else "area",
            "audience": audience or ["everyone"],
        }

    def validate(self, config: dict[str, Any]) -> None:
        if not _slug(config.get("dashboard")):
            raise vol.Invalid("Give the dashboard a name")
        if not str(config.get("title") or "").strip():
            raise vol.Invalid("Give the section a title")
        if config.get("group_by") not in (None, *GROUP_BY):
            raise vol.Invalid("Group by must be area, floor, domain or none")

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        cfg = self._normalise(config)
        return frozenset({json.dumps(cfg, sort_keys=True)}) if cfg else frozenset()

    def target_label(self, target: str) -> str:
        try:
            cfg = json.loads(target)
            return f"dashboard “{cfg['dashboard']}” › {cfg['title']}"
        except (ValueError, KeyError):
            return target

    def size_limit(self, target: str, settings: Any) -> int:
        return 0  # a dashboard can list as many entities as the rule selects

    async def async_stop(self) -> None:
        self._members.clear()

    async def async_current(self, target: str) -> set[str]:
        return set(self._members.get(target, set()))

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        members = self._members.setdefault(target, set())
        members |= add
        members -= remove
        if not members:
            self._members.pop(target, None)

    def status(self) -> dict[str, Any]:
        return {
            "sections": len(self._members),
            "entities": sum(len(m) for m in self._members.values()),
        }

    # ---- read side, used by the websocket command and the dashboard strategy

    def dashboards(self) -> list[str]:
        return sorted({json.loads(t)["dashboard"] for t in self._members})

    @callback
    def resolve(self, dashboard: str, user_id: str | None, is_admin: bool) -> list[dict[str, Any]]:
        """Sections of ``dashboard`` this user may see, each with its entities grouped."""
        wanted = _slug(dashboard)
        sections = []
        for target in sorted(self._members):
            cfg = json.loads(target)
            if cfg["dashboard"] != wanted:
                continue
            if not audience_matches(cfg["audience"], user_id, is_admin):
                continue
            entities = sorted(self._members[target])
            sections.append(
                {
                    "title": cfg["title"],
                    "group_by": cfg["group_by"],
                    "groups": self._group(entities, cfg["group_by"]),
                }
            )
        sections.sort(key=lambda s: s["title"].lower())
        return sections

    def _group(self, entity_ids: list[str], group_by: str) -> list[dict[str, Any]]:
        if group_by == "none":
            return [{"name": "", "entities": entity_ids}]
        ent_reg = er.async_get(self._hass)
        dev_reg = dr.async_get(self._hass)
        areas = ar.async_get(self._hass)
        floors = fr.async_get(self._hass)

        def area_of(entity_id: str):
            entry = ent_reg.async_get(entity_id)
            if entry is None:
                return None
            area_id = entry.area_id
            if area_id is None and entry.device_id:
                device = dev_reg.async_get(entry.device_id)
                area_id = device.area_id if device else None
            return areas.async_get_area(area_id) if area_id else None

        buckets: dict[str, list[str]] = {}
        for entity_id in entity_ids:
            if group_by == "domain":
                key = entity_id.split(".", 1)[0].replace("_", " ").title()
            elif group_by == "floor":
                area = area_of(entity_id)
                floor = floors.async_get_floor(area.floor_id) if area and area.floor_id else None
                key = floor.name if floor else NO_FLOOR
            else:
                area = area_of(entity_id)
                key = area.name if area else NO_AREA
            buckets.setdefault(key, []).append(entity_id)
        fallback = (NO_AREA, NO_FLOOR)
        ordered = sorted(buckets, key=lambda k: (k in fallback, k.lower()))
        return [{"name": k, "entities": buckets[k]} for k in ordered]
