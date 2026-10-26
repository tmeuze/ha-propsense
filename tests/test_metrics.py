"""Shipping numeric history: opt-in, bounded, one URL, survives outages."""
from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    entity_registry as er,
    label_registry as lr,
)
from homeassistant.util import dt as dt_util

from custom_components.propsense.metrics_action import line, numeric

from .conftest import settle
from .test_integration import make_entity, setup

URL = "https://metrics.example.test/write"
ALLOW = {"allow_external_data": True, "metrics_url": URL}


@pytest.fixture
def label(hass: HomeAssistant):
    return lr.async_get(hass).async_create("Metrics").label_id


def rule(label, **config):
    return {
        "id": "m1",
        "name": "Ship",
        "include": {"labels": [label]},
        "actions": [{"type": "metrics", "config": config}],
    }


def sensor(hass, name, label, state="21.5", **attrs):
    entity_id = make_entity(hass, "sensor", name, labels=[label])
    hass.states.async_set(entity_id, state, attrs)
    return entity_id


async def tick(hass, freezer, seconds=31):
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()


def bodies(aioclient_mock):
    return [call[2].decode() for call in aioclient_mock.mock_calls if call[0] == "POST"]


# ------------------------------------------------------------ line protocol


def test_line_escapes_tags_and_formats_the_value(hass):
    when = dt_util.utc_from_timestamp(1_700_000_000)
    text = line({"entity_id": "sensor.a", "area": "Living room, north", "x": "a=b"}, 21.5, when)
    assert text == (
        r"homeassistant,area=Living\ room\,\ north,entity_id=sensor.a,x=a\=b "
        "value=21.5 1700000000000000000"
    )


def test_numeric_accepts_numbers_only():
    assert numeric("21.5", booleans=False) == 21.5
    assert numeric("-3", booleans=False) == -3.0
    for bad in (None, "", "unknown", "unavailable", "on", "nan", "inf", "abc"):
        assert numeric(bad, booleans=False) is None
    assert numeric("on", booleans=True) == 1.0 and numeric("off", booleans=True) == 0.0


# ---------------------------------------------------------------- behaviour


async def test_nothing_is_sent_until_data_may_leave(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)])  # allow_external_data is off
    await settle(hass)
    assert entry.runtime_data.last.dormant == {"m1": ["metrics"]}
    await tick(hass, freezer)
    assert bodies(aioclient_mock) == []


