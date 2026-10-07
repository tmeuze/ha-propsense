"""Run the integration inside Home Assistant's test harness, with real registries."""
from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.homeassistant.exposed_entities import (
    async_expose_entity,
    async_get_assistant_settings,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    floor_registry as fr,
    issue_registry as ir,
    label_registry as lr,
)

from custom_components.propsense.const import DOMAIN

from .conftest import settle

ASSIST = "conversation"


def exposed(hass: HomeAssistant, assistant: str = ASSIST) -> set[str]:
    return {
        e
        for e, o in async_get_assistant_settings(hass, assistant).items()
        if o.get("should_expose")
    }


def make_entity(hass, domain, name, *, labels=(), area_id=None, device_id=None):
    reg = er.async_get(hass)
    entry = reg.async_get_or_create(
        domain, "test", name, suggested_object_id=name, device_id=device_id
    )
    reg.async_update_entity(entry.entity_id, labels=set(labels), area_id=area_id)
    hass.states.async_set(entry.entity_id, "on")
    return entry.entity_id


def rule(rid="r1", include=None, exclude=None, assistants=None, enabled=True):
    return {
        "id": rid,
        "name": f"Rule {rid}",
        "enabled": enabled,
        "include": include or {},
        "exclude": exclude or {},
        "assistants": assistants or [ASSIST],
    }


async def setup(hass: HomeAssistant, rules, settings=None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={"rules": rules, "settings": settings or {}},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass)
    return entry


@pytest.fixture
def label(hass: HomeAssistant):
    return lr.async_get(hass).async_create("Expose: Novak").label_id


