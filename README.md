# PropSense

Rules for Home Assistant entities, driven by labels, areas, floors, groups and more. A rule selects entities and applies an action to them. It works like a soft ACL that you maintain by labelling things instead of ticking boxes.

Version 0.1 has one action: **expose entities to voice assistants** (Assist, Alexa, Google Assistant).

Example: label an entity `Expose: Novak`, add one rule that exposes everything with that label to Assist, and the entity appears in Assist's exposed list. Remove the label and it disappears.

> **Rules are the single source of truth.** For every assistant PropSense manages, anything no rule selects is un-exposed, including entities you ticked by hand. Start with **dry run** on (see [Safe first run](#safe-first-run)).

## Use cases

Today PropSense has four actions: **expose to voice assistants**, **keep a group's members in sync**, **turn on or off on a timer or schedule**, and **ship numeric history to a metrics endpoint**. The rest are what the rules-and-actions design is for, and they are planned, not built.

- **Fewer labels** *(available)*: select by integration, manufacturer, model, entity category, name pattern or a label name wildcard such as `Expose: *`, instead of tagging every entity.
- **Curated voice exposure** *(available)*: label entities `Expose: Novak` and only those reach that agent, which keeps an LLM's prompt small.
- **Per-assistant exposure** *(available)*: different rules for Assist, Alexa and Google Assistant.
- **Dynamic groups** *(available)*: keep a light, switch, fan, cover, media player or valve group equal to a rule, for example the lights in the living room that can change white temperature, or every cover that can be set to a position. PropSense creates the group or edits one you pick, and labels it `[PropSense]`.
- **Auto-off timers** *(available)*: turn outlets off after they have been on for three hours. Survives restarts and respects manual switching.
- **Time and sunset schedules** *(available)*: turn lights on at sunset, off at 23:00, on chosen weekdays.
- **Metrics shipping** *(available)*: label the sensors you care about and their numeric history is sent to VictoriaMetrics, with no YAML.
- **Run something when a label is applied** *(planned)*: Home Assistant has no trigger for "label added". An `edge` action would call a service or fire an event when an entity enters a selection.
- **Auto-tagging** *(planned)*: apply a label from metadata, such as every battery sensor getting `Needs battery`, or everything in the garage getting `Outdoor`.
- **Voice aliases** *(planned)*: entities selected for a voice agent also get a standard alias.
- **Hygiene rules** *(planned)*: exclude entities from the recorder by label, or flag entities that should be labelled but aren't.
- **Access tiers** *(planned)*: labels decide what a guest dashboard or a voice agent can see.
- **Grant to child instances** *(planned)*: an action type provided by [ha-unity](https://github.com/tmeuze/ha-unity) through PropSense's extension API.

Similar tools exist for parts of this, for example label-based voice exposure in community integrations. PropSense aims to be the general engine: one selector model, safety guards, and an API other integrations can build actions on.

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

A **selector** is a set of optional fields: `labels`, `areas`, `floors`, `domains`, `device_classes`, `entities`, `devices`, `groups`, `capabilities`, `integrations`, `manufacturers`, `models`, `entity_categories`, `name_patterns`, `label_patterns`, `states` and `conditions`. Capabilities are tags read from an entity's state: lights (`onoff`, `brightness`, `color_temp`, `color`, `white`), covers (`position`, `tilt`), fans (`speed`, `oscillate`, `direction`, `preset`) and climate entities (`heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only`, `target_temp`).

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

### Patterns and wildcards

`name_patterns`, `label_patterns`, `manufacturers` and `models` accept `*` (any text) and `?` (one character), ignoring case. Name patterns are tried against both the entity id and its name, so `switch.*_plug` and `*outlet*` both work. Label patterns match label **names**, so `Expose: *` selects every label named like that, including ones you add later. Integrations match exactly (ignoring case). Entity categories are `primary` (no category), `config` and `diagnostic`.

### State-based selection

`states` matches the entity's current state (any of a list, ignoring case). `conditions` read the state or an attribute:

| Condition | Meaning |
|---|---|
| `state < 20` | the state is a number below 20 |
| `attr:battery_level <= 15` | the attribute is a number at most 15 |
| `state between 10 20` | a number from 10 to 20 (either order) |
| `state = on`, `attr:hvac_action != idle` | equal or not equal; numbers compare as numbers, anything else as text ignoring case |

Operators are `<`, `<=`, `>`, `>=`, `=`, `!=` and `between`. Any one condition may hold, and a missing state or attribute never matches (so `!=` does not match an entity that lacks the attribute).

A selection that follows live state changes as entities change, so be deliberate about the action: an expose rule on `state = on` will expose and un-expose as things toggle. **Cost:** PropSense does not re-run the plan on every state change. When a state or attribute changes, it checks that one entity against the rules that use state, and re-runs (after a 5 second quiet period) only if the answer for that rule changed. Rules without state fields add no work.

### Group action

The **Keep a group's members in sync** action targets a Home Assistant group helper. Pick an existing group to edit, or give a name (and type) and PropSense creates it. Either way the group gets the `[PropSense]` label. The rules are the single source of truth: members added by hand are removed on the next apply. Entities of the wrong domain for the group type, other group helpers, and blocked domains are skipped and listed in the status page. Editing members reloads the group briefly.

### Timers and schedules

The **Turn on or off on a timer or schedule** action has three triggers:

- **After being on (or off) for a duration**: an auto-off timer. It watches the entity's state, so it makes no difference whether the entity was switched in Home Assistant or by hand; if it changes to the other state first, the timer is cancelled. Deadlines are stored as absolute times, so a restart neither resets nor loses them. If a deadline passes while Home Assistant is down, the entity is turned off after start-up, provided it is still on. Entities that are already on when PropSense first sees them start their timer then.
- **At a time of day**, optionally on chosen weekdays.
- **At sunrise or sunset**, with an offset in minutes.

For time and sun triggers, "catch up" runs a trigger that was missed while Home Assistant was down, if it is within the window you choose (0 skips it). Entities already in the wanted state are left alone. Only domains that can be turned on and off are supported (lights, switches, fans, input booleans, humidifiers, media players, climate, remotes, sirens, water heaters). Locks, alarm panels and cameras are blocked by default, and dry run stops anything from firing. Active timers and the next run of each schedule appear on the Status page.

### Metrics shipping

The **Ship numeric history** action sends the numeric states of the entities a rule selects, in the InfluxDB line protocol, to one URL: the **Metrics URL** setting (default `https://vm.in.a64.one/write`, a VictoriaMetrics endpoint). It is **off until you turn on "Allow sending data off this instance"** in Settings, and it uses no credentials, so the endpoint should only accept posts from your own network. PropSense verifies the endpoint's TLS certificate and never relaxes that check: with an HTTPS URL the certificate must be trusted by the machine Home Assistant runs on (for example one issued by your own CA).

Each point looks like `homeassistant,area=Kitchen,device_class=temperature,domain=sensor,entity_id=sensor.kitchen_temp,unit_of_measurement=°C value=21.5 <ns timestamp>`. The area, device class and unit tags are optional.

- **Cost:** PropSense listens only to the state changes of the entities selected, never to every event. Each entity emits at most one point per interval (60 s by default; the latest value wins) and points are posted in batches every 30 s. A rule may select at most 200 entities by default (up to 1000); a wider rule is refused and a repair issue is raised.
- **What is sent:** numeric states only. `unknown`, `unavailable` and text are skipped; on/off states are sent as 1/0 only if you turn that on. Locks, alarm panels and cameras are blocked by default.
- **If the endpoint is down:** points wait in a bounded in-memory buffer (5000) and are retried every 30 s; the oldest are dropped when it is full.
- **Restarts:** the buffer is not saved, so a restart loses what had not been sent (at most one 30 s window, plus any outage).
- **Dry run** and withdrawing the permission discard waiting points and send nothing.

## Configure

Open **PropSense** in the sidebar (administrators only).

- **Rules:** add, edit, enable or disable and delete rules. The editor shows a live preview of the entities a rule selects, and the prompt-token estimate if you expose them to an LLM agent.
- **Status:** the last result per action and target, a **dry run** that shows what would be added or removed, and **Apply now**.
- **Explain:** pick an entity and see which rules select it, which exclude it, and what each action would do.
- **Settings:** managed assistants, blocked domains, the size guard, label inheritance, dry run, and whether third-party actions are allowed.

Rules are stored in PropSense's own storage, and settings in the config entry options. The integration's **Configure** button still offers the older step-by-step flow for the same rules and settings.

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

1. Turn on **dry run** (the Rules page offers it while there are no rules).
2. Add your rules and watch the live preview.
3. Open **Status → Dry run** and check what would be added and removed.
4. Turn dry run off.

Mind your model's context budget too. Each exposed entity costs roughly 26 prompt tokens for an LLM conversation agent, so keep exposure small and curated. `max_exposed` is the guard rail.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
```

The panel is a Lit web component in `frontend/`. The built bundle is committed to `custom_components/propsense/frontend/` so HACS installs need no build step; CI fails if it is out of date.

```bash
cd frontend && npm ci && npm run build
```

### Extending PropSense

Other integrations register action types through `custom_components/propsense/api.py` (see the docstring there). A provider subclasses `ActionType`, declares `dependencies: ["propsense"]`, and calls `async_register_action(hass, MyAction())`. Actions are either `state` (kept equal to the selection) or `edge` (fire when an entity enters or leaves it). They stay dormant until the user allows third-party actions in the settings.

`engine.py` is pure policy with no Home Assistant imports. `snapshot.py` builds entity facts from the registries and `manager.py` applies the result.

## License

MIT
