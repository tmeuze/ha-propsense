"""Websocket commands used by the PropSense panel (admin only)."""
from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol

try:  # Home Assistant 2026.10 replaced voluptuous with probatio
    import probatio

    _to_fields = probatio.to_field_list
except ImportError:  # 2026.9 and earlier
    import voluptuous_serialize

    _to_fields = voluptuous_serialize.convert

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .api import async_get_registry
from .const import ASSISTANT_LABELS, ASSISTANTS, DOMAIN
from .engine import SELECTOR_FIELDS, Settings

_SELECTOR = vol.Schema({vol.Optional(f): [str] for f in SELECTOR_FIELDS})
_RULE = vol.Schema(
    {
        vol.Optional("id"): str,
        vol.Required("name"): vol.All(str, vol.Length(min=1)),
        vol.Optional("enabled", default=True): bool,
        vol.Optional("include", default=dict): _SELECTOR,
        vol.Optional("exclude", default=dict): _SELECTOR,
        vol.Required("actions"): [
            {
                vol.Required("type"): str,
                vol.Optional("config", default=dict): dict,
            }
        ],
    }
)
_SETTINGS = vol.Schema(
    {
        vol.Optional("managed_assistants"): vol.All([vol.In(ASSISTANTS)], vol.Length(min=1)),
        vol.Optional("blocked_domains"): [str],
        vol.Optional("max_exposed"): vol.All(int, vol.Range(min=0)),
        vol.Optional("inherit_device_labels"): bool,
        vol.Optional("inherit_area_labels"): bool,
        vol.Optional("dry_run"): bool,
        vol.Optional("allow_third_party_actions"): bool,
    }
)


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    for command in (
        ws_overview,
        ws_save_rule,
        ws_delete_rule,
        ws_update_settings,
        ws_preview,
        ws_explain,
        ws_apply,
    ):
        websocket_api.async_register_command(hass, command)


def _manager(hass: HomeAssistant, connection, msg) -> Any | None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        connection.send_error(msg["id"], "not_loaded", "PropSense is not set up")
        return None
    return entries[0].runtime_data


def _action_types(manager) -> list[dict[str, Any]]:
    allowed = manager.settings.allow_third_party_actions
    out = []
    for type_id, action in sorted(manager.registry.types.items()):
        builtin = manager.registry.is_builtin(type_id)
        out.append(
            {
                "type": type_id,
                "name": action.name or type_id,
                "mode": action.mode,
                "builtin": builtin,
                "available": builtin or allowed,
                "schema": _to_fields(
                    action.config_schema(), custom_serializer=cv.custom_serializer
                ),
            }
        )
    return out


def _validate_rule(manager, raw: dict[str, Any]) -> dict[str, Any]:
    rule = _RULE(raw)
    for action in rule["actions"]:
        provider = manager.registry.get(action["type"])
        if provider is not None:
            action["config"] = dict(provider.config_schema()(action["config"]))
            provider.validate(action["config"])
    return rule


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "propsense/overview"})
@websocket_api.async_response
async def ws_overview(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    connection.send_result(
        msg["id"],
        {
            "rules": manager.rules_raw,
            "settings": manager.settings.to_dict(),
            "actions": _action_types(manager),
            "assistants": [
                {"value": a, "label": ASSISTANT_LABELS.get(a, a)} for a in ASSISTANTS
            ],
            "last": manager.last.to_dict() if manager.last else None,
            "runtime": {
                type_id: status
                for type_id, action in manager.registry.types.items()
                if manager.registry.is_builtin(type_id) and (status := action.status())
            },
            "defaults": Settings().to_dict(),
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/rule/save", vol.Required("rule"): dict}
)
@websocket_api.async_response
async def ws_save_rule(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    try:
        rule = _validate_rule(manager, msg["rule"])
    except vol.Invalid as err:
        connection.send_error(msg["id"], "invalid_format", str(err))
        return
    rules = manager.rules_raw
    if "id" in rule and any(r["id"] == rule["id"] for r in rules):
        rules = [rule if r["id"] == rule["id"] else r for r in rules]
    else:
        rule.setdefault("id", uuid.uuid4().hex[:8])
        rules.append(rule)
    await manager.async_set_rules(rules)
    connection.send_result(msg["id"], {"rule": rule})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/rule/delete", vol.Required("rule_id"): str}
)
@websocket_api.async_response
async def ws_delete_rule(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    await manager.async_set_rules(
        [r for r in manager.rules_raw if r["id"] != msg["rule_id"]]
    )
    connection.send_result(msg["id"], {})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/settings/update", vol.Required("settings"): dict}
)
@websocket_api.async_response
async def ws_update_settings(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    try:
        settings = _SETTINGS(msg["settings"])
    except vol.Invalid as err:
        connection.send_error(msg["id"], "invalid_format", str(err))
        return
    await manager.async_set_settings(settings)
    connection.send_result(msg["id"], {})


def _name(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    return state.name if state else entity_id


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/preview", vol.Optional("rule"): dict}
)
@websocket_api.async_response
async def ws_preview(hass, connection, msg) -> None:
    """Dry run, optionally with an unsaved draft rule in place of its saved self."""
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    override = None
    draft_id = None
    if "rule" in msg:
        try:
            draft = _validate_rule(manager, msg["rule"])
        except vol.Invalid as err:
            connection.send_error(msg["id"], "invalid_format", str(err))
            return
        draft_id = draft.setdefault("id", "__draft__")
        rules = manager.rules_raw
        if any(r["id"] == draft_id for r in rules):
            override = [draft if r["id"] == draft_id else r for r in rules]
        else:
            override = [*rules, draft]
    result = await manager.async_apply(dry_run=True, rules_override=override)
    payload = result.to_dict()
    if draft_id is not None:
        entities = sorted(result.rule_entities.get(draft_id, set()))
        payload["draft"] = {
            "count": len(entities),
            "entities": [
                {"entity_id": e, "name": _name(hass, e)} for e in entities[:200]
            ],
        }
    connection.send_result(msg["id"], payload)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/explain", vol.Required("entity_id"): str}
)
@websocket_api.async_response
async def ws_explain(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    connection.send_result(msg["id"], manager.explain(msg["entity_id"]))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "propsense/apply", vol.Optional("dry_run", default=False): bool}
)
@websocket_api.async_response
async def ws_apply(hass, connection, msg) -> None:
    manager = _manager(hass, connection, msg)
    if manager is None:
        return
    result = await manager.async_apply(dry_run=msg["dry_run"])
    connection.send_result(msg["id"], result.to_dict())
