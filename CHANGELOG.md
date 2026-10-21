# Changelog

## Unreleased

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
