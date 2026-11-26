# PropSense

**Rules for Home Assistant entities: pick them by label, area, integration or state, then expose, group, tag, schedule or put them on a dashboard.**

> **Status: in testing.** The rules, actions and panel work and are covered by tests, but the project is young and the extension API for other integrations may still change.
> This project comes with no warranty or guarantee of fitness for any purpose. Use it at your own risk.
>
> **LLM use.** Built and maintained with substantial AI assistance (Claude Code). Design decisions and reviews are by a human, and generated code is reviewed before it is merged.

<p align="center">
  <img src="https://raw.githubusercontent.com/tmeuze/ha-propsense/main/docs/images/overview.svg" alt="Four layers: Home Assistant's facts about entities feed a rule, which acts through voice exposure, groups, labels, schedules and dashboards, with safety checks applied last" width="860">
</p>

## What it does

A PropSense rule has two parts: a selector and one or more actions. The selector describes a set of entities, for example "every switch labelled Outdoor, except the ones in the garage". The actions say what happens to that set. PropSense watches the registries and states in Home Assistant, so when a label, area or state changes, the set changes and every action follows.

Rules are the single source of truth. If a rule says three lights belong in a group, the group has those three lights, and a light someone added by hand is removed on the next apply. That is what makes the result reproducible, and it is why you should read [Safe first run](#safe-first-run) before you switch it on.

## Use cases

**Reach for it when** you want Home Assistant's labels and areas to decide things for you. Some examples:

- Only entities labelled `Expose: Voice` reach your assistant, which keeps an LLM conversation agent's prompt small.
- A light or cover group always equals a rule, such as the living room lights that can change color.
- Outlets switch off three hours after they were switched on, or lights come on at sunset, and it survives a restart.
- Every low battery sensor gets a `Needs battery` label, and other rules react to that label.
- A guest or kiosk account sees a dashboard built from a rule and nothing else on it.
- Repairs lists the entities that should have a label and don't.

**Look elsewhere when** you need to restrict what a user can read or control. A dashboard audience only chooses what is shown. See [Dashboards](docs/dashboards.md#what-this-does-not-protect). PropSense also does not change the sidebar, create users, or edit `configuration.yaml`.

## Getting started

PropSense needs Home Assistant 2026.9.0 or newer.

1. In HACS, open the menu, choose **Custom repositories**, and add `https://github.com/tmeuze/ha-propsense` as an **Integration**.
2. Download **PropSense** and restart Home Assistant.
3. Go to Settings, Devices & services, **Add integration**, and pick PropSense.
4. Open **PropSense** in the sidebar (administrators only).

To copy the integration by hand instead, put `custom_components/propsense` into your `<config>/custom_components/` folder and restart.

### Your first rule

1. On the Rules tab, turn on **dry run** when the page offers it. Nothing is applied while it is on.
2. Choose **Add rule**, pick a template or start empty, and fill in the selector. The live preview on the right shows what the rule selects.
3. Add the action you want, then save.
4. Open the Status tab, run a dry run, and read what would be added or removed.
5. When that looks right, turn dry run off.

### Safe first run

Because rules are the single source of truth, an empty or wrong rule set un-exposes everything PropSense manages on its first apply. That is the reason for steps 1 and 4 above. It also helps to keep exposure small: each exposed entity costs roughly 26 prompt tokens for an LLM conversation agent, and the `max_exposed` setting (100 by default) stops a plan that would expose more than that.

## Usage

The PropSense panel has four tabs.

| Tab | What it is for |
|---|---|
| Rules | Add, edit, duplicate, switch on and off, and delete rules. Rules are grouped by what they do, with search and filters. The editor shows a live preview of what a rule selects. |
| Status | The last result for each action, a dry run, **Apply now**, running timers and the next scheduled runs. |
| Explain | Pick an entity and see which rules select it, which exclude it, and what each action would do to it. |
| Settings | Managed assistants, blocked domains, the size limit, label inheritance, dry run, the permissions for third-party actions and sending data, and the display options. |

A rule can carry several actions, and they all share its selection. Keep actions together when they should always apply to the same entities. Split them into separate rules when they need different selections, or when you want to switch one off on its own, because the on/off switch belongs to the rule. Rules can also feed each other through labels.

| Action | What it does | Details |
|---|---|---|
| Expose to voice assistants | Exposes the selection to Assist, Alexa or Google Assistant and un-exposes everything else | [Actions](docs/actions.md#expose-to-voice-assistants) |
| Keep a group in sync | Makes a group helper's members equal to the selection, and labels the group `[PropSense]` | [Actions](docs/actions.md#keep-a-groups-members-in-sync) |
| Timers and schedules | Turns entities on or off after a delay, at a time of day, or at sunrise or sunset | [Actions](docs/actions.md#timers-and-schedules) |
| Apply a label | Adds a label to the selection and removes it from entities that stop matching | [Actions](docs/actions.md#apply-a-label) |
| Give a voice alias | Keeps an extra name on the selected entities for voice assistants | [Actions](docs/actions.md#give-a-voice-alias) |
| Flag in Repairs | Lists the selection in Repairs, which suits hygiene checks | [Actions](docs/actions.md#flag-in-repairs) |
| Run actions on enter or leave | Runs your own Home Assistant actions when an entity starts or stops matching | [Actions](docs/actions.md#run-actions-when-an-entity-enters-or-leaves) |
| Show on a dashboard | Fills a named dashboard section, shown to the audience you choose | [Dashboards](docs/dashboards.md) |
| Ship numeric history | Sends numeric states to a metrics endpoint you set, once you allow it | [Metrics](docs/metrics.md) |

Two services are available. `propsense.resync` re-evaluates the rules and applies now, and takes `dry_run: true` to report without applying. `propsense.preview` returns the plan as response data. A status sensor shows the last result, and diagnostics include the rules, settings and last result.

## Configuration

Settings live on the panel's Settings tab. The ones you are most likely to change are the managed assistants (Assist by default), the blocked domains (locks, alarm panels and cameras), the size limit, and dry run. Nothing that sends data off your instance is on by default, and the metrics action has no default address. The full list, with defaults, is in [Selectors and settings](docs/selectors.md#settings). What PropSense controls and what it leaves alone is in [Ownership](docs/ownership.md).

The panel offers display options for text size, high contrast and reduced motion. It follows Home Assistant's own light and dark theme. What was offered and what was tested is in [Accessibility](docs/accessibility.md).

## How it works

A rules engine with no Home Assistant code in it decides which entities each rule selects. A manager builds that from the registries and states, works out what each action would add and remove, runs the safety checks, and then lets the action apply the difference. Actions are plug-ins, so other integrations can add their own. [Architecture](docs/architecture.md) has the details and the extension API.

## Documentation

| Read | For |
|---|---|
| [Documentation index](docs/README.md) | Every document, with a line on what it covers. |
| [Actions](docs/actions.md) | What each action does and what it will not do. |
| [Selectors and settings](docs/selectors.md) | The selector fields, how rules combine, and every setting. |
| [Dashboards](docs/dashboards.md) | Building a dashboard from rules, and what audiences do and don't protect. |
| [Metrics](docs/metrics.md) | Shipping numeric history, and the limits on it. |
| [Accessibility](docs/accessibility.md) | The display options, and what was tested. |
| [Architecture](docs/architecture.md) | How the pieces fit, and the extension API for other integrations. |
| [Ownership](docs/ownership.md) | What PropSense controls, what it leaves alone, and how to change each thing. |
| [Security](docs/security.md) | Trust boundaries, what leaves your instance, and dependency updates. |
| [Decisions](docs/decisions.md) | The significant choices, with the reasoning and the cost. |
| [Where this got to](docs/STATE.md) | Current state and known gaps. |
| [Credits](docs/credits.md) | Dependencies and licences. |
| [Changelog](CHANGELOG.md) | What changed in each release. |

## Development

Create a Python virtual environment with the pyenv or venv tooling you normally use, then:

```bash
pip install -r requirements-test.txt
python -m pytest -q
```

The panel is a Lit web component in `frontend/`. The built bundle is committed to `custom_components/propsense/frontend/` so a HACS install needs no build step, and CI fails if the bundle is out of date.

```bash
cd frontend && npm ci && npm run build
```

Other integrations add their own actions through the extension API. The module docstring in `custom_components/propsense/api.py` is the reference. See [AGENTS.md](AGENTS.md) for how contributors and AI agents should work in this repository.

## Licence

MIT. See [LICENSE](LICENSE).
