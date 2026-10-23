"""Built-in action: keep a group helper's members equal to a rule's selection.

Targets are Home Assistant group helpers (the "Group" helper in the UI: light,
switch, fan, cover, media player and valve groups). A rule either names an
existing group, or asks PropSense to create one. Both are labelled
``[PropSense]`` so you can see which groups the rules own.

The rules are the single source of truth: members someone added by hand are
removed on the next apply.
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    entity_registry as er,
    label_registry as lr,
    selector,
)

from .api import ActionType

_LOGGER = logging.getLogger(__name__)

GROUP = "group"
GROUP_DOMAIN = "group"
LABEL_NAME = "[PropSense]"
# Group types whose helper only needs a name and members. Others (sensor,
# binary_sensor) need extra options and are out of scope for now.
GROUP_TYPES = ["light", "switch", "fan", "cover", "media_player", "valve"]
_NEW = "new:"


def _target_for(config: dict[str, Any]) -> str | None:
    if config.get("group"):
        return str(config["group"])
    if config.get("create_name"):
        gtype = config.get("group_type") or "light"
        return f"{_NEW}{gtype}:{str(config['create_name']).strip()}"
    return None


class GroupMembersAction(ActionType):
    type_id = GROUP
    name = "Keep a group's members in sync"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    # ------------------------------------------------------------- schema

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional("group"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        integration=GROUP_DOMAIN, domain=GROUP_TYPES
                    )
                ),
                vol.Optional("create_name"): selector.TextSelector(),
                vol.Optional("group_type", default="light"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=GROUP_TYPES, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
            }
        )

    def validate(self, config: dict[str, Any]) -> None:
        has_group = bool(config.get("group"))
        has_name = bool((config.get("create_name") or "").strip())
        if has_group == has_name:
            raise vol.Invalid(
                "Choose an existing group, or give a name to create a new one (not both)"
            )
        if has_group:
            entry = self._entry_for_entity(config["group"])
            if entry is None:
                raise vol.Invalid(
                    f"{config['group']} is not a group helper PropSense can edit"
                )

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        target = _target_for(config)
        return frozenset({target}) if target else frozenset()

    def target_label(self, target: str) -> str:
        if target.startswith(_NEW):
            gtype, _, name = target[len(_NEW) :].partition(":")
            return f"new {gtype} group “{name}”"
        return target

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        gtype = self._type_for(_target_for(config))
        domain = entity_id.split(".", 1)[0]
        if gtype and domain != gtype:
            return f"can't join a {gtype} group (domain '{domain}')"
        if entity_id == config.get("group"):
            return "a group can't contain itself"
        entry = er.async_get(self._hass).async_get(entity_id)
        if entry is not None and entry.platform == GROUP_DOMAIN:
            return "group helpers can't be members of PropSense-managed groups"
        return None

    # ------------------------------------------------------------ lookups

    def _type_for(self, target: str | None) -> str | None:
        if target is None:
            return None
        if target.startswith(_NEW):
            return target[len(_NEW) :].partition(":")[0]
        entry = self._entry_for_entity(target)
        return entry.options.get("group_type") if entry else target.split(".", 1)[0]

    def _entry_for_entity(self, entity_id: str) -> ConfigEntry | None:
        reg_entry = er.async_get(self._hass).async_get(entity_id)
        if reg_entry is None or reg_entry.platform != GROUP_DOMAIN:
            return None
        if reg_entry.config_entry_id is None:
            return None
        return self._hass.config_entries.async_get_entry(reg_entry.config_entry_id)

    def _entry_for_target(self, target: str) -> ConfigEntry | None:
        if not target.startswith(_NEW):
            return self._entry_for_entity(target)
        gtype, _, name = target[len(_NEW) :].partition(":")
        for entry in self._hass.config_entries.async_entries(GROUP_DOMAIN):
            if entry.title == name and entry.options.get("group_type") == gtype:
                return entry
        return None

    def _members(self, entry: ConfigEntry) -> list[str]:
        """Member entity ids (the option can hold registry ids)."""
        registry = er.async_get(self._hass)
        out = []
        for member in entry.options.get("entities", []):
            resolved = er.async_resolve_entity_id(registry, member)
            out.append(resolved or member)
        return out

    # ----------------------------------------------------------- reconcile

    async def async_current(self, target: str) -> set[str]:
        entry = self._entry_for_target(target)
        return set(self._members(entry)) if entry else set()

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        entry = self._entry_for_target(target)
        if entry is None:
            if add:
                await self._create(target, sorted(add))
            return
        members = [m for m in self._members(entry) if m not in remove]
        members += [m for m in sorted(add) if m not in members]
        if members == self._members(entry):
            return
        self._hass.config_entries.async_update_entry(
            entry, options={**entry.options, "entities": members}
        )
        # Group helpers only re-read their members when they reload.
        self._hass.config_entries.async_schedule_reload(entry.entry_id)

    async def _create(self, target: str, members: list[str]) -> None:
        gtype, _, name = target[len(_NEW) :].partition(":")
        flow = self._hass.config_entries.flow
        result = await flow.async_init(GROUP_DOMAIN, context={"source": "user"})
        result = await flow.async_configure(result["flow_id"], {"next_step_id": gtype})
        result = await flow.async_configure(
            result["flow_id"],
            {"name": name, "entities": members, "hide_members": False},
        )
        if result.get("type") != "create_entry":
            raise RuntimeError(f"could not create the {gtype} group {name!r}: {result}")
        _LOGGER.info("PropSense created the %s group %r with %d members", gtype, name, len(members))

    async def async_sync(self, target: str) -> None:
        """Keep the ``[PropSense]`` label on the group, once its entity exists."""
        entry = self._entry_for_target(target)
        if entry is None:
            return
        registry = er.async_get(self._hass)
        entity_id = registry.async_get_entity_id(
            entry.options.get("group_type", ""), GROUP_DOMAIN, entry.entry_id
        )
        if entity_id is None:  # not registered yet; the registry event re-runs us
            return
        entity = registry.async_get(entity_id)
        labels = lr.async_get(self._hass)
        label = labels.async_get_label_by_name(LABEL_NAME) or labels.async_create(
            LABEL_NAME
        )
        if label.label_id not in entity.labels:
            registry.async_update_entity(
                entity_id, labels=entity.labels | {label.label_id}
            )
