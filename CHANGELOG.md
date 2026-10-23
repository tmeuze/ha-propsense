# Changelog

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
