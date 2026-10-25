"""Registry-derived facts for the integration, manufacturer, category, name and label-name selectors."""
from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import EntityCategory
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    label_registry as lr,
)

from custom_components.propsense.engine import Settings
from custom_components.propsense.snapshot import build_facts

from .test_integration import exposed, setup


def facts_for(hass):
    return {f.entity_id: f for f in build_facts(hass, Settings(), set())}


async def test_facts_carry_integration_device_category_name_and_label_names(hass):
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={("test", "d1")},
        manufacturer="IKEA",
        model="TRADFRI bulb",
    )
    label = lr.async_get(hass).async_create("Expose: Novak")
    dr.async_get(hass).async_update_device(device.id, labels={label.label_id})
    reg = er.async_get(hass)
    lamp = reg.async_get_or_create(
        "light", "hue", "1", suggested_object_id="lamp", device_id=device.id,
        original_name="Reading lamp",
    )
    diag = reg.async_get_or_create(
        "sensor", "hue", "2", suggested_object_id="lamp_rssi", device_id=device.id,
        entity_category=EntityCategory.DIAGNOSTIC,
    )

    facts = facts_for(hass)
    f = facts[lamp.entity_id]
    assert (f.integration, f.manufacturer, f.model) == ("hue", "IKEA", "TRADFRI bulb")
    assert f.entity_category == "primary"
    assert f.name == "Reading lamp"
    assert f.label_names == {"Expose: Novak"}  # inherited from the device
    assert facts[diag.entity_id].entity_category == "diagnostic"


async def test_state_only_entities_get_their_friendly_name(hass):
    hass.states.async_set("sensor.virtual", "1", {"friendly_name": "Virtual thing"})
    f = facts_for(hass)["sensor.virtual"]
    assert f.name == "Virtual thing" and f.integration is None


async def test_rule_exposes_by_label_wildcard_and_integration(hass):
    reg = er.async_get(hass)
    labels = lr.async_get(hass)
    novak = labels.async_create("Expose: Novak").label_id
    alexa = labels.async_create("Expose: Alexa").label_id
    other = labels.async_create("Needs battery").label_id
    a = reg.async_get_or_create("light", "hue", "a", suggested_object_id="a").entity_id
    b = reg.async_get_or_create("light", "hue", "b", suggested_object_id="b").entity_id
    c = reg.async_get_or_create("light", "hue", "c", suggested_object_id="c").entity_id
    for entity_id, label in ((a, novak), (b, alexa), (c, other)):
        reg.async_update_entity(entity_id, labels={label})
        hass.states.async_set(entity_id, "on")

    await setup(
        hass,
        [
            {
                "id": "r",
                "name": "Any Expose label",
                "include": {"label_patterns": ["expose: *"], "integrations": ["hue"]},
                "actions": [{"type": "expose", "config": {"assistants": ["conversation"]}}],
            }
        ],
    )
    assert exposed(hass) == {a, b}
