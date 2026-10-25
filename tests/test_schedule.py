"""Timers and schedules: auto-off that survives restarts, time and sun triggers."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers import label_registry as lr
from homeassistant.util import dt as dt_util

from .conftest import settle
from .test_integration import make_entity, setup


@pytest.fixture
def label(hass: HomeAssistant):
    return lr.async_get(hass).async_create("Auto off").label_id


def timer_rule(label, hours=3, state="on", do="turn_off"):
    return {
        "id": "t1",
        "name": "Outlets auto-off",
        "include": {"labels": [label]},
        "actions": [
            {
                "type": "schedule",
                "config": {
                    "trigger": "state_for",
                    "state": state,
                    "do": do,
                    "duration": {"hours": hours, "minutes": 0, "seconds": 0},
                },
            }
        ],
    }


def time_rule(label, at="18:00:00", do="turn_on", days=None, catch_up=0):
    return {
        "id": "s1",
        "name": "Evening",
        "include": {"labels": [label]},
        "actions": [
            {
                "type": "schedule",
                "config": {
                    "trigger": "time",
                    "at": at,
                    "do": do,
                    "days": days or [],
                    "catch_up_minutes": catch_up,
                },
            }
        ],
    }


async def advance(hass, freezer, **delta):
    freezer.tick(timedelta(**delta))
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()


async def test_outlet_turns_off_after_the_duration(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    plug = make_entity(hass, "switch", "plug", labels=[label])
    await setup(hass, [timer_rule(label)])
    await settle(hass)

    await advance(hass, freezer, hours=2, minutes=59)
    assert calls == []
    await advance(hass, freezer, minutes=2)
    assert [c.data["entity_id"] for c in calls] == [[plug]]


async def test_turning_it_off_by_hand_cancels_the_timer(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    plug = make_entity(hass, "switch", "plug", labels=[label])
    await setup(hass, [timer_rule(label)])
    await settle(hass)

    await advance(hass, freezer, hours=1)
    hass.states.async_set(plug, "off")  # physical switch
    await advance(hass, freezer, hours=1)
    hass.states.async_set(plug, "on")  # back on: a fresh 3 h starts now
    await advance(hass, freezer, hours=2, minutes=30)
    assert calls == []
    await advance(hass, freezer, minutes=40)
    assert len(calls) == 1


async def test_deadline_survives_a_restart(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    make_entity(hass, "switch", "plug", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)

    await advance(hass, freezer, hours=2)  # 1 h left
    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.tick(timedelta(minutes=30))  # down for 30 min
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)

    await advance(hass, freezer, minutes=25)
    assert calls == []  # the timer was not reset to 3 h, nor lost
    await advance(hass, freezer, minutes=10)
    assert len(calls) == 1


async def test_deadline_that_passed_while_down_fires_after_start(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    make_entity(hass, "switch", "plug", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)

    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.tick(timedelta(hours=5))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    await advance(hass, freezer, seconds=1)
    assert len(calls) == 1


async def test_removing_the_rule_stops_the_timer(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    make_entity(hass, "switch", "plug", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)

    await entry.runtime_data.async_set_rules([])
    await settle(hass)
    await advance(hass, freezer, hours=4)
    assert calls == []


async def test_dry_run_never_fires(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    make_entity(hass, "switch", "plug", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "settings": {"dry_run": True}}
    )
    await advance(hass, freezer, hours=4)
    assert calls == []


async def test_locks_are_never_governed(hass, label):
    make_entity(hass, "lock", "front", labels=[label])
    entry = await setup(hass, [timer_rule(label, do="turn_on", state="off")])
    await settle(hass)
    assert entry.runtime_data.last.blocked["lock.front"] == "domain 'lock' is blocked"


async def test_unsupported_domains_are_skipped_with_a_reason(hass, label):
    make_entity(hass, "sensor", "temp", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)
    assert "can't be turned on or off" in entry.runtime_data.last.blocked["sensor.temp"]


async def test_time_trigger_turns_lights_on_at_the_time_on_chosen_days(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_on")
    freezer.move_to(datetime(2026, 10, 26, 12, 0, tzinfo=dt_util.get_default_time_zone()))  # Monday
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "off")
    await setup(hass, [time_rule(label, at="18:00:00", days=["mon"])])
    await settle(hass)

    await advance(hass, freezer, hours=5)
    assert calls == []
    await advance(hass, freezer, hours=1, minutes=1)
    assert [c.data["entity_id"] for c in calls] == [[lamp]]

    hass.states.async_set(lamp, "off")
    await advance(hass, freezer, days=1)  # Tuesday 18:01: not a chosen day
    assert len(calls) == 1


async def test_already_on_lights_are_left_alone(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_on")
    freezer.move_to(datetime(2026, 10, 26, 12, 0, tzinfo=dt_util.get_default_time_zone()))
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "on")
    await setup(hass, [time_rule(label)])
    await settle(hass)
    await advance(hass, freezer, hours=7)
    assert calls == []


async def test_missed_trigger_is_caught_up_within_the_grace_period(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_on")
    freezer.move_to(datetime(2026, 10, 26, 17, 50, tzinfo=dt_util.get_default_time_zone()))
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "off")
    entry = await setup(hass, [time_rule(label, catch_up=30)])
    await settle(hass)

    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.move_to(datetime(2026, 10, 26, 18, 10, tzinfo=dt_util.get_default_time_zone()))  # 10 min late
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    await advance(hass, freezer, seconds=1)
    assert len(calls) == 1

    # and not twice
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    await advance(hass, freezer, seconds=1)
    assert len(calls) == 1


async def test_late_beyond_the_grace_period_is_skipped(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_on")
    freezer.move_to(datetime(2026, 10, 26, 17, 50, tzinfo=dt_util.get_default_time_zone()))
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "off")
    entry = await setup(hass, [time_rule(label, catch_up=5)])
    await settle(hass)
    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.move_to(datetime(2026, 10, 26, 18, 30, tzinfo=dt_util.get_default_time_zone()))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    await advance(hass, freezer, seconds=1)
    assert calls == []


async def test_sun_trigger_is_scheduled_with_its_offset(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    hass.states.async_set(lamp, "off")
    rule = {
        "id": "sun",
        "name": "Sunset",
        "include": {"labels": [label]},
        "actions": [
            {
                "type": "schedule",
                "config": {"trigger": "sun", "event": "sunset", "offset_minutes": -30, "do": "turn_on"},
            }
        ],
    }
    entry = await setup(hass, [rule])
    await settle(hass)
    status = entry.runtime_data.registry.get("schedule").status()
    (item,) = status["schedules"]
    assert item["label"] == "Turn on at sunset -30 min"
    assert item["next"] and dt_util.parse_datetime(item["next"]) > dt_util.utcnow()


async def test_schedule_config_is_validated(hass, hass_ws_client, label):
    await setup(hass, [])
    client = await hass_ws_client(hass)

    async def save(config):
        await client.send_json_auto_id(
            {
                "type": "propsense/rule/save",
                "rule": {"name": "x", "actions": [{"type": "schedule", "config": config}]},
            }
        )
        return await client.receive_json()

    assert (await save({"trigger": "state_for", "do": "turn_off"}))["error"]["code"] == "invalid_format"
    assert (await save({"trigger": "state_for", "state": "on", "do": "turn_on",
                        "duration": {"hours": 1}}))["error"]["code"] == "invalid_format"
    assert (await save({"trigger": "time", "do": "turn_on"}))["error"]["code"] == "invalid_format"
    assert (await save({"trigger": "state_for", "do": "turn_off", "duration": {"hours": 3}}))["success"]
    assert (await save({"trigger": "time", "at": "18:00:00", "do": "turn_on"}))["success"]


async def test_switched_off_while_down_is_left_alone(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    plug = make_entity(hass, "switch", "plug", labels=[label])
    entry = await setup(hass, [timer_rule(label)])
    await settle(hass)

    assert await hass.config_entries.async_unload(entry.entry_id)
    hass.states.async_set(plug, "off")  # someone pressed the button
    freezer.tick(timedelta(hours=5))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    await advance(hass, freezer, seconds=1)
    assert calls == []
    assert entry.runtime_data.registry.get("schedule").status()["schedules"][0]["timers"] == []


async def test_unavailable_at_the_deadline_acts_when_it_reports_back(hass, freezer, label):
    calls = async_mock_service(hass, "homeassistant", "turn_off")
    plug = make_entity(hass, "switch", "plug", labels=[label])
    await setup(hass, [timer_rule(label)])
    await settle(hass)

    await advance(hass, freezer, hours=1)
    hass.states.async_set(plug, "unavailable")
    await advance(hass, freezer, hours=3)  # deadline passes while unavailable
    assert calls == []
    hass.states.async_set(plug, "on")  # still on once it is back
    await advance(hass, freezer, seconds=1)
    assert len(calls) == 1
