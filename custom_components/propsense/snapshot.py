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
* Integration is the entity's platform; manufacturer and model come from its
  device; the category is Home Assistant's entity category (``primary`` when
  it has none); the name is what the entity is called in the UI. Label names
  (for wildcard matching) come from the label registry.
* State and attributes are the entity's current ones, for the ``states`` and
  ``conditions`` selector fields.
* Capabilities are tags read from the state of lights, covers, fans and
  climate entities (see ``capabilities_of``). Entities without a state, or of
  other domains, have none.
* Disabled entities are skipped. Entities that exist only in the state
  machine (no registry entry) are included with whatever their state says.
"""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.cover import CoverEntityFeature
from homeassistant.components.fan import FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    label_registry as lr,
)

from .engine import EntityFacts, Settings

_MAX_GROUP_DEPTH = 5

_COLOR_MODES = {"hs", "xy", "rgb", "rgbw", "rgbww"}
_WHITE_MODES = {"white", "rgbw", "rgbww"}
_HVAC_TAGS = ("heat", "cool", "heat_cool", "auto", "dry", "fan_only")

# Domains whose entities report capabilities (see ``capabilities_of``).
CAPABILITY_DOMAINS = ("light", "cover", "fan", "climate")


def _features(state) -> int:
    try:
        return int(state.attributes.get("supported_features") or 0)
    except (TypeError, ValueError):
        return 0


def capabilities_of(hass: HomeAssistant, entity_id: str) -> frozenset[str]:
    """What an entity can do, as plain tags, from what its state reports.

    * light: onoff, brightness, color_temp, color, white (supported color modes)
    * cover: position, tilt (supported features)
    * fan: speed, oscillate, direction, preset (supported features)
    * climate: heat, cool, heat_cool, auto, dry, fan_only (HVAC modes) and
      target_temp (can set a target temperature)
    """
    domain = entity_id.split(".", 1)[0]
    if domain not in CAPABILITY_DOMAINS:
        return frozenset()
    state = hass.states.get(entity_id)
    if state is None:
        return frozenset()

    tags: set[str] = set()
    if domain == "light":
        modes = set(state.attributes.get("supported_color_modes") or [])
        if not modes:
            return frozenset()
        if modes == {"onoff"}:
            return frozenset({"onoff"})
        tags.add("brightness")
        if "color_temp" in modes:
            tags.add("color_temp")
        if modes & _COLOR_MODES:
            tags.add("color")
        if modes & _WHITE_MODES:
            tags.add("white")
    elif domain == "cover":
        features = _features(state)
        if features & CoverEntityFeature.SET_POSITION:
            tags.add("position")
        if features & CoverEntityFeature.SET_TILT_POSITION:
            tags.add("tilt")
    elif domain == "fan":
        features = _features(state)
        for flag, tag in (
            (FanEntityFeature.SET_SPEED, "speed"),
            (FanEntityFeature.OSCILLATE, "oscillate"),
            (FanEntityFeature.DIRECTION, "direction"),
            (FanEntityFeature.PRESET_MODE, "preset"),
        ):
            if features & flag:
                tags.add(tag)
    else:  # climate
        modes = {str(m) for m in state.attributes.get("hvac_modes") or []}
        tags |= {m for m in _HVAC_TAGS if m in modes}
        if _features(state) & (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        ):
            tags.add("target_temp")
    return frozenset(tags)


def _live(hass: HomeAssistant, entity_id: str) -> dict:
    state = hass.states.get(entity_id)
    if state is None:
        return {}
    return {"state": state.state, "attributes": state.attributes}


def _display_name(hass: HomeAssistant, entry: er.RegistryEntry) -> str | None:
    state = hass.states.get(entry.entity_id)
    if state is not None:
        return state.name
    return entry.name or entry.original_name


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
    hass: HomeAssistant,
    settings: Settings,
    group_ids: set[str],
    only: set[str] | None = None,
) -> list[EntityFacts]:
    """Facts for every entity, or just those in ``only`` (a quick single-entity check)."""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    area_reg = ar.async_get(hass)
    label_reg = lr.async_get(hass)

    def label_names(ids: set[str]) -> frozenset[str]:
        return frozenset(
            label.name for lid in ids if (label := label_reg.async_get_label(lid))
        )

    membership: dict[str, set[str]] = {}
    for gid in group_ids:
        for member in expand_group(hass, gid):
            membership.setdefault(member, set()).add(gid)

    facts: list[EntityFacts] = []
    seen: set[str] = set()

    entries = (
        [e for eid in only if (e := ent_reg.async_get(eid)) is not None]
        if only is not None
        else ent_reg.entities.values()
    )
    for entry in entries:
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
                capabilities=capabilities_of(hass, entry.entity_id),
                integration=entry.platform,
                manufacturer=device.manufacturer if device is not None else None,
                model=device.model if device is not None else None,
                entity_category=(
                    entry.entity_category.value if entry.entity_category else "primary"
                ),
                name=_display_name(hass, entry),
                label_names=label_names(labels),
                **_live(hass, entry.entity_id),
            )
        )

    for state in (
        [s for eid in only if (s := hass.states.get(eid)) is not None]
        if only is not None
        else hass.states.async_all()
    ):
        if state.entity_id in seen:
            continue
        facts.append(
            EntityFacts(
                entity_id=state.entity_id,
                device_class=state.attributes.get("device_class"),
                groups=frozenset(membership.get(state.entity_id, ())),
                capabilities=capabilities_of(hass, state.entity_id),
                name=state.name,
                state=state.state,
                attributes=state.attributes,
            )
        )
    return facts
