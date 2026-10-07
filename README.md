# PropSense

Rules for Home Assistant entities, driven by labels, areas, floors, groups and more. A rule selects entities and applies an action to them. It works like a soft ACL that you maintain by labelling things instead of ticking boxes.

Version 0.1 has one action: **expose entities to voice assistants** (Assist, Alexa, Google Assistant).

Example: label an entity `Expose: Novak`, add one rule that exposes everything with that label to Assist, and the entity appears in Assist's exposed list. Remove the label and it disappears.

> **Rules are the single source of truth.** For every assistant PropSense manages, anything no rule selects is un-exposed, including entities you ticked by hand. Start with **dry run** on (see [Safe first run](#safe-first-run)).

## Install

### HACS (custom repository)

1. HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/tmeuze/ha-propsense` as an **Integration**.
3. Download **PropSense**, then restart Home Assistant.
4. Settings → Devices & services → **Add integration** → PropSense.

Requires Home Assistant 2026.9.0 or newer.

### Manual

Copy `custom_components/propsense` into `<config>/custom_components/` and restart.

## Concepts

A **rule** has:

- an **include** selector,
- an optional **exclude** selector,
- an **action** (expose to one or more assistants),
- an enabled switch.

A **selector** is a set of optional fields: `labels`, `areas`, `floors`, `domains`, `device_classes`, `entities`, `devices`, `groups`.

### Semantics

- Within one field, a list means **any of**.
- Across fields, every non-empty field must match (**and**). Labels `Expose: Novak` plus area `Kitchen` means labelled *and* in the kitchen.
- An **empty selector matches nothing**, so a half-edited rule can never expose everything. An exclude-only rule also matches nothing.
- Rules are **additive**. An entity is wanted if any enabled rule includes it. A rule's exclude only subtracts from that same rule.
- Entities inherit their device's labels (default on) and optionally their area's labels (default off). An entity's area falls back to its device's area, and its floor comes from the area.
- Group fields expand group members, including nested groups.
- Disabled entities are skipped.

### Settings

| Setting | Default | Meaning |
|---|---|---|
| `managed_assistants` | Assist | Assistants PropSense owns. Anything not selected is un-exposed there. |
| `blocked_domains` | `lock`, `alarm_control_panel`, `camera` | Never exposed, even if a rule lists them explicitly. Reported as blocked. |
| `max_exposed` | 100 | If a plan would expose more than this to one assistant, nothing changes for that assistant and a Repairs issue is raised. `0` disables the guard. |
| `inherit_device_labels` | on | Entities inherit their device's labels. |
| `inherit_area_labels` | off | Entities inherit their area's labels. |
| `dry_run` | off | Compute and report the plan without applying it. |

## Configure

Settings → Devices & services → PropSense → **Configure**. The menu lets you add, edit, toggle and delete rules, edit settings, and **preview** what the current rules would change.

Rules and settings are stored in the config entry options.

### Services

| Service | Purpose |
|---|---|
| `propsense.resync` | Re-evaluate and apply now. `dry_run: true` reports without applying. |
| `propsense.preview` | Return the plan (what would be exposed and un-exposed) as response data. |

A status sensor shows the last result, and diagnostics include the rules, settings and last result.

### When it runs

On Home Assistant start, on registry changes (entity, device, area, floor, label), when the state of a group used by a rule changes, and hourly. Triggers are debounced by 2 seconds.

## Safe first run

With the single-source-of-truth model, an empty or wrong rule set un-exposes everything on the first apply.

1. Turn on **dry run** in settings.
2. Add your rules.
3. Open **Preview** and check the exposed and un-exposed lists.
4. Turn dry run off.

Mind your model's context budget too. Each exposed entity costs roughly 26 prompt tokens for an LLM conversation agent, so keep exposure small and curated. `max_exposed` is the guard rail.

## Development

```bash
python -m venv .venv
.venv/bin/pip install pytest-homeassistant-custom-component
.venv/bin/python -m pytest -q
```

`engine.py` is pure policy with no Home Assistant imports. `snapshot.py` builds entity facts from the registries and `manager.py` applies the result.

## License

MIT
