"""Built-in action: ship the numeric history of selected entities as metrics.

Matching entities are listened to individually (never the whole event bus) and
their numeric states are sent, in the InfluxDB line protocol, to the one URL in
PropSense's settings (a VictoriaMetrics ``/write`` endpoint). Nothing is sent
anywhere else, and nothing is sent at all until the user allows data to leave
the instance. There are no credentials: the endpoint is expected to accept
posts from this network only.

Load is bounded three ways: each entity emits at most one point per
``min_interval_seconds`` (the latest value wins), points are posted in batches
every ``FLUSH_SECONDS``, and a rule may select at most ``max_entities``.

If the endpoint is unreachable, points wait in a bounded in-memory buffer and
the oldest are dropped when it is full. The buffer is not saved: a restart
loses what had not been sent yet (at most one flush window plus any outage).
"""
from __future__ import annotations

import json
import logging
import math
import time
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    selector,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .api import ActionType
from .engine import DEFAULT_METRICS_URL, Settings

_LOGGER = logging.getLogger(__name__)

METRICS = "metrics"
MEASUREMENT = "homeassistant"
FLUSH_SECONDS = 30
BATCH_LINES = 1000
BUFFER_POINTS = 5000  # about ten minutes for 200 entities at one point a minute
REQUEST_TIMEOUT = 10
DEFAULT_INTERVAL = 60
DEFAULT_MAX_ENTITIES = 200
HARD_MAX_ENTITIES = 1000
_NUMERIC_DOMAINS = ("sensor", "number", "input_number", "counter")
_BOOLEAN_DOMAINS = ("binary_sensor", "switch", "light", "fan", "input_boolean")
_BOOLEAN_STATES = {"on": 1.0, "off": 0.0}


# ----------------------------------------------------------------- config


def normalise(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "booleans": bool(config.get("include_booleans", False)),
        "interval": int(config.get("min_interval_seconds") or DEFAULT_INTERVAL),
        "area": bool(config.get("tag_area", True)),
        "device_class": bool(config.get("tag_device_class", True)),
        "unit": bool(config.get("tag_unit", True)),
        "max": int(config.get("max_entities") or DEFAULT_MAX_ENTITIES),
    }


def describe(cfg: dict[str, Any]) -> str:
    extra = " (with on/off as 0/1)" if cfg["booleans"] else ""
    return (
        f"Ship numeric history, at most one point per {cfg['interval']} s "
        f"for up to {cfg['max']} entities{extra}"
    )


# ------------------------------------------------------------ line protocol


def _escape_tag(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(" ", "\\ ")
        .replace("=", "\\=")
        .replace("\n", " ")
    )


def line(tags: dict[str, str], value: float, when: datetime) -> str:
    """One InfluxDB line: measurement, sorted tags, ``value`` field, ns timestamp."""
    tag_text = ",".join(
        f"{_escape_tag(k)}={_escape_tag(v)}" for k, v in sorted(tags.items()) if v
    )
    ns = int(when.timestamp() * 1_000_000_000)
    return f"{MEASUREMENT},{tag_text} value={value!r} {ns}"


def numeric(state: str | None, *, booleans: bool) -> float | None:
    """The state as a number, or None if it isn't one (or isn't wanted)."""
    if state is None or state in (STATE_UNAVAILABLE, STATE_UNKNOWN, ""):
        return None
    if booleans and state in _BOOLEAN_STATES:
        return _BOOLEAN_STATES[state]
    try:
        value = float(state)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


# --------------------------------------------------------------- provider


