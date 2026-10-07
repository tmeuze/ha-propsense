"""Shared fixtures: load the custom integration and make the debounce instant."""
from datetime import timedelta

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def instant_debounce(monkeypatch):
    monkeypatch.setattr("custom_components.propsense.manager.DEBOUNCE_SECONDS", 0.0)


async def settle(hass: HomeAssistant) -> None:
    """Let debounced work run and finish."""
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()


@pytest.fixture(autouse=True)
async def core_homeassistant(hass: HomeAssistant):
    """A running install always has the core integration (it stores exposure)."""
    assert await async_setup_component(hass, "homeassistant", {})
