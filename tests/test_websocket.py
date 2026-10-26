"""The websocket API the panel uses."""
from __future__ import annotations

from homeassistant.helpers import label_registry as lr

from .test_actions import FakeGrant, ensure_loaded
from .test_integration import exposed, make_entity, setup

from custom_components.propsense.api import async_register_action


def expose_rule(label, rid=None, name="Voice"):
    rule = {
        "name": name,
        "include": {"labels": [label]},
        "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}],
    }
    if rid:
        rule["id"] = rid
    return rule


async def test_overview_lists_rules_settings_and_action_types(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "propsense/overview"})
    result = (await client.receive_json())["result"]
    assert result["rules"] == []
    assert result["settings"]["allow_third_party_actions"] is False
    expose = next(a for a in result["actions"] if a["type"] == "expose")
    assert expose["builtin"] and expose["available"]
    assert expose["schema"][0]["name"] == "assistants"


async def test_save_preview_and_delete_a_rule(hass, hass_ws_client):
    label = lr.async_get(hass).async_create("Expose: Voice").label_id
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    await setup(hass, [])
    client = await hass_ws_client(hass)

    # a draft previews without saving or applying
    await client.send_json_auto_id(
        {"type": "propsense/preview", "rule": expose_rule(label)}
    )
    preview = (await client.receive_json())["result"]
    assert preview["draft"]["count"] == 1
    assert preview["draft"]["entities"][0]["entity_id"] == lamp
    assert exposed(hass) == set()

    await client.send_json_auto_id(
        {"type": "propsense/rule/save", "rule": expose_rule(label)}
    )
    saved = (await client.receive_json())["result"]["rule"]
    assert saved["id"]
    await hass.async_block_till_done()
    await client.send_json_auto_id({"type": "propsense/apply"})
    await client.receive_json()
    assert exposed(hass) == {lamp}

    await client.send_json_auto_id(
        {"type": "propsense/rule/delete", "rule_id": saved["id"]}
    )
    assert (await client.receive_json())["success"]
    await client.send_json_auto_id({"type": "propsense/apply"})
    await client.receive_json()
    assert exposed(hass) == set()


async def test_invalid_rule_and_settings_are_rejected(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "propsense/rule/save", "rule": {"name": ""}})
    assert (await client.receive_json())["error"]["code"] == "invalid_format"
    await client.send_json_auto_id(
        {"type": "propsense/rule/save", "rule": {"name": "x", "actions": [
            {"type": "expose", "config": {"assistants": ["nope"]}}]}}
    )
    assert (await client.receive_json())["error"]["code"] == "invalid_format"
    await client.send_json_auto_id(
        {"type": "propsense/settings/update", "settings": {"max_exposed": -1}}
    )
    assert (await client.receive_json())["error"]["code"] == "invalid_format"


async def test_settings_update_persists(hass, hass_ws_client):
    entry = await setup(hass, [])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "propsense/settings/update", "settings": {"max_exposed": 7}}
    )
    assert (await client.receive_json())["success"]
    assert entry.options["settings"]["max_exposed"] == 7


async def test_explain_reports_each_rule(hass, hass_ws_client):
    label = lr.async_get(hass).async_create("Expose: Voice").label_id
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    lock = make_entity(hass, "lock", "front", labels=[label])
    await setup(hass, [{**expose_rule(label, "r1"), "name": "Voice"}])
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "propsense/explain", "entity_id": lamp})
    out = (await client.receive_json())["result"]
    assert out["found"] and label in out["labels"]
    assert out["capabilities"] == []
    assert out["rules"][0]["actions"][0]["status"] == "applies"

    await client.send_json_auto_id({"type": "propsense/explain", "entity_id": lock})
    out = (await client.receive_json())["result"]
    assert out["rules"][0]["actions"][0]["status"] == "blocked"

    await client.send_json_auto_id({"type": "propsense/explain", "entity_id": "light.nope"})
    assert (await client.receive_json())["result"]["found"] is False


async def test_third_party_action_type_is_listed_unavailable_until_allowed(
    hass, hass_ws_client
):
    await ensure_loaded(hass)
    async_register_action(hass, FakeGrant())
    await setup(hass, [])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "propsense/overview"})
    result = (await client.receive_json())["result"]
    fake = next(a for a in result["actions"] if a["type"] == "fake.grant")
    assert fake["available"] is False and fake["builtin"] is False


async def test_non_admin_is_refused(hass, hass_ws_client, hass_read_only_access_token):
    await setup(hass, [])
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "propsense/overview"})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"


async def test_panel_is_registered_for_admins_and_removed_on_unload(hass):
    entry = await setup(hass, [])
    panel = hass.data["frontend_panels"]["propsense"]
    assert panel.require_admin is True
    assert panel.sidebar_title == "PropSense"

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert "propsense" not in hass.data["frontend_panels"]


async def test_overview_offers_registry_choices_and_explain_shows_the_new_facts(hass, hass_ws_client):
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    cfg = MockConfigEntry(domain="test")
    cfg.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=cfg.entry_id, identifiers={("test", "d")},
        manufacturer="IKEA", model="TRADFRI",
    )
    lamp = er.async_get(hass).async_get_or_create(
        "light", "hue", "1", suggested_object_id="lamp", device_id=device.id
    ).entity_id
    hass.states.async_set(lamp, "on")
    await setup(hass, [])
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "propsense/overview"})
    choices = (await client.receive_json())["result"]["choices"]
    assert "hue" in choices["integrations"]
    assert choices["manufacturers"] == ["IKEA"] and choices["models"] == ["TRADFRI"]

    await client.send_json_auto_id({"type": "propsense/explain", "entity_id": lamp})
    out = (await client.receive_json())["result"]
    assert (out["integration"], out["manufacturer"], out["model"]) == ("hue", "IKEA", "TRADFRI")
    assert out["entity_category"] == "primary"
