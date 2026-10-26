# Changelog

## 0.8.2

- **There is no default Metrics URL any more.** An earlier default pointed at one person's own infrastructure, which is meaningless (and wrong) for everyone else. Set your own in Settings. Nothing is sent without a URL, the permission cannot be turned on without one, and the Status page says so. Addresses that earlier versions saved as a default are cleared; a URL you typed yourself is never touched.
- Examples and test fixtures no longer use personal names.

## 0.8.1

- Certificate verification is unchanged and is not weakened: with an HTTPS URL the endpoint's certificate must be trusted by the machine Home Assistant runs on. If it is not, sends fail with a TLS error, which PropSense treats like any other failed send (points wait in the buffer and are retried).

## 0.8.0

- **State-based selection.** Two new selector fields read an entity's own state:
  - **Current state**: any of a list of states (`on`, `unavailable`, ...).
  - **Conditions** on the state or an attribute: `state < 20`, `attr:battery_level <= 15`, `state between 10 20`, `attr:hvac_action != idle`. Operators: `<`, `<=`, `>`, `>=`, `=`, `!=`, `between`. Any one condition may hold. A missing value never matches.
- The plan re-runs when a state change flips what a rule selects, not on every state change: PropSense checks the one entity that changed against the rules that use state, and re-runs (after a 5 second quiet period) only if its answer changed. Rules without state fields cost nothing extra.
- The editor has a "Current state and attributes" section with a row editor for conditions, and Explain shows an entity's state.

## 0.7.0

- New built-in action **Ship numeric history to a metrics endpoint**: entities a rule selects (by label, integration, name pattern and so on) have their numeric states sent in the InfluxDB line protocol (for example to a VictoriaMetrics `/write` endpoint). Opt-in: nothing is sent until **Allow sending data off this instance** is turned on, and data goes only to the **Metrics URL** setting, which you set yourself (there is no default). No credentials are used or stored.
  - Only numeric states are sent (booleans as 1/0 if you ask), at most one point per entity per interval (default 60 s, latest value wins), batched every 30 s, and a rule may select at most 200 entities (adjustable up to 1000).
  - If the endpoint is unreachable, points wait in a bounded in-memory buffer (5000 points) and the oldest are dropped when it is full. The buffer is not saved, so a restart loses what had not been sent. Dry run and withdrawing the permission discard the buffer and send nothing.
  - The Status page shows the target, points sent, waiting and dropped, and the last error.
- Actions can now have their own entity limit (the metrics cap) instead of the shared `max_exposed`.
- Status page shows readable names for each action target instead of raw configuration.

## 0.6.0

- Six new selector fields, so rules need fewer labels:
  - **Integrations** (where an entity comes from, for example `hue`).
  - **Manufacturers** and **Models** of the entity's device, with wildcards.
  - **Entity categories** (primary, config, diagnostic).
  - **Name or entity id patterns** with `*` and `?` wildcards, matched against both the id and the name.
  - **Label name patterns**, for example `Expose: *` matches every label that starts that way, whatever its id.
- The editor groups the new fields under "More filters", offers the integrations, manufacturers and models you actually have, and the Explain tab shows these facts for an entity.

## 0.5.0

- New built-in action **Turn on or off on a timer or schedule**:
  - **Auto-off timer**: turn entities off (or on) after they have been on (or off) for a set time. It watches the entity's state, so manual and in-Home-Assistant changes are treated the same. Deadlines are stored as absolute times, so restarts neither reset nor lose them, and the state is re-checked before acting.
  - **Time of day** and **sunrise/sunset** (with an offset) triggers, optionally on chosen weekdays, with an optional catch-up window for triggers missed while Home Assistant was down.
  - Locks, alarms and cameras are never touched (blocked domains); dry run stops everything from firing.
- Panel: rule templates (auto-off, lights on at sunset, lights off at night, expose, dynamic group), a plain-language editor for the schedule action, rule cards that say what each rule does, running timers and next runs on the Status page, confirmation toasts, and the draft preview now shows only what that rule skipped.
- Extension API: providers can implement `async_start`, `async_stop` and `status`.

## 0.4.0

- Capabilities now cover more than lights: covers (`position`, `tilt`), fans (`speed`, `oscillate`, `direction`, `preset`) and climate entities (`heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only`, `target_temp`). The selector field is simply called **Capabilities**.

## 0.3.0

- New built-in action **Keep a group's members in sync**: rules decide the members of a group helper (light, switch, fan, cover, media player or valve group). Name an existing group to edit, or give a name and PropSense creates the group. Managed groups get the `[PropSense]` label. Rules are the single source of truth: members added by hand are removed.
- New selector field **Light capabilities** (on/off, brightness, white temperature, color, white channel), read from a light's supported color modes.
- Extension API: providers can `validate` configs, filter members with `accepts`, and get an `async_sync` housekeeping hook.

## 0.2.0

- **PropSense panel** in the sidebar (admin only): rule list with enable switches, a rule editor with live preview of what a rule selects, a status page with dry run and apply, an "explain this entity" page, and settings.
- Websocket API (`propsense/...`) behind the panel.
- Rules carry a list of actions. Exposure is the built-in `expose` action; 0.1 rules migrate automatically.
- Extension API (`custom_components/propsense/api.py`): other integrations register action types, either `state` (reconciled) or `edge` (fires on enter or leave).
- New setting "Allow third-party actions" (off by default). Rules using unavailable or disallowed action types stay dormant and never remove anything.
- Rules are stored in PropSense's own storage instead of the config entry options (migrated on first start).

## 0.1.0

- Rules engine: selectors over labels, areas, floors, domains, device classes, entities, devices and groups, with per-rule excludes.
- Action: expose matching entities to Assist, Alexa and Google Assistant.
- Rules are the single source of truth for each managed assistant.
- Safety: blocked domains, `max_exposed` guard with a Repairs issue, dry run.
- Options flow for rules and settings, status sensor, diagnostics, `propsense.resync` and `propsense.preview` services.