async def test_numeric_states_are_posted_with_tags_to_the_configured_url(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    area = ar.async_get(hass).async_create("Kitchen")
    temp = sensor(hass, "temp", label, device_class="temperature", unit_of_measurement="°C")
    er.async_get(hass).async_update_entity(temp, area_id=area.id)
    await setup(hass, [rule(label)], ALLOW)
    await settle(hass)

    hass.states.async_set(temp, "22.5", {"device_class": "temperature", "unit_of_measurement": "°C"})
    await hass.async_block_till_done()
    await tick(hass, freezer)

    (body,) = bodies(aioclient_mock)
    (text,) = body.splitlines()
    assert text.startswith(
        "homeassistant,area=Kitchen,device_class=temperature,domain=sensor,"
        "entity_id=sensor.temp,unit_of_measurement=°C value=22.5 "
    )
    assert all(str(c[1]) == URL for c in aioclient_mock.mock_calls)


async def test_non_numeric_states_are_skipped(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    temp = sensor(hass, "temp", label)
    await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    for state in ("unavailable", "unknown", "hot", "nan"):
        hass.states.async_set(temp, state)
        await hass.async_block_till_done()
    await tick(hass, freezer)
    assert bodies(aioclient_mock) == []


async def test_minimum_interval_sends_the_latest_value_later(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    temp = sensor(hass, "temp", label)
    await setup(hass, [rule(label, min_interval_seconds=60)], ALLOW)
    await settle(hass)

    hass.states.async_set(temp, "1")
    await hass.async_block_till_done()
    for value in ("2", "3"):  # inside the interval: only the last survives
        hass.states.async_set(temp, value)
        await hass.async_block_till_done()
    await tick(hass, freezer, 31)
    first = "\n".join(bodies(aioclient_mock))
    assert "value=1.0" in first and "value=2.0" not in first and "value=3.0" not in first

    await tick(hass, freezer, 31)  # the interval is up: the latest value goes out
    assert "value=3.0" in "\n".join(bodies(aioclient_mock))
    assert "value=2.0" not in "\n".join(bodies(aioclient_mock))


async def test_booleans_are_sent_as_numbers_only_when_asked(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    plug = make_entity(hass, "switch", "plug", labels=[label])
    hass.states.async_set(plug, "off")
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    assert "domain 'switch' has no numeric state" in entry.runtime_data.last.blocked[plug]

    await entry.runtime_data.async_set_rules([rule(label, include_booleans=True)])
    await settle(hass)
    hass.states.async_set(plug, "on")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    assert "entity_id=switch.plug" in "\n".join(bodies(aioclient_mock))
    assert "value=1.0" in "\n".join(bodies(aioclient_mock))


async def test_an_outage_keeps_points_and_sends_them_when_it_ends(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=500)
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    provider = entry.runtime_data.registry.get("metrics")

    hass.states.async_set(temp, "5")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    assert provider.status()["buffered"] == 1 and provider.status()["last_error"] == "HTTP 500"

    aioclient_mock.clear_requests()
    aioclient_mock.post(URL, status=204)
    await tick(hass, freezer)
    assert provider.status()["buffered"] == 0 and provider.status()["sent"] == 1
    assert "value=5.0" in "\n".join(bodies(aioclient_mock))


async def test_an_unreachable_endpoint_is_survived(hass, freezer, label, aioclient_mock):
    import aiohttp

    aioclient_mock.post(URL, exc=aiohttp.ClientConnectionError("down"))
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    hass.states.async_set(temp, "5")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    provider = entry.runtime_data.registry.get("metrics")
    assert provider.status()["buffered"] == 1 and "down" in provider.status()["last_error"]


async def test_the_buffer_is_bounded_and_drops_the_oldest(hass, freezer, label, aioclient_mock, monkeypatch):
    from collections import deque

    aioclient_mock.post(URL, status=500)
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label, min_interval_seconds=10)], ALLOW)
    await settle(hass)
    provider = entry.runtime_data.registry.get("metrics")
    provider._buffer = deque(maxlen=3)

    for n in range(6):
        hass.states.async_set(temp, str(n))
        await hass.async_block_till_done()
        freezer.tick(timedelta(seconds=11))
        # the interval uses a monotonic clock; step it too
        provider._last_emit[temp] -= 11
    status = provider.status()
    assert status["buffered"] == 3 and status["dropped"] == 3


async def test_the_entity_cap_refuses_a_too_wide_rule(hass, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    for n in range(4):
        sensor(hass, f"t{n}", label)
    entry = await setup(hass, [rule(label, max_entities=3)], ALLOW)
    await settle(hass)
    result = entry.runtime_data.last.actions["metrics"]
    (res,) = result.values()
    assert res.refused is True
    assert entry.runtime_data.registry.get("metrics").status()["targets"] == []


async def test_dry_run_sends_nothing(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "settings": {**ALLOW, "dry_run": True}}
    )
    hass.states.async_set(temp, "9")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    assert bodies(aioclient_mock) == []


async def test_withdrawing_permission_drops_the_buffer_and_sends_nothing(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=500)
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    hass.states.async_set(temp, "5")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    provider = entry.runtime_data.registry.get("metrics")
    assert provider.status()["buffered"] == 1

    aioclient_mock.clear_requests()
    aioclient_mock.post(URL, status=204)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "settings": {"allow_external_data": False}}
    )
    await provider.async_flush()
    assert provider.status()["buffered"] == 0
    assert bodies(aioclient_mock) == []


async def test_removing_the_rule_stops_the_listener(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    temp = sensor(hass, "temp", label)
    entry = await setup(hass, [rule(label)], ALLOW)
    await settle(hass)
    await entry.runtime_data.async_set_rules([])
    await settle(hass)
    hass.states.async_set(temp, "7")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    assert bodies(aioclient_mock) == []


async def test_settings_validate_the_url_and_the_permission_is_listed(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)

    async def metrics_type():
        await client.send_json_auto_id({"type": "propsense/overview"})
        result = (await client.receive_json())["result"]
        return next(a for a in result["actions"] if a["type"] == "metrics")

    async def update(settings):
        await client.send_json_auto_id({"type": "propsense/settings/update", "settings": settings})
        return await client.receive_json()

    before = await metrics_type()
    assert before["builtin"] and not before["available"] and before["requires"] == "external_data"

    assert (await update({"metrics_url": "ftp://x"}))["error"]["code"] == "invalid_format"
    # there is no default URL, so the permission cannot be given without one
    refused = await update({"allow_external_data": True})
    assert refused["error"]["code"] == "invalid_format" and "Metrics URL" in refused["error"]["message"]
    assert (await update({"metrics_url": "http://10.1.2.3/write", "allow_external_data": True}))["success"]
    await hass.async_block_till_done()
    after = await metrics_type()
    assert after["available"] and after["requires"] is None


async def test_no_url_means_nothing_is_sent(hass, freezer, label, aioclient_mock):
    aioclient_mock.post(URL, status=204)
    temp = sensor(hass, "temp", label)
    # permission on but no URL (e.g. edited by hand): never sends, says why
    entry = await setup(hass, [rule(label)], {"allow_external_data": True})
    await settle(hass)
    hass.states.async_set(temp, "5")
    await hass.async_block_till_done()
    await tick(hass, freezer)
    assert bodies(aioclient_mock) == []
    assert entry.runtime_data.registry.get("metrics").status()["last_error"] == (
        "No Metrics URL is set (Settings)"
    )
