"""The built-in group action: create or edit group helpers from rules."""
from __future__ import annotations

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    entity_registry as er,
    label_registry as lr,
)
from homeassistant.setup import async_setup_component

from custom_components.propsense.group_action import LABEL_NAME

from .conftest import settle
from .test_integration import make_entity, setup


@pytest.fixture
def label(hass: HomeAssistant):
    return lr.async_get(hass).async_create("Tunable").label_id


async def lamp(hass, name, label, modes, domain="light"):
    entity_id = make_entity(hass, domain, name, labels=[label])
    hass.states.async_set(entity_id, "on", {"supported_color_modes": modes})
    return entity_id


def group_rule(label, **action_config):
    return {
        "id": "g1",
        "name": "Tunable lights",
        "include": {"labels": [label], "capabilities": ["color_temp"]},
        "actions": [{"type": "group", "config": action_config}],
    }


async def group_entries(hass):
    return hass.config_entries.async_entries("group")


async def test_creates_a_group_with_matching_members_and_labels_it(hass, label):
    await async_setup_component(hass, "light", {})
    await async_setup_component(hass, "group", {})
    tunable = await lamp(hass, "tunable", label, ["color_temp"])
    await lamp(hass, "plain", label, ["onoff"])

    entry = await setup(
        hass, [group_rule(label, create_name="Tunable group", group_type="light")]
    )
    await settle(hass)
    await settle(hass)

    (group,) = await group_entries(hass)
    assert group.title == "Tunable group"
    assert group.options["entities"] == [tunable]

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("light", "group", group.entry_id)
    marker = lr.async_get(hass).async_get_label_by_name(LABEL_NAME)
    assert marker is not None
    assert marker.label_id in registry.async_get(entity_id).labels
    assert entry.runtime_data.last.actions["group"]


async def test_existing_group_is_edited_and_hand_added_members_are_removed(hass, label):
    await async_setup_component(hass, "light", {})
    await async_setup_component(hass, "group", {})
    tunable = await lamp(hass, "tunable", label, ["color_temp"])
    stray = await lamp(hass, "stray", "other", ["onoff"])

    # create a group by hand, as a user would, with the stray member in it
    flow = hass.config_entries.flow
    r = await flow.async_init("group", context={"source": "user"})
    r = await flow.async_configure(r["flow_id"], {"next_step_id": "light"})
    r = await flow.async_configure(
        r["flow_id"], {"name": "Mine", "entities": [stray], "hide_members": False}
    )
    await settle(hass)
    group_entity = er.async_get(hass).async_get_entity_id(
        "light", "group", r["result"].entry_id
    )
    assert group_entity

    await setup(hass, [group_rule(label, group=group_entity)])
    await settle(hass)

    (group,) = await group_entries(hass)
    assert group.options["entities"] == [tunable]
    marker = lr.async_get(hass).async_get_label_by_name(LABEL_NAME)
    assert marker.label_id in er.async_get(hass).async_get(group_entity).labels


async def test_members_of_the_wrong_domain_are_skipped_and_reported(hass, label):
    await async_setup_component(hass, "light", {})
    await async_setup_component(hass, "group", {})
    tunable = await lamp(hass, "tunable", label, ["color_temp"])
    make_entity(hass, "switch", "plug", labels=[label])
    rule = group_rule(label, create_name="Only lights", group_type="light")
    rule["include"] = {"labels": [label]}  # no capabilities filter: the switch matches

    entry = await setup(hass, [rule])
    await settle(hass)

    (group,) = await group_entries(hass)
    assert group.options["entities"] == [tunable]
    assert "light group" in entry.runtime_data.last.blocked["switch.plug"]


async def test_nothing_is_created_for_an_empty_selection(hass, label):
    await async_setup_component(hass, "group", {})
    await setup(hass, [group_rule(label, create_name="Empty", group_type="light")])
    await settle(hass)
    assert await group_entries(hass) == []


async def test_group_action_config_is_validated(hass, hass_ws_client, label):
    await setup(hass, [])
    client = await hass_ws_client(hass)

    async def save(config):
        await client.send_json_auto_id(
            {
                "type": "propsense/rule/save",
                "rule": {"name": "x", "actions": [{"type": "group", "config": config}]},
            }
        )
        return await client.receive_json()

    assert (await save({}))["error"]["code"] == "invalid_format"
    assert (await save({"group": "light.x", "create_name": "y"}))["error"]["code"] == "invalid_format"
    assert (await save({"group": "light.not_a_group_helper"}))["error"]["code"] == "invalid_format"
    assert (await save({"create_name": "Fine", "group_type": "light"}))["success"]
