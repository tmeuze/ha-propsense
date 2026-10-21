"""The action registry and third-party providers, in the HA test harness."""
from __future__ import annotations

from typing import Any

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, label_registry as lr
from homeassistant.setup import async_setup_component

from custom_components.propsense.api import (
    ActionType,
    async_get_registry,
    async_register_action,
)
from custom_components.propsense.const import DOMAIN

from .conftest import settle
from .test_integration import make_entity, setup


class FakeGrant(ActionType):
    """A stand-in for a provider such as ha-unity's grant action."""

    type_id = "fake.grant"
    name = "Fake grant"

    def __init__(self, mode="state") -> None:
        self.mode = mode
        self.held: dict[str, set[str]] = {}
        self.calls: list[tuple[str, set[str], set[str]]] = []
        self.fail = False

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        return frozenset(config.get("children", []))

    async def async_current(self, target):
        return set(self.held.get(target, set()))

    async def async_apply(self, target, add, remove):
        if self.fail:
            raise RuntimeError("boom")
        self.calls.append((target, set(add), set(remove)))
        self.held.setdefault(target, set()).update(add)
        self.held[target] -= remove


def grant_rule(label, rid="g1", children=("kid1",)):
    return {
        "id": rid,
        "name": f"Grant {rid}",
        "include": {"labels": [label]},
        "actions": [{"type": "fake.grant", "config": {"children": list(children)}}],
    }


async def ensure_loaded(hass: HomeAssistant) -> None:
    assert await async_setup_component(hass, DOMAIN, {})


@pytest.fixture
def label(hass: HomeAssistant):
    return lr.async_get(hass).async_create("Grant: Kid").label_id


async def test_third_party_actions_are_dormant_until_allowed(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    await ensure_loaded(hass)
    provider = FakeGrant()
    async_register_action(hass, provider)

    entry = await setup(hass, [grant_rule(label)], {"allow_third_party_actions": False})
    manager = entry.runtime_data
    assert provider.calls == []
    assert manager.last.dormant == {"g1": ["fake.grant"]}

    hass.config_entries.async_update_entry(
        entry,
        options={
            **entry.options,
            "settings": {"allow_third_party_actions": True},
        },
    )
    await manager.async_apply()
    assert provider.held == {"kid1": {lamp}}
    assert manager.last.dormant == {}


async def test_state_action_adds_and_removes_with_the_label(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    await ensure_loaded(hass)
    provider = FakeGrant()
    async_register_action(hass, provider)
    await setup(hass, [grant_rule(label)], {"allow_third_party_actions": True})
    assert provider.held == {"kid1": {lamp}}

    er.async_get(hass).async_update_entity(lamp, labels=set())
    await settle(hass)
    assert provider.held == {"kid1": set()}


async def test_removing_the_last_rule_revokes(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    await ensure_loaded(hass)
    provider = FakeGrant()
    async_register_action(hass, provider)
    entry = await setup(hass, [grant_rule(label)], {"allow_third_party_actions": True})
    assert provider.held == {"kid1": {lamp}}

    manager = entry.runtime_data
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "rules": []}
    )
    await manager.async_apply()
    assert provider.held == {"kid1": set()}


async def test_missing_provider_never_revokes(hass, label):
    lamp = make_entity(hass, "light", "lamp", labels=[label])
    await ensure_loaded(hass)
    provider = FakeGrant()
    unregister = async_register_action(hass, provider)
    entry = await setup(hass, [grant_rule(label)], {"allow_third_party_actions": True})
    assert provider.held == {"kid1": {lamp}}

    unregister()
    await settle(hass)
    assert provider.held == {"kid1": {lamp}}
    assert entry.runtime_data.last.dormant == {"g1": ["fake.grant"]}


async def test_provider_error_is_contained(hass, label):
    make_entity(hass, "light", "lamp", labels=[label])
    await ensure_loaded(hass)
    provider = FakeGrant()
    provider.fail = True
    async_register_action(hass, provider)
    entry = await setup(hass, [grant_rule(label)], {"allow_third_party_actions": True})
    result = entry.runtime_data.last
    assert result.actions["fake.grant"]["kid1"].error == "boom"
    # built-in exposure still reported
    assert "conversation" in result.assistants


async def test_edge_action_fires_on_enter_and_leave_not_on_first_sight(hass, label):
    existing = make_entity(hass, "light", "existing", labels=[label])
    late = make_entity(hass, "light", "late")
    await ensure_loaded(hass)
    provider = FakeGrant(mode="edge")
    async_register_action(hass, provider)
    await setup(hass, [grant_rule(label)], {"allow_third_party_actions": True})
    assert provider.calls == []  # baseline only

    er.async_get(hass).async_update_entity(late, labels={label})
    await settle(hass)
    assert provider.calls == [("kid1", {late}, set())]

    er.async_get(hass).async_update_entity(existing, labels=set())
    await settle(hass)
    assert provider.calls[-1] == ("kid1", set(), {existing})


async def test_duplicate_registration_is_rejected(hass):
    await ensure_loaded(hass)
    async_register_action(hass, FakeGrant())
    with pytest.raises(ValueError):
        async_register_action(hass, FakeGrant())
    assert "expose" in async_get_registry(hass).types
