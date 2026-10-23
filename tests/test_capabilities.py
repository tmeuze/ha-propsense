"""Capability tags read from entity state."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.cover import CoverEntityFeature
from homeassistant.components.fan import FanEntityFeature

from custom_components.propsense.snapshot import capabilities_of


def tags(hass, entity_id, state="on", **attrs):
    hass.states.async_set(entity_id, state, attrs)
    return capabilities_of(hass, entity_id)


def test_light_tags(hass):
    assert tags(hass, "light.a", supported_color_modes=["onoff"]) == {"onoff"}
    assert tags(hass, "light.b", supported_color_modes=["brightness"]) == {"brightness"}
    assert tags(hass, "light.c", supported_color_modes=["color_temp", "hs"]) == {
        "brightness",
        "color_temp",
        "color",
    }
    assert tags(hass, "light.d", supported_color_modes=["rgbww"]) == {
        "brightness",
        "color",
        "white",
    }


def test_cover_tags(hass):
    assert tags(hass, "cover.a", supported_features=CoverEntityFeature.OPEN) == set()
    both = CoverEntityFeature.SET_POSITION | CoverEntityFeature.SET_TILT_POSITION
    assert tags(hass, "cover.b", supported_features=int(both)) == {"position", "tilt"}


def test_fan_tags(hass):
    features = FanEntityFeature.SET_SPEED | FanEntityFeature.OSCILLATE
    assert tags(hass, "fan.a", supported_features=int(features)) == {"speed", "oscillate"}
    assert tags(hass, "fan.b", supported_features=int(FanEntityFeature.PRESET_MODE)) == {"preset"}


def test_climate_tags(hass):
    assert tags(
        hass,
        "climate.a",
        state="heat",
        hvac_modes=["off", "heat", "cool"],
        supported_features=int(ClimateEntityFeature.TARGET_TEMPERATURE),
    ) == {"heat", "cool", "target_temp"}
    assert tags(hass, "climate.b", state="off", hvac_modes=["off"]) == set()


def test_other_domains_and_missing_state_have_none(hass):
    assert tags(hass, "switch.a", supported_features=3) == set()
    assert capabilities_of(hass, "light.nope") == set()
