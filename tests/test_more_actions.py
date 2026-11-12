"""Apply a label, voice aliases, flag in Repairs, run actions on enter/leave, and the loop breaker."""
from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import async_mock_service

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    entity_registry as er,
    issue_registry as ir,
    label_registry as lr,
)

from custom_components.propsense.const import DOMAIN, ISSUE_OSCILLATING

from .conftest import settle
from .test_integration import make_entity, setup


def rule(include, action_type, config, rid="r1", exclude=None):
    return {
        "id": rid,
        "name": rid,
        "include": include,
        "exclude": exclude or {},
        "actions": [{"type": action_type, "config": config}],
    }


def aliases_of(hass, entity_id):
    """Plain-text aliases (newer Home Assistant versions also keep a name marker in the set)."""
    return {a for a in er.async_get(hass).async_get(entity_id).aliases if isinstance(a, str)}


def flagged(hass):
    return [
        i for i in ir.async_get(hass).issues.values()
        if i.domain == DOMAIN and i.issue_id.startswith("flagged_")
    ]


def labels_of(hass, entity_id):
    reg = lr.async_get(hass)
    return {reg.async_get_label(i).name for i in er.async_get(hass).async_get(entity_id).labels}


# ------------------------------------------------------------------ label


async def test_label_is_applied_created_and_removed_when_no_longer_selected(hass):
    low = make_entity(hass, "sensor", "low")
    fine = make_entity(hass, "sensor", "fine")
    hass.states.async_set(low, "ok", {"battery_level": 5})
    hass.states.async_set(fine, "ok", {"battery_level": 90})
    stale = make_entity(hass, "sensor", "stale")  # had it by hand, but no longer qualifies
    hass.states.async_set(stale, "ok", {"battery_level": 80})
    existing = lr.async_get(hass).async_create("Needs battery")
    reg = er.async_get(hass)
    reg.async_update_entity(stale, labels={existing.label_id})

    await setup(hass, [rule({"conditions": ["attr:battery_level < 20"]}, "label", {"name": "Needs battery"})])
    assert labels_of(hass, low) == {"Needs battery"}
    assert labels_of(hass, fine) == set()
    assert labels_of(hass, stale) == set()  # single source of truth

    hass.states.async_set(fine, "ok", {"battery_level": 3})  # drops: gets the label live
    await settle(hass)
    assert labels_of(hass, fine) == {"Needs battery"}


async def test_the_label_is_created_if_missing_and_other_labels_are_kept(hass):
    keep = lr.async_get(hass).async_create("Keep me").label_id
    lamp = make_entity(hass, "light", "lamp", labels=[keep])
    await setup(hass, [rule({"entities": [lamp]}, "label", {"name": "Brand new"})])
    assert labels_of(hass, lamp) == {"Keep me", "Brand new"}


async def test_labels_chain_between_rules(hass):
    plug = make_entity(hass, "switch", "plug")
    other = make_entity(hass, "switch", "other")
    rules = [
        rule({"entities": [plug]}, "label", {"name": "Outdoor"}, rid="a"),
        rule({"label_patterns": ["outdoor"]}, "label", {"name": "Weatherproof"}, rid="b"),
    ]
    await setup(hass, rules)
    await settle(hass)
    assert labels_of(hass, plug) == {"Outdoor", "Weatherproof"}
    assert labels_of(hass, other) == set()


async def test_state_only_entities_are_skipped_with_a_reason(hass):
    hass.states.async_set("sensor.virtual", "1")
    entry = await setup(hass, [rule({"entities": ["sensor.virtual"]}, "label", {"name": "X"})])
    assert "no registry entry" in entry.runtime_data.last.blocked["sensor.virtual"]


# ------------------------------------------------------------------ aliases


async def test_aliases_are_added_and_removed_and_others_are_untouched(hass):
    lamp = make_entity(hass, "light", "lamp")
    gone = make_entity(hass, "light", "gone")
    reg = er.async_get(hass)
    reg.async_update_entity(lamp, aliases={"reading lamp"})
    reg.async_update_entity(gone, aliases={"sala", "keep"})

    await setup(hass, [rule({"entities": [lamp]}, "aliases", {"aliases": ["sala"]})])
    assert aliases_of(hass, lamp) == {"reading lamp", "sala"}
    assert aliases_of(hass, gone) == {"keep"}  # no longer selected: only that alias goes


# --------------------------------------------------------------------- flag


