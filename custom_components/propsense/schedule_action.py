"""Built-in action: turn entities on or off on a timer or a schedule.

Three triggers, one effect (turn the selected entities on or off):

* ``state_for``: after an entity has been on (or off) for a duration. This is
  an auto-off timer. It watches the entity's *state*, so it doesn't matter
  whether it was switched in Home Assistant or on the wall. Deadlines are
  stored as absolute times, so a restart doesn't lose or reset them, and the
  entity's state is checked again before acting.
* ``time``: at a time of day, optionally only on some weekdays.
* ``sun``: at sunrise or sunset, with an offset.

The rule selects the entities. PropSense hands this action the governed set
per target (a target is one canonical trigger-and-effect configuration), and
this module keeps the timers.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

import voluptuous as vol

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_state_change_event,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.sun import get_astral_event_date, get_astral_event_next
from homeassistant.util import dt as dt_util

from .api import ActionType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCHEDULE = "schedule"
TRIGGERS = ["state_for", "time", "sun"]
EFFECTS = ["turn_on", "turn_off"]
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
# Domains that have turn_on and turn_off, so the effect can be applied to them.
SUPPORTED_DOMAINS = (
    "light",
    "switch",
    "fan",
    "input_boolean",
    "humidifier",
    "media_player",
    "climate",
    "remote",
    "siren",
    "water_heater",
)
_SAVE_DELAY = 1.0
_INACTIVE = ("off", "unavailable", "unknown")


# ----------------------------------------------------------------- config


def _seconds(value: Any) -> int:
    if isinstance(value, dict):
        return int(
            int(value.get("days", 0)) * 86400
            + int(value.get("hours", 0)) * 3600
            + int(value.get("minutes", 0)) * 60
            + int(value.get("seconds", 0))
        )
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def normalise(config: dict[str, Any]) -> dict[str, Any]:
    """The part of a config that matters for its trigger, in canonical form."""
    trigger = config.get("trigger") or "state_for"
    out: dict[str, Any] = {
        "trigger": trigger,
        "do": config.get("do") or "turn_off",
    }
    if trigger == "state_for":
        out["state"] = config.get("state") or "on"
        out["seconds"] = _seconds(config.get("duration"))
    else:
        out["days"] = sorted(config.get("days") or [], key=WEEKDAYS.index)
        out["catch_up"] = int(config.get("catch_up_minutes") or 0)
        if trigger == "time":
            out["at"] = str(config.get("at") or "")[:8]
        else:
            out["event"] = config.get("event") or "sunset"
            out["offset"] = int(config.get("offset_minutes") or 0)
    return out


def _duration_text(seconds: int) -> str:
    parts = []
    for unit, size in (("d", 86400), ("h", 3600), ("min", 60), ("s", 1)):
        if seconds >= size:
            parts.append(f"{seconds // size}{unit}")
            seconds %= size
    return " ".join(parts) or "0s"


def describe(cfg: dict[str, Any]) -> str:
    verb = "Turn on" if cfg["do"] == "turn_on" else "Turn off"
    if cfg["trigger"] == "state_for":
        return f"{verb} after being {cfg['state']} for {_duration_text(cfg['seconds'])}"
    days = f" on {', '.join(cfg['days'])}" if cfg["days"] else ""
    if cfg["trigger"] == "time":
        return f"{verb} at {cfg['at']}{days}"
    off = cfg["offset"]
    shift = f" {'+' if off > 0 else '-'}{abs(off)} min" if off else ""
    return f"{verb} at {cfg['event']}{shift}{days}"


# --------------------------------------------------------------- provider


class ScheduleAction(ActionType):
    type_id = SCHEDULE
    name = "Turn on or off on a timer or schedule"
    mode = "state"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.schedule")
        # target -> entity ids governed by it
        self._governed: dict[str, set[str]] = {}
        # target -> entity id -> deadline (ISO, UTC)
        self._deadlines: dict[str, dict[str, str]] = {}
        # target -> when a time/sun trigger last ran (ISO, UTC)
        self._last_fired: dict[str, str] = {}
        self._timer_unsubs: dict[tuple[str, str], Callable[[], None]] = {}
        self._sched_unsubs: dict[str, Callable[[], None]] = {}
        self._state_unsub: Callable[[], None] | None = None
        self._running = False
        self._started_listener: Callable[[], None] | None = None
        # Set by the manager: True while dry run is on, so nothing fires.
        self.is_dry_run: Callable[[], bool] = lambda: False

    # ------------------------------------------------------------- schema

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("trigger", default="state_for"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=TRIGGERS, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Required("do", default="turn_off"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=EFFECTS, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional("state", default="on"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["on", "off"], mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional("duration"): selector.DurationSelector(),
                vol.Optional("at"): selector.TimeSelector(),
                vol.Optional("event", default="sunset"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["sunrise", "sunset"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("offset_minutes", default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=-720, max=720, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Optional("days"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=WEEKDAYS, multiple=True)
                ),
                vol.Optional("catch_up_minutes", default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=720, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

    def validate(self, config: dict[str, Any]) -> None:
        cfg = normalise(config)
        if cfg["trigger"] == "state_for":
            if cfg["seconds"] <= 0:
                raise vol.Invalid("Choose how long the entity must stay in that state")
            ends_on = cfg["state"] == "on" and cfg["do"] == "turn_on"
            ends_off = cfg["state"] == "off" and cfg["do"] == "turn_off"
            if ends_on or ends_off:
                raise vol.Invalid(
                    f"Nothing to do: the entity is already {cfg['state']} when the timer ends"
                )
        elif cfg["trigger"] == "time":
            try:
                datetime.strptime(cfg["at"], "%H:%M:%S")
            except ValueError as err:
                raise vol.Invalid("Choose a time of day") from err

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        return frozenset({json.dumps(normalise(config), sort_keys=True)})

    def target_label(self, target: str) -> str:
        try:
            return describe(json.loads(target))
        except (ValueError, KeyError):
            return target

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        domain = entity_id.split(".", 1)[0]
        if domain not in SUPPORTED_DOMAINS:
            return f"domain '{domain}' can't be turned on or off"
        return None

    # -------------------------------------------------------- persistence

    async def async_start(self) -> None:
        if self._running:
            return
        self._running = True
        saved = await self._store.async_load() or {}
        self._governed = {t: set(v) for t, v in saved.get("governed", {}).items()}
        self._deadlines = saved.get("deadlines", {})
        self._last_fired = saved.get("last_fired", {})
        if self._hass.is_running:
            self._resume()
        else:
            self._started_listener = self._hass.bus.async_listen_once(
                "homeassistant_started", lambda _e: self._resume()
            )

    async def async_stop(self) -> None:
        self._running = False
        if self._started_listener:
            self._started_listener()
            self._started_listener = None
        self._cancel_everything()
        await self._store.async_save(self._snapshot())

    def _snapshot(self) -> dict[str, Any]:
        return {
            "governed": {t: sorted(v) for t, v in self._governed.items()},
            "deadlines": self._deadlines,
            "last_fired": self._last_fired,
        }

    def _save(self) -> None:
        self._store.async_delay_save(self._snapshot, _SAVE_DELAY)

    def _cancel_everything(self) -> None:
        for unsub in [*self._timer_unsubs.values(), *self._sched_unsubs.values()]:
            unsub()
        self._timer_unsubs.clear()
        self._sched_unsubs.clear()
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None

    # ---------------------------------------------------------- reconcile

    async def async_current(self, target: str) -> set[str]:
        return set(self._governed.get(target, set()))

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        members = self._governed.setdefault(target, set())
        members |= add
        members -= remove
        for entity_id in remove:
            self._drop_timer(target, entity_id)
        if not members:
            self._governed.pop(target, None)
            self._deadlines.pop(target, None)
            self._last_fired.pop(target, None)
            self._disarm(target)
        self._save()
        if self._running and self._hass.is_running:
            self._resume(only=target, entities=add)

    # -------------------------------------------------------------- resume

    @callback
    def _resume(self, only: str | None = None, entities: set[str] | None = None) -> None:
        """Bring timers and schedules in line with the governed sets.

        Called at start-up and whenever a target's members change.
        """
        self._track_states()
        now = dt_util.utcnow()
        for target, members in self._governed.items():
            if only is not None and target != only:
                continue
            cfg = json.loads(target)
            if cfg["trigger"] == "state_for":
                for entity_id in sorted(members if entities is None else entities & members):
                    self._reconcile_timer(target, cfg, entity_id, now)
            else:
                if target not in self._sched_unsubs:
                    self._catch_up(target, cfg, now)
                    self._arm(target, cfg)

    @callback
    def _track_states(self) -> None:
        if self._state_unsub:
            self._state_unsub()
            self._state_unsub = None
        watched = {
            e
            for target, members in self._governed.items()
            if json.loads(target)["trigger"] == "state_for"
            for e in members
        }
        if watched:
            self._state_unsub = async_track_state_change_event(
                self._hass, sorted(watched), self._on_state_event
            )

    # ------------------------------------------------------ state_for timers

    @staticmethod
    def _matches(cfg: dict[str, Any], state: str | None) -> bool | None:
        """True if in the watched state, False if in the opposite one, None if unknown."""
        if state is None or state in ("unavailable", "unknown"):
            return None
        is_off = state == "off"
        return is_off if cfg["state"] == "off" else not is_off

    @callback
    def _on_state_event(self, event: Event) -> None:
        entity_id = event.data["entity_id"]
        new = event.data.get("new_state")
        now = dt_util.utcnow()
        for target, members in self._governed.items():
            if entity_id not in members:
                continue
            cfg = json.loads(target)
            if cfg["trigger"] == "state_for":
                self._reconcile_timer(target, cfg, entity_id, now, new.state if new else None)

    @callback
    def _reconcile_timer(
        self,
        target: str,
        cfg: dict[str, Any],
        entity_id: str,
        now: datetime,
        state: str | None = None,
    ) -> None:
        if state is None:
            current = self._hass.states.get(entity_id)
            state = current.state if current else None
        matches = self._matches(cfg, state)
        deadline = self._deadlines.get(target, {}).get(entity_id)

        if matches is False:
            self._drop_timer(target, entity_id)
        elif matches is True:
            if deadline is None:
                due = now + timedelta(seconds=cfg["seconds"])
                self._deadlines.setdefault(target, {})[entity_id] = due.isoformat()
                self._save()
                self._schedule_timer(target, entity_id, due)
            else:
                self._schedule_timer(target, entity_id, dt_util.parse_datetime(deadline) or now)
        elif deadline is not None and (target, entity_id) not in self._timer_unsubs:
            # Unavailable right now: keep the deadline and act when it is due.
            self._schedule_timer(target, entity_id, dt_util.parse_datetime(deadline) or now)

    @callback
    def _schedule_timer(self, target: str, entity_id: str, due: datetime) -> None:
        key = (target, entity_id)
        if (old := self._timer_unsubs.pop(key, None)) is not None:
            old()

        @callback
        def _fire(_now: datetime) -> None:
            self._timer_unsubs.pop(key, None)
            self._timer_due(target, entity_id)

        self._timer_unsubs[key] = async_track_point_in_utc_time(self._hass, _fire, max(due, dt_util.utcnow()))

    @callback
    def _drop_timer(self, target: str, entity_id: str) -> None:
        if (unsub := self._timer_unsubs.pop((target, entity_id), None)) is not None:
            unsub()
        if self._deadlines.get(target, {}).pop(entity_id, None) is not None:
            self._save()

    @callback
    def _timer_due(self, target: str, entity_id: str) -> None:
        cfg = json.loads(target)
        state = self._hass.states.get(entity_id)
        matches = self._matches(cfg, state.state if state else None)
        if matches is None:
            # unavailable: try again when it reports (see _reconcile_timer)
            return
        self._drop_timer(target, entity_id)
        if matches:  # still in the watched state, so the timer applies
            self._hass.async_create_task(self._run(cfg, [entity_id], "timer"))

    # ----------------------------------------------------- time / sun triggers

    def _occurrence(self, cfg: dict[str, Any], day: date) -> datetime | None:
        """The trigger's moment on a local calendar day, in UTC (None if not that day)."""
        if cfg["days"] and WEEKDAYS[day.weekday()] not in cfg["days"]:
            return None
        if cfg["trigger"] == "time":
            hh, mm, ss = (int(p) for p in cfg["at"].split(":"))
            local = datetime(day.year, day.month, day.day, hh, mm, ss, tzinfo=dt_util.get_default_time_zone())
            return dt_util.as_utc(local)
        event = get_astral_event_date(self._hass, cfg["event"], day)
        return event + timedelta(minutes=cfg["offset"]) if event else None

    def _next(self, cfg: dict[str, Any], after: datetime) -> datetime | None:
        today = dt_util.as_local(after).date()
        for delta in range(0, 9):
            moment = self._occurrence(cfg, today + timedelta(days=delta))
            if moment is not None and moment > after:
                return moment
        return None

    def _previous(self, cfg: dict[str, Any], before: datetime) -> datetime | None:
        today = dt_util.as_local(before).date()
        for delta in range(0, 9):
            moment = self._occurrence(cfg, today - timedelta(days=delta))
            if moment is not None and moment <= before:
                return moment
        return None

    @callback
    def _arm(self, target: str, cfg: dict[str, Any]) -> None:
        due = self._next(cfg, dt_util.utcnow())
        if due is None:
            return

        @callback
        def _fire(_now: datetime) -> None:
            self._sched_unsubs.pop(target, None)
            self._last_fired[target] = dt_util.utcnow().isoformat()
            self._save()
            members = sorted(self._governed.get(target, ()))
            if members:
                self._hass.async_create_task(self._run(cfg, members, "schedule"))
            self._arm(target, cfg)

        self._sched_unsubs[target] = async_track_point_in_utc_time(self._hass, _fire, due)

    @callback
    def _disarm(self, target: str) -> None:
        if (unsub := self._sched_unsubs.pop(target, None)) is not None:
            unsub()

    @callback
    def _catch_up(self, target: str, cfg: dict[str, Any], now: datetime) -> None:
        """Run a trigger missed while Home Assistant was down, if allowed."""
        grace = cfg["catch_up"]
        if not grace:
            return
        prev = self._previous(cfg, now)
        if prev is None or now - prev > timedelta(minutes=grace):
            return
        last = dt_util.parse_datetime(self._last_fired.get(target, ""))
        if last is not None and last >= prev:
            return
        self._last_fired[target] = now.isoformat()
        self._save()
        self._hass.async_create_task(self._run(cfg, sorted(self._governed.get(target, ())), "catch-up"))

    # ------------------------------------------------------------- effect

    async def _run(self, cfg: dict[str, Any], entity_ids: list[str], why: str) -> None:
        if self.is_dry_run():
            _LOGGER.info("PropSense dry run: would %s %s (%s)", cfg["do"], entity_ids, why)
            return
        want_on = cfg["do"] == "turn_on"
        todo = []
        for entity_id in entity_ids:
            state = self._hass.states.get(entity_id)
            if state is None or state.state in ("unavailable", "unknown"):
                continue
            if (state.state != "off") == want_on:
                continue  # already as wanted
            todo.append(entity_id)
        if not todo:
            return
        _LOGGER.info("PropSense %s: %s %s", why, cfg["do"], todo)
        try:
            await self._hass.services.async_call(
                "homeassistant", cfg["do"], {"entity_id": todo}, blocking=True
            )
        except Exception:  # one failing device must not stop the rest
            _LOGGER.exception("PropSense could not %s %s", cfg["do"], todo)

    # ------------------------------------------------------------- status

    def status(self) -> dict[str, Any]:
        out = []
        for target, members in sorted(self._governed.items()):
            cfg = json.loads(target)
            item: dict[str, Any] = {
                "label": describe(cfg),
                "trigger": cfg["trigger"],
                "entities": sorted(members),
            }
            if cfg["trigger"] == "state_for":
                item["timers"] = [
                    {"entity_id": e, "due": d}
                    for e, d in sorted(self._deadlines.get(target, {}).items())
                ]
            else:
                nxt = self._next(cfg, dt_util.utcnow())
                item["next"] = nxt.isoformat() if nxt else None
            out.append(item)
        return {"schedules": out}
