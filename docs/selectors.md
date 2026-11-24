# Selectors and settings

## Selector fields

A selector is a set of optional fields. Each field takes a list of values.

| Field | Matches |
|---|---|
| `labels` | Entities with one of these labels, including labels inherited from the device |
| `areas`, `floors` | The entity's area, which falls back to its device's area, and the floor that area is on |
| `domains`, `device_classes` | The entity's domain (`light`) or device class (`temperature`) |
| `entities`, `devices` | Specific entities or devices |
| `groups` | Members of a group, including nested groups |
| `capabilities` | Tags read from the entity's state (see below) |
| `integrations`, `manufacturers`, `models` | Where the entity comes from, and its device's manufacturer and model |
| `entity_categories` | `primary` (no category), `config` or `diagnostic` |
| `name_patterns`, `label_patterns` | Wildcard patterns on names, or on label names |
| `states`, `conditions` | The entity's current state or an attribute (see below) |

Capabilities cover lights (`onoff`, `brightness`, `color_temp`, `color`, `white`), covers (`position`, `tilt`), fans (`speed`, `oscillate`, `direction`, `preset`) and climate entities (`heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only`, `target_temp`).

## How rules combine

- Within one field, a list means any of the values.
- Across fields, every non-empty field must match. Label `Expose: Voice` plus area `Kitchen` means labelled and in the kitchen.
- An empty selector matches nothing, so a half-edited rule can never select everything. A rule with only an exclude also matches nothing.
- Rules are additive. An entity is wanted if any enabled rule includes it. A rule's exclude only subtracts from that same rule.
- Entities inherit their device's labels (on by default) and can inherit their area's labels (off by default).
- Disabled entities are skipped.

## Patterns and wildcards

`name_patterns`, `label_patterns`, `manufacturers` and `models` accept `*` for any text and `?` for one character, ignoring case. A name pattern is tried against both the entity id and its name, so `switch.*_plug` and `*outlet*` both work. A label pattern matches label names, so `Expose: *` selects every label named like that, including ones you add later. Integrations match exactly, ignoring case.

## State-based selection

`states` matches the entity's current state against a list, ignoring case. `conditions` read the state or an attribute:

| Condition | Meaning |
|---|---|
| `state < 20` | the state is a number below 20 |
| `attr:battery_level <= 15` | the attribute is a number of at most 15 |
| `state between 10 20` | a number from 10 to 20, in either order |
| `state = on`, `attr:hvac_action != idle` | equal or not equal. Numbers compare as numbers and anything else as text, ignoring case |

The operators are `<`, `<=`, `>`, `>=`, `=`, `!=` and `between`. Any one condition may hold. A missing state or attribute never matches, so `!=` does not match an entity that lacks the attribute.

A selection based on state follows the entities as they change, so think about the action. An expose rule on `state = on` will expose and un-expose entities as they toggle.

PropSense does not re-run the plan on every state change. When a state or attribute changes, it checks that one entity against the rules that use state, and re-runs after a 5 second quiet period only if the answer for that rule changed. Rules without state fields add no work.

## Settings

| Setting | Default | What it does |
|---|---|---|
| Managed assistants | Assist | The assistants PropSense owns. Anything not selected is un-exposed there. |
| Blocked domains | `lock`, `alarm_control_panel`, `camera` | Never touched, even if a rule names them. They are reported as blocked. |
| Maximum exposed (`max_exposed`) | 100 | If a plan would expose more than this to one assistant, nothing changes for that assistant and a Repairs issue is raised. `0` turns the guard off. |
| Inherit device labels | on | Entities inherit their device's labels. |
| Inherit area labels | off | Entities inherit their area's labels. |
| Dry run | off | Work out and report the plan without applying it. |
| Allow third-party actions | off | Lets actions from other integrations run. Rules that use them stay dormant (the panel shows Paused) until this is on. |
| Allow sending data off this instance | off | Needed before the metrics action sends anything. |
| Metrics URL | none | The one address metrics are sent to. There is no default. |

Rules are stored in PropSense's own storage, and settings in the config entry options.

## When it runs

PropSense re-evaluates on Home Assistant start, when an entity, device, area, floor or label changes, when the state of a group used by a rule changes, and once an hour. Triggers are debounced by 2 seconds.