async def test_flag_creates_and_clears_a_repairs_issue(hass):
    a = make_entity(hass, "light", "a")
    make_entity(hass, "light", "b", labels=[lr.async_get(hass).async_create("Tagged").label_id])
    rules = [
        rule({"domains": ["light"]}, "flag", {"title": "Lights without a label"}, rid="f",
             exclude={"label_patterns": ["*"]})
    ]
    entry = await setup(hass, rules)

    issues = flagged(hass)
    assert len(issues) == 1
    issue = issues[0]
    assert issue.translation_placeholders["title"] == "Lights without a label"
    assert issue.translation_placeholders["count"] == "1" and a in issue.translation_placeholders["entities"]

    er.async_get(hass).async_update_entity(a, labels={lr.async_get(hass).async_create("Fixed").label_id})
    await settle(hass)
    assert flagged(hass) == []


# ---------------------------------------------------------------------- run


def notify(event):
    return [{"action": "test.notify", "data": {"entity": "{{ entity_id }}", "event": "{{ event }}"}}]


async def test_run_fires_on_enter_and_leave_not_on_first_sight(hass):
    calls = async_mock_service(hass, "test", "notify")
    label = lr.async_get(hass).async_create("Watch").label_id
    existing = make_entity(hass, "light", "existing", labels=[label])
    late = make_entity(hass, "light", "late")
    config = {"on_enter": notify("enter"), "on_leave": [{"action": "test.notify", "data": {"entity": "{{ entity_id }}", "event": "{{ event }}"}}]}
    await setup(hass, [rule({"labels": [label]}, "run", config)])
    assert calls == []  # baseline only: `existing` already matched

    er.async_get(hass).async_update_entity(late, labels={label})
    await settle(hass)
    assert [(c.data["entity"], c.data["event"]) for c in calls] == [(late, "enter")]

    er.async_get(hass).async_update_entity(existing, labels=set())
    await settle(hass)
    assert [(c.data["entity"], c.data["event"]) for c in calls][-1] == (existing, "leave")


async def test_run_is_capped_per_evaluation(hass):
    calls = async_mock_service(hass, "test", "notify")
    label = lr.async_get(hass).async_create("Watch").label_id
    lamps = [make_entity(hass, "light", f"l{n}") for n in range(6)]
    await setup(hass, [rule({"labels": [label]}, "run", {"on_enter": notify("enter"), "max_per_run": 3})])
    for lamp in lamps:
        er.async_get(hass).async_update_entity(lamp, labels={label})
    await settle(hass)
    assert len(calls) == 3


async def test_run_needs_actions_and_valid_ones(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)

    async def save(config):
        await client.send_json_auto_id(
            {"type": "propsense/rule/save",
             "rule": {"name": "x", "actions": [{"type": "run", "config": config}]}}
        )
        return await client.receive_json()

    assert (await save({}))["error"]["code"] == "invalid_format"
    assert (await save({"on_enter": [{"nonsense_key": 1}]}))["error"]["code"] == "invalid_format"
    assert (await save({"on_enter": notify("enter")}))["success"]


# ----------------------------------------------------- validation of the others


async def test_label_alias_and_flag_configs_are_validated(hass, hass_ws_client):
    await setup(hass, [])
    client = await hass_ws_client(hass)

    async def save(type_, config):
        await client.send_json_auto_id(
            {"type": "propsense/rule/save",
             "rule": {"name": "x", "actions": [{"type": type_, "config": config}]}}
        )
        return await client.receive_json()

    assert (await save("label", {"name": "  "}))["error"]["code"] == "invalid_format"
    assert (await save("aliases", {"aliases": []}))["error"]["code"] == "invalid_format"
    assert (await save("flag", {"title": ""}))["error"]["code"] == "invalid_format"
    assert (await save("label", {"name": "Outdoor"}))["success"]
    assert (await save("aliases", {"aliases": ["sala"]}))["success"]
    assert (await save("flag", {"title": "Check"}))["success"]


# ------------------------------------------------------------- loop breaker


