"""Extension API: let other integrations register PropSense action types.

A provider (for example ha-unity's "grant to child instance") declares
``dependencies: ["propsense"]`` and registers an :class:`ActionType` during its
own setup::

    from custom_components.propsense.api import ActionType, async_register_action

    unregister = async_register_action(hass, MyAction())

PropSense does the rest: it evaluates the rules, works out per target which
entities were added or removed, and calls the provider. Providers never see
rules, selectors or the registries.

Third-party action types stay dormant until the user turns on "Allow
third-party actions" in PropSense's options. Rules that name an unregistered
type are kept and reported as dormant; a missing provider never causes
removals.

``API_VERSION`` is bumped on breaking changes.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

import voluptuous as vol

from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .engine import ActionSpec

API_VERSION = 1

_REGISTRY_KEY = f"{DOMAIN}_actions"


class ActionType:
    """Base class for an action type. Subclass and register it.

    ``mode = "state"``: PropSense keeps each target equal to the selection.
    ``async_current`` reports what the target has now, and ``async_apply``
    receives the difference. Unselected entities are removed.

    ``mode = "edge"``: PropSense calls ``async_apply`` when entities enter
    (``add``) or leave (``remove``) a target's selection. The first time a
    target is seen it only records the selection and fires nothing.
    """

    type_id: str = ""
    name: str = ""
    mode: Literal["state", "edge"] = "state"
    respects_blocked_domains: bool = True
    # True for actions that send data off this instance. They stay dormant until
    # the user allows that in PropSense's settings.
    needs_external_data: bool = False

    def size_limit(self, target: str, settings: Any) -> int:
        """Most entities one target may hold before PropSense refuses (0 = no limit)."""
        return settings.max_exposed

    def config_schema(self) -> vol.Schema:
        """Schema of this action's config; also drives the rule editor form."""
        return vol.Schema({})

    def validate(self, config: dict[str, Any]) -> None:
        """Raise ``vol.Invalid`` if a config the schema accepts makes no sense."""

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        """The targets (assistants, child instances, ...) this config addresses."""
        raise NotImplementedError

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        """Return a reason if ``entity_id`` can't be part of this action's targets."""
        return None

    async def async_start(self) -> None:
        """Called when PropSense starts (built-in providers only). Resume timers here."""

    async def async_stop(self) -> None:
        """Called when PropSense stops or reloads (built-in providers only)."""

    def status(self) -> dict[str, Any]:
        """Optional runtime state for the panel's Status page (JSON-serialisable)."""
        return {}

    async def async_sync(self, target: str) -> None:
        """Called after each applied run for a state target, changed or not.

        For housekeeping that should hold even when nothing changed.
        """

    def target_label(self, target: str) -> str:
        return target

    async def async_current(self, target: str) -> set[str]:
        """Entity ids the target has right now (state mode)."""
        return set()

    async def async_apply(
        self, target: str, add: set[str], remove: set[str]
    ) -> None:
        raise NotImplementedError

    def spec(self) -> ActionSpec:
        return ActionSpec(
            type_id=self.type_id,
            targets=self.targets,
            mode=self.mode,
            respects_blocked_domains=self.respects_blocked_domains,
            accepts=self.accepts,
        )


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, ActionType] = {}
        self._builtin: set[str] = set()
        self._listeners: list[Callable[[], None]] = []

    def get(self, type_id: str) -> ActionType | None:
        return self._actions.get(type_id)

    def is_builtin(self, type_id: str) -> bool:
        return type_id in self._builtin

    @property
    def types(self) -> dict[str, ActionType]:
        return dict(self._actions)

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Call ``listener`` whenever a type is registered or removed."""
        self._listeners.append(listener)

        def remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove

    @callback
    def register(self, action: ActionType, *, builtin: bool = False) -> Callable[[], None]:
        if not action.type_id:
            raise ValueError("ActionType.type_id must be set")
        if action.type_id in self._actions:
            raise ValueError(f"Action type {action.type_id!r} is already registered")
        self._actions[action.type_id] = action
        if builtin:
            self._builtin.add(action.type_id)
        self._notify()

        def unregister() -> None:
            if self._actions.get(action.type_id) is action:
                del self._actions[action.type_id]
                self._builtin.discard(action.type_id)
                self._notify()

        return unregister

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()


@callback
def async_get_registry(hass: HomeAssistant) -> ActionRegistry:
    registry = hass.data.get(_REGISTRY_KEY)
    if registry is None:
        registry = hass.data[_REGISTRY_KEY] = ActionRegistry()
    return registry


@callback
def async_register_action(hass: HomeAssistant, action: ActionType) -> Callable[[], None]:
    """Register an action type; returns a function that unregisters it."""
    return async_get_registry(hass).register(action)
