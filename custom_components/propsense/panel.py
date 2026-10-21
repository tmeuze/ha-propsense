"""The PropSense sidebar panel: a custom panel (admin only) served from this integration."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PANEL_URL_PATH = "propsense"
_STATIC_URL = f"/{DOMAIN}_static"
_FRONTEND_DIR = Path(__file__).parent / "frontend"
_BUNDLE = "propsense-panel.js"
_STATIC_KEY = f"{DOMAIN}_static_registered"


async def async_register_panel(hass: HomeAssistant) -> None:
    if not hass.data.get(_STATIC_KEY):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(_STATIC_URL, str(_FRONTEND_DIR), cache_headers=False)]
        )
        hass.data[_STATIC_KEY] = True

    bundle = _FRONTEND_DIR / _BUNDLE
    # The mtime busts the browser cache when a new release ships a new bundle.
    version = int(bundle.stat().st_mtime) if bundle.exists() else 0
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="propsense-panel",
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{_STATIC_URL}/{_BUNDLE}?v={version}",
        sidebar_title="PropSense",
        sidebar_icon="mdi:tag-multiple",
        require_admin=True,
        config={},
    )


def async_remove_panel(hass: HomeAssistant) -> None:
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