class MetricsAction(ActionType):
    type_id = METRICS
    name = "Ship numeric history to a metrics endpoint"
    mode = "state"
    needs_external_data = True

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._governed: dict[str, set[str]] = {}
        self._unsub_states: Callable[[], None] | None = None
        self._unsub_flush: Callable[[], None] | None = None
        self._running = False
        # entity id -> monotonic time of its last emitted point
        self._last_emit: dict[str, float] = {}
        # entity id -> (value, when) held back by the minimum interval
        self._deferred: dict[str, tuple[float, datetime, str]] = {}
        self._buffer: deque[str] = deque(maxlen=BUFFER_POINTS)
        self.sent = 0
        self.dropped = 0
        self.last_error: str | None = None
        self.last_success: str | None = None
        # Set by the manager.
        self.is_dry_run: Callable[[], bool] = lambda: False
        self.get_settings: Callable[[], Settings] = Settings

    # ------------------------------------------------------------- schema

    def config_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional("min_interval_seconds", default=DEFAULT_INTERVAL): (
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10, max=3600, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    )
                ),
                vol.Optional("include_booleans", default=False): selector.BooleanSelector(),
                vol.Optional("tag_area", default=True): selector.BooleanSelector(),
                vol.Optional("tag_device_class", default=True): selector.BooleanSelector(),
                vol.Optional("tag_unit", default=True): selector.BooleanSelector(),
                vol.Optional("max_entities", default=DEFAULT_MAX_ENTITIES): (
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=HARD_MAX_ENTITIES,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    )
                ),
            }
        )

    def validate(self, config: dict[str, Any]) -> None:
        cfg = normalise(config)
        if not 10 <= cfg["interval"] <= 3600:
            raise vol.Invalid("The minimum interval must be between 10 and 3600 seconds")
        if not 1 <= cfg["max"] <= HARD_MAX_ENTITIES:
            raise vol.Invalid(f"The entity cap must be between 1 and {HARD_MAX_ENTITIES}")

    def targets(self, config: dict[str, Any]) -> frozenset[str]:
        return frozenset({json.dumps(normalise(config), sort_keys=True)})

    def target_label(self, target: str) -> str:
        try:
            return describe(json.loads(target))
        except (ValueError, KeyError):
            return target

    def size_limit(self, target: str, settings: Any) -> int:
        try:
            return int(json.loads(target)["max"])
        except (ValueError, KeyError):
            return DEFAULT_MAX_ENTITIES

    def accepts(self, config: dict[str, Any], entity_id: str) -> str | None:
        domain = entity_id.split(".", 1)[0]
        if domain in _NUMERIC_DOMAINS:
            return None
        if domain in _BOOLEAN_DOMAINS:
            if config.get("include_booleans"):
                return None
            return f"domain '{domain}' has no numeric state (turn on 'include on/off as 0/1')"
        return f"domain '{domain}' has no numeric state"

    # ---------------------------------------------------------- lifecycle

    async def async_start(self) -> None:
        self._running = True
        if self._unsub_flush is None:
            self._unsub_flush = async_track_time_interval(
                self._hass, self._on_flush_tick, timedelta(seconds=FLUSH_SECONDS)
            )

    async def async_stop(self) -> None:
        self._running = False
        if self._unsub_flush:
            self._unsub_flush()
            self._unsub_flush = None
        if self._unsub_states:
            self._unsub_states()
            self._unsub_states = None
        # Not persisted: see the module docstring.
        self._governed = {}
        self._buffer.clear()
        self._deferred.clear()

    # ---------------------------------------------------------- reconcile

    async def async_current(self, target: str) -> set[str]:
        return set(self._governed.get(target, set()))

    async def async_apply(self, target: str, add: set[str], remove: set[str]) -> None:
        members = self._governed.setdefault(target, set())
        members |= add
        members -= remove
        if not members:
            self._governed.pop(target, None)
        for entity_id in remove:
            self._deferred.pop(entity_id, None)
            self._last_emit.pop(entity_id, None)
        self._retrack()

    @callback
    def _retrack(self) -> None:
        if self._unsub_states:
            self._unsub_states()
            self._unsub_states = None
        watched = sorted({e for members in self._governed.values() for e in members})
        if watched:
            self._unsub_states = async_track_state_change_event(
                self._hass, watched, self._on_state_event
            )

    # ------------------------------------------------------------- points

    @callback
    def _on_state_event(self, event: Event) -> None:
        new = event.data.get("new_state")
        if new is None or self.is_dry_run():
            return
        entity_id = new.entity_id
        for target, members in self._governed.items():
            if entity_id not in members:
                continue
            cfg = json.loads(target)
            value = numeric(new.state, booleans=cfg["booleans"])
            if value is None:
                continue
            self._offer(cfg, entity_id, value, new.last_updated, new.attributes)

    def _tags(self, cfg: dict[str, Any], entity_id: str, attributes: Any) -> dict[str, str]:
        tags = {"entity_id": entity_id, "domain": entity_id.split(".", 1)[0]}
        entry = er.async_get(self._hass).async_get(entity_id)
        if cfg["area"]:
            area_id = entry.area_id if entry else None
            if not area_id and entry and entry.device_id:
                device = dr.async_get(self._hass).async_get(entry.device_id)
                area_id = device.area_id if device else None
            area = ar.async_get(self._hass).async_get_area(area_id) if area_id else None
            if area:
                tags["area"] = area.name
        if cfg["device_class"]:
            klass = attributes.get("device_class") or (entry.device_class if entry else None)
            if klass:
                tags["device_class"] = str(klass)
        if cfg["unit"] and (unit := attributes.get("unit_of_measurement")):
            tags["unit_of_measurement"] = str(unit)
        return tags

    @callback
    def _offer(
        self,
        cfg: dict[str, Any],
        entity_id: str,
        value: float,
        when: datetime,
        attributes: Any,
    ) -> None:
        now = time.monotonic()
        last = self._last_emit.get(entity_id)
        text = line(self._tags(cfg, entity_id, attributes), value, when)
        if last is None or now - last >= cfg["interval"]:
            self._emit(entity_id, text, now)
            self._deferred.pop(entity_id, None)
        else:
            # Too soon: keep only the latest value and send it once the interval is up.
            self._deferred[entity_id] = (value, when, text)

    def _emit(self, entity_id: str, text: str, now: float) -> None:
        if len(self._buffer) == self._buffer.maxlen:
            self.dropped += 1  # the deque discards the oldest
        self._buffer.append(text)
        self._last_emit[entity_id] = now

    @callback
    def _release_deferred(self) -> None:
        now = time.monotonic()
        for entity_id, (_value, _when, text) in list(self._deferred.items()):
            cfg = self._config_for(entity_id)
            interval = cfg["interval"] if cfg else DEFAULT_INTERVAL
            if now - self._last_emit.get(entity_id, 0.0) >= interval:
                self._emit(entity_id, text, now)
                del self._deferred[entity_id]

    def _config_for(self, entity_id: str) -> dict[str, Any] | None:
        for target, members in self._governed.items():
            if entity_id in members:
                return json.loads(target)
        return None

    # -------------------------------------------------------------- flush

    @callback
    def _on_flush_tick(self, _now: datetime) -> None:
        if self._running:
            self._hass.async_create_task(self.async_flush())

    async def async_flush(self) -> None:
        """Post buffered points to the configured URL, in batches."""
        self._release_deferred()
        if not self._buffer:
            return
        settings = self.get_settings()
        if not settings.allow_external_data:
            self._buffer.clear()  # permission withdrawn: send nothing, keep nothing
            return
        if self.is_dry_run():
            self._buffer.clear()
            return
        if not settings.metrics_url:
            self._buffer.clear()  # nowhere to send: keep nothing
            self.last_error = "No Metrics URL is set (Settings)"
            return
        session = async_get_clientsession(self._hass)
        while self._buffer:
            batch = [self._buffer[i] for i in range(min(BATCH_LINES, len(self._buffer)))]
            try:
                async with session.post(
                    settings.metrics_url,
                    data="\n".join(batch).encode(),
                    headers={"Content-Type": "text/plain; charset=utf-8"},
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    if response.status >= 300:
                        raise RuntimeError(f"HTTP {response.status}")
            except Exception as err:  # unreachable, refused, timed out: try again next flush
                if self.last_error is None:
                    _LOGGER.warning(
                        "PropSense could not send metrics to %s: %s (will retry)",
                        settings.metrics_url,
                        err,
                    )
                self.last_error = str(err) or type(err).__name__
                return
            for _ in batch:
                self._buffer.popleft()
            self.sent += len(batch)
            self.last_error = None
            self.last_success = dt_util.utcnow().isoformat()

    # ------------------------------------------------------------- status

    def status(self) -> dict[str, Any]:
        settings = self.get_settings()
        return {
            "url": settings.metrics_url,
            "targets": [
                {"label": describe(json.loads(t)), "entities": len(m)}
                for t, m in sorted(self._governed.items())
            ],
            "buffered": len(self._buffer),
            "sent": self.sent,
            "dropped": self.dropped,
            "last_error": self.last_error,
            "last_success": self.last_success,
        }
