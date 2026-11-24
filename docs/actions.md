# Actions

An action is what a rule does with the entities its selector picks. A rule can have several, and they all share the same selection. This page covers each built-in action. Dashboards and metrics have their own pages: [Dashboards](dashboards.md) and [Metrics](metrics.md).

Actions come in two kinds. A **state** action keeps something equal to the selection, so anything not selected is removed (exposure, groups, labels, aliases, dashboard sections). An **edge** action fires when an entity starts or stops matching (run actions on enter or leave).

## Expose to voice assistants

Exposes the selected entities to one or more of Assist, Alexa and Google Assistant. For each assistant PropSense manages, anything no rule selects is un-exposed, including entities you ticked by hand. The assistants it manages are a setting (Assist by default), so Alexa and Google are left alone until you add them.

Safety limits apply here. Locks, alarm panels and cameras are never exposed, even when a rule names them. If a plan would expose more than `max_exposed` entities to one assistant, nothing changes for that assistant and a Repairs issue explains why. See [Selectors and settings](selectors.md#settings).

## Keep a group's members in sync

Targets a Home Assistant group helper (light, switch, fan, cover, media player or valve). Pick an existing group to edit, or give a name and a type and PropSense creates the group. Either way the group gets the `[PropSense]` label, so you can tell managed groups apart.

The rules decide the members, so a member added by hand is removed on the next apply. Entities of the wrong domain for the group type, other group helpers, and blocked domains are skipped and listed on the Status tab. Editing members reloads the group briefly.

## Timers and schedules

One action with three triggers.

- **After being on (or off) for a while.** This is the auto-off timer. It watches the entity's state, so it makes no difference whether you switched the entity in Home Assistant or by hand. If the entity changes to the other state first, the timer is cancelled. Deadlines are stored as absolute times, so a restart neither resets nor loses them. If a deadline passes while Home Assistant is down, the entity is turned off after start-up, provided it is still on. An entity that is already on when PropSense first sees it starts its timer at that moment.
- **At a time of day**, optionally on chosen weekdays.
- **At sunrise or sunset**, with an offset in minutes.

For time and sun triggers, "catch up" runs a trigger that was missed while Home Assistant was down, as long as it falls inside the window you choose (0 skips it). Entities already in the wanted state are left alone.

Each schedule action has one trigger and one direction. To turn lights on at sunset and off at sunrise, add two schedule actions to the same rule.

Only domains that can be turned on and off are supported: lights, switches, fans, input booleans, humidifiers, media players, climate, remotes, sirens and water heaters. Locks, alarm panels and cameras are blocked by default. A dry run stops everything from firing. Active timers and the next run of each schedule show on the Status tab.

## Apply a label

Adds a label to every selected entity and removes it from entities that stop matching, even ones someone labelled by hand. The label is created if it does not exist. Only the entity's own labels change, not the ones it inherits from its device or area, and entities without a registry entry are skipped.

Because other rules can select on that label, rules can feed each other: one rule labels low batteries, another sends a notification when something gets the label.

## Give a voice alias

Does the same for one or more aliases on an entity. The entity's other aliases are never touched.

## Flag in Repairs

Lists the selected entities in Home Assistant's Repairs under a title you choose. The issue disappears when nothing matches. It changes no entity.

This is for hygiene checks, so write the rule to select what should not exist. For example, lights that have no label at all: select the `light` domain and exclude the label pattern `*`.

## Run actions when an entity enters or leaves

Runs ordinary Home Assistant actions (services, notifications, scripts, conditions) for each entity that starts or stops matching. Home Assistant has no trigger for "a label was added", and this fills that gap.

In templates you can use `entity_id`, `event` (`enter` or `leave`) and `name`. The first time PropSense sees a rule it only records what matches, so adding the rule never fires for entities that already match, and a restart does not re-fire either. At most 20 entities run per evaluation, which you can change.

## Loop breaker

Rules that apply labels can chase each other, for example when one rule adds a label that another rule removes. If applying changes something 20 times within a minute, PropSense pauses for five minutes, keeps reporting what it would do, and raises a Repairs issue. It then resumes on its own.
