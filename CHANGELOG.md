# Changelog

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