async def test_rules_that_feed_each_other_are_paused(hass, monkeypatch):
    monkeypatch.setattr("custom_components.propsense.manager.OSCILLATION_RUNS", 6)
    lamp = make_entity(hass, "light", "lamp")
    rules = [
        # A is applied unless B is present; B is applied when A is present: a ring
        rule({"entities": [lamp]}, "label", {"name": "A"}, rid="a", exclude={"label_patterns": ["B"]}),
        rule({"label_patterns": ["A"]}, "label", {"name": "B"}, rid="b"),
    ]
    entry = await setup(hass, rules)
    for _ in range(15):  # each pass of the ring needs a fresh evaluation
        if entry.runtime_data._paused_until:
            break
        await settle(hass)

    assert entry.runtime_data._paused_until > 0
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_OSCILLATING) is not None
    assert entry.runtime_data.last is not None


async def test_ordinary_use_does_not_trip_the_breaker(hass):
    label = lr.async_get(hass).async_create("Watch").label_id
    lamps = [make_entity(hass, "light", f"l{n}") for n in range(5)]
    entry = await setup(hass, [rule({"labels": [label]}, "aliases", {"aliases": ["x"]})])
    for lamp in lamps:
        er.async_get(hass).async_update_entity(lamp, labels={label})
        await settle(hass)
    assert entry.runtime_data._paused_until == 0
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_OSCILLATING) is None
    # and the alias really landed on every lamp (a provider error would be swallowed)
    assert all(aliases_of(hass, lamp) == {"x"} for lamp in lamps)
    assert all(r.error is None for t in entry.runtime_data.last.actions.values() for r in t.values())


# ---------------------------------------------------------------- dashboard


def dash_rule(include, **cfg):
    config = {"dashboard": "Guest Panel", "title": "Lights", "group_by": "area", **cfg}
    return rule(include, "dashboard", config)


async def resolve(hass, hass_ws_client, user_admin=True, name="guest-panel"):
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "propsense/dashboard/resolve", "dashboard": name})
    return await client.receive_json()


async def test_dashboard_sections_follow_the_rule_grouped_by_area(hass, hass_ws_client):
    from homeassistant.helpers import area_registry as ar

    kitchen = ar.async_get(hass).async_create("Kitchen")
    lamp = make_entity(hass, "light", "lamp")
    other = make_entity(hass, "light", "other")
    er.async_get(hass).async_update_entity(lamp, area_id=kitchen.id)
    await setup(hass, [dash_rule({"domains": ["light"]})])

    msg = await resolve(hass, hass_ws_client)
    assert msg["success"]
    (section,) = msg["result"]["sections"]
    assert section["title"] == "Lights"
    groups = {g["name"]: g["entities"] for g in section["groups"]}
    assert groups == {"Kitchen": [lamp], "No area": [other]}
    assert [g["name"] for g in section["groups"]][-1] == "No area"  # fallback last


async def test_dashboard_other_name_is_empty_and_disabled_rule_vanishes(hass, hass_ws_client):
    lamp = make_entity(hass, "light", "lamp")
    entry = await setup(hass, [dash_rule({"entities": [lamp]})])
    assert (await resolve(hass, hass_ws_client, name="nothing"))["result"]["sections"] == []

    rules = entry.runtime_data.rules_raw
    rules[0]["enabled"] = False
    await entry.runtime_data.async_set_rules(rules)
    await settle(hass)
    assert (await resolve(hass, hass_ws_client))["result"]["sections"] == []


async def test_dashboard_audience_filters_by_user(hass, hass_ws_client, hass_admin_user):
    from custom_components.propsense.dashboard_action import audience_matches

    assert audience_matches([], "u1", False)
    assert audience_matches(["everyone"], "u1", False)
    assert audience_matches(["non-admins"], "u1", False)
    assert not audience_matches(["non-admins"], "u1", True)
    assert audience_matches(["admins"], "u1", True)
    assert audience_matches(["u2", "u1"], "u1", False)
    assert not audience_matches(["u2"], "u1", False)

    lamp = make_entity(hass, "light", "lamp")
    await setup(hass, [dash_rule({"entities": [lamp]}, audience=["non-admins"])])
    # the test client is an admin, so a non-admin-only section is hidden from it
    assert (await resolve(hass, hass_ws_client))["result"]["sections"] == []


async def test_dashboard_non_admin_can_resolve(hass, hass_ws_client, hass_read_only_access_token):
    lamp = make_entity(hass, "light", "lamp")
    await setup(hass, [dash_rule({"entities": [lamp]}, audience=["non-admins"])])
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json({"id": 1, "type": "propsense/dashboard/resolve", "dashboard": "guest-panel"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["sections"][0]["groups"][0]["entities"] == [lamp]
