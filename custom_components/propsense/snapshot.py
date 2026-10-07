"""Turn Home Assistant's registries into the engine's plain facts.

This is the only place that knows how labels, areas, floors, devices and
groups relate in Home Assistant. Rules:

* An entity's labels are its own, plus its device's (setting), plus its
  area's (setting, off by default).
* Its area is its own, falling back to its device's area.
* Its floor comes from that area.
* Group membership is read from a group entity's ``entity_id`` attribute
  (``group.*`` and the light, switch, fan and cover groups all expose it),
  expanded through nested groups.
* Disabled entities are skipped. Entities that exist only in the state
  machine (no registry entry) are included with whatever their state says.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

from .engine import EntityFacts, Settings

_MAX_GROUP_DEPTH = 5


def expand_group(hass: HomeAssistant, group_id: str, _depth: int = 0) -> set[str]:
    """All entity ids inside a group, following nested groups."""
    if _depth > _MAX_GROUP_DEPTH:
        return set()
    state = hass.states.get(group_id)
    if state is None:
        return set()
    members = state.attributes.get("entity_id") or []
    if isinstance(members, str):
        members = [members]
    out: set[str] = set()
    for member in members:
        out.add(member)
        out |= expand_group(hass, member, _depth + 1)
    return out


def build_facts(
    hass: HomeAssistant, settings: Settings, group_ids: set[str]
) -> list[EntityFacts]:
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    area_reg = ar.async_get(hass)

    membership: dict[str, set[str]] = {}
    for gid in group_ids:
        for member in expand_group(hass, gid):
            membership.setdefault(member, set()).add(gid)

    facts: list[EntityFacts] = []
    seen: set[str] = set()

    for entry in ent_reg.entities.values():
        if entry.disabled_by is not None:
            continue
        seen.add(entry.entity_id)

        device = dev_reg.async_get(entry.device_id) if entry.device_id else None
        labels = set(entry.labels)
        if settings.inherit_device_labels and device is not None:
            labels |= set(device.labels)

        area_id = entry.area_id or (device.area_id if device is not None else None)
        floor_id = None
        if area_id:
            area = area_reg.async_get_area(area_id)
            if area is not None:
                floor_id = area.floor_id
                if settings.inherit_area_labels:
                    labels |= set(area.labels)

        facts.append(
            EntityFacts(
                entity_id=entry.entity_id,
                labels=frozenset(labels),
                area_id=area_id,
                floor_id=floor_id,
                device_id=entry.device_id,
                device_class=entry.device_class or entry.original_device_class,
                groups=frozenset(membership.get(entry.entity_id, ())),
            )
        )

    for state in hass.states.async_all():
        if state.entity_id in seen:
            continue
        facts.append(
            EntityFacts(
                entity_id=state.entity_id,
                device_class=state.attributes.get("device_class"),
                groups=frozenset(membership.get(state.entity_id, ())),
            )
        )
    return facts
