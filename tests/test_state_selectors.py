"""State-based selection: live re-evaluation, only when a state flips a rule."""
from __future__ import annotations

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import label_registry as lr

from .conftest import settle
from .test_integration import exposed, make_entity, setup


def low_battery(**extra):
    return {
        "id": "low",
        "name": "Low battery",
        "include": {"conditions": ["attr:battery_level < 20"], **extra},
        "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}],
    }


def sensor(hass, name, level):
    entity_id = make_entity(hass, "sensor", name)
    hass.states.async_set(entity_id, "ok", {"battery_level": level})
    return entity_id


async def test_selection_follows_the_state_without_a_restart(hass):
    a = sensor(hass, "a", 80)
    b = sensor(hass, "b", 10)
    await setup(hass, [low_battery()])
    assert exposed(hass) == {b}

    hass.states.async_set(a, "ok", {"battery_level": 5})  # drops below 20
    await settle(hass)
    assert exposed(hass) == {a, b}

    hass.states.async_set(b, "ok", {"battery_level": 90})  # replaced
    await settle(hass)
    assert exposed(hass) == {a}


async def test_state_rules_combine_with_the_other_selectors(hass):
    label = lr.async_get(hass).async_create("Watch").label_id
    a = make_entity(hass, "light", "a", labels=[label])
    b = make_entity(hass, "light", "b")
    hass.states.async_set(a, "on")
    hass.states.async_set(b, "on")
    rule = {
        "id": "on",
        "name": "Watched lights that are on",
        "include": {"labels": [label], "states": ["on"]},
        "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}],
    }
    await setup(hass, [rule])
    assert exposed(hass) == {a}
    hass.states.async_set(a, "off")
    await settle(hass)
    assert exposed(hass) == set()


async def test_unrelated_state_changes_do_not_rerun_the_plan(hass):
    a = sensor(hass, "a", 80)
    other = sensor(hass, "other", 80)
    entry = await setup(hass, [low_battery()])
    first = entry.runtime_data.last

    # moves, but stays on the same side of the condition
    hass.states.async_set(a, "ok", {"battery_level": 70})
    hass.states.async_set(other, "ok", {"battery_level": 50})
    hass.states.async_set("sensor.not_in_any_rule", "1")
    await settle(hass)
    assert entry.runtime_data.last is first

    hass.states.async_set(a, "ok", {"battery_level": 19})  # now it flips
    await settle(hass)
    assert entry.runtime_data.last is not first


async def test_rules_without_state_selectors_ignore_state_changes(hass):
    label = lr.async_get(hass).async_create("L").label_id
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "on")
    entry = await setup(
        hass,
        [{"id": "r", "name": "r", "include": {"labels": [label]},
          "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}]}],
    )
    first = entry.runtime_data.last
    hass.states.async_set(lamp, "off")
    await settle(hass)
    assert entry.runtime_data.last is first


async def test_exclude_by_state(hass):
    label = lr.async_get(hass).async_create("L").label_id
    ok = make_entity(hass, "light", "ok", labels=[label])
    gone = make_entity(hass, "light", "gone", labels=[label])
    hass.states.async_set(ok, "on")
    hass.states.async_set(gone, "unavailable")
    rule = {
        "id": "r", "name": "r",
        "include": {"labels": [label]},
        "exclude": {"states": ["unavailable"]},
        "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}],
    }
    await setup(hass, [rule])
    assert exposed(hass) == {ok}
    hass.states.async_set(gone, "on")  # comes back
    await settle(hass)
    assert exposed(hass) == {ok, gone}


async def test_editing_rules_resets_what_is_watched(hass):
    a = sensor(hass, "a", 5)
    entry = await setup(hass, [])
    assert exposed(hass) == set()
    await entry.runtime_data.async_set_rules([low_battery()])
    await settle(hass)
    assert exposed(hass) == {a}
    hass.states.async_set(a, "ok", {"battery_level": 90})
    await settle(hass)
    assert exposed(hass) == set()


async def test_bad_conditions_are_rejected_when_saving(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "propsense/rule/save",
         "rule": {"name": "x", "include": {"conditions": ["state ~ 3"]}, "actions": []}}
    )
    reply = await client.receive_json()
    assert reply["error"]["code"] == "invalid_format" and "operator" in reply["error"]["message"]
    await client.send_json_auto_id(
        {"type": "propsense/rule/save",
         "rule": {"name": "x", "include": {"conditions": ["state < 20"], "states": ["on"]}, "actions": []}}
    )
    assert (await client.receive_json())["success"]