async def test_label_rule_exposes_and_manual_exposure_is_overridden(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    other = make_entity(hass, "light", "other")
    # someone ticked this by hand in Settings; the rules are the source of truth
    async_expose_entity(hass, ASSIST, other, True)
    assert other in exposed(hass)

    await setup(hass, [rule(include={"labels": [label]})])

    assert exposed(hass) == {kitchen}


async def test_removing_the_label_unexposes(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    await setup(hass, [rule(include={"labels": [label]})])
    assert exposed(hass) == {kitchen}

    er.async_get(hass).async_update_entity(kitchen, labels=set())
    await settle(hass)
    assert exposed(hass) == set()


async def test_adding_the_label_exposes_without_a_restart(hass, label):
    kitchen = make_entity(hass, "light", "kitchen")
    await setup(hass, [rule(include={"labels": [label]})])
    assert exposed(hass) == set()

    er.async_get(hass).async_update_entity(kitchen, labels={label})
    await settle(hass)
    assert exposed(hass) == {kitchen}


async def test_device_label_is_inherited(hass, label):
    dev_entry = MockConfigEntry(domain="test")
    dev_entry.add_to_hass(hass)
    dev = dr.async_get(hass).async_get_or_create(
        config_entry_id=dev_entry.entry_id, identifiers={("test", "d1")}
    )
    dr.async_get(hass).async_update_device(dev.id, labels={label})
    lamp = make_entity(hass, "light", "lamp", device_id=dev.id)

    await setup(hass, [rule(include={"labels": [label]})])
    assert exposed(hass) == {lamp}


async def test_label_and_floor_are_anded(hass, label):
    floor1 = fr.async_get(hass).async_create("Level 1")
    floor2 = fr.async_get(hass).async_create("Level 2")
    a1 = ar.async_get(hass).async_create("Kitchen", floor_id=floor1.floor_id)
    a2 = ar.async_get(hass).async_create("Bedroom", floor_id=floor2.floor_id)
    kitchen = make_entity(hass, "light", "kitchen", labels=[label], area_id=a1.id)
    make_entity(hass, "light", "bedroom", labels=[label], area_id=a2.id)

    await setup(
        hass, [rule(include={"labels": [label], "floors": [floor1.floor_id]})]
    )
    assert exposed(hass) == {kitchen}


async def test_blocked_domain_is_never_exposed(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    make_entity(hass, "lock", "front", labels=[label])

    await setup(hass, [rule(include={"labels": [label]})])
    assert exposed(hass) == {lamp}


async def test_over_the_limit_changes_nothing_and_raises_a_repair(hass, label):
    ids = [make_entity(hass, "light", f"l{i}", labels=[label]) for i in range(5)]
    keep = make_entity(hass, "light", "keep")
    async_expose_entity(hass, ASSIST, keep, True)

    await setup(
        hass, [rule(include={"labels": [label]})], settings={"max_exposed": 3}
    )

    assert exposed(hass) == {keep}  # untouched
    issue = ir.async_get(hass).async_get_issue(DOMAIN, f"too_many_exposed_{ASSIST}")
    assert issue is not None
    assert len(ids) == 5


async def test_dry_run_changes_nothing(hass, label):
    make_entity(hass, "light", "kitchen", labels=[label])
    await setup(
        hass, [rule(include={"labels": [label]})], settings={"dry_run": True}
    )
    assert exposed(hass) == set()


async def test_no_rules_unexposes_everything_managed(hass):
    other = make_entity(hass, "light", "other")
    async_expose_entity(hass, ASSIST, other, True)
    await setup(hass, [])
    assert exposed(hass) == set()


async def test_preview_service_reports_without_changing(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    await setup(hass, [rule(include={"labels": [label]})], settings={"dry_run": True})
    assert exposed(hass) == set()

    response = await hass.services.async_call(
        DOMAIN, "preview", {}, blocking=True, return_response=True
    )
    assert response["assistants"][ASSIST]["entities"] == [kitchen]
    assert response["assistants"][ASSIST]["added"] == [kitchen]
    assert exposed(hass) == set()


async def test_resync_service_applies(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    await setup(hass, [rule(include={"labels": [label]})], settings={"dry_run": True})
    assert exposed(hass) == set()
    await hass.services.async_call(DOMAIN, "resync", {"dry_run": False}, blocking=True)
    assert exposed(hass) == {kitchen}


async def test_sensor_reports_count_and_tokens(hass, label):
    make_entity(hass, "light", "kitchen", labels=[label])
    await setup(hass, [rule(include={"labels": [label]})])
    state = hass.states.get("sensor.propsense_exposed_to_assist")
    assert state is not None
    assert state.state == "1"
    assert state.attributes["estimated_tokens"] == 26


async def test_group_membership_selects_members(hass):
    a = make_entity(hass, "light", "a")
    b = make_entity(hass, "light", "b")
    make_entity(hass, "light", "c")
    hass.states.async_set("light.grp", "on", {"entity_id": [a, b]})
    await setup(hass, [rule(include={"groups": ["light.grp"]})])
    assert exposed(hass) == {a, b}


async def test_config_flow_creates_the_single_entry(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY

    again = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert again["type"] is FlowResultType.ABORT


async def test_options_flow_adds_a_rule_that_takes_effect(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    entry = await setup(hass, [])
    assert exposed(hass) == set()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "add_rule"}
    )
    assert result["step_id"] == "rule_include"

    # an empty selection is rejected
    bad = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Novak", "enabled": True, "assistants": [ASSIST]},
    )
    assert bad["type"] is FlowResultType.FORM
    assert bad["errors"] == {"base": "empty_selector"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "name": "Novak",
            "enabled": True,
            "assistants": [ASSIST],
            "include_labels": [label],
        },
    )
    assert result["step_id"] == "rule_exclude"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await settle(hass)

    assert len(entry.options["rules"]) == 1
    assert entry.options["rules"][0]["include"]["labels"] == [label]
    assert exposed(hass) == {kitchen}


async def test_options_flow_toggle_and_delete(hass, label):
    kitchen = make_entity(hass, "light", "kitchen", labels=[label])
    entry = await setup(hass, [rule("r1", include={"labels": [label]})])
    assert exposed(hass) == {kitchen}

    # disable it
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "pick_rule"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"rule": "r1"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "toggle_rule"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await settle(hass)
    assert entry.options["rules"][0]["enabled"] is False
    assert exposed(hass) == set()

    # delete it
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "pick_rule"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"rule": "r1"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "delete_rule"}
    )
    await settle(hass)
    assert entry.options["rules"] == []


async def test_options_flow_preview_shows_summary_and_changes_nothing(hass, label):
    make_entity(hass, "light", "kitchen", labels=[label])
    entry = await setup(hass, [rule(include={"labels": [label]})], settings={"dry_run": True})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "preview"}
    )
    assert result["step_id"] == "preview"
    assert "1 entities" in result["description_placeholders"]["summary"]
    assert exposed(hass) == set()


async def test_settings_roundtrip_through_the_flow(hass, label):
    entry = await setup(hass, [rule(include={"labels": [label]})])
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "settings"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "managed_assistants": [ASSIST],
            "blocked_domains": ["lock"],
            "max_exposed": 42,
            "inherit_device_labels": True,
            "inherit_area_labels": True,
            "dry_run": False,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["settings"]["max_exposed"] == 42
    assert entry.options["settings"]["inherit_area_labels"] is True
    assert entry.options["settings"]["blocked_domains"] == ["lock"]
