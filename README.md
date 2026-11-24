# PropSense

[![Validate](https://github.com/tmeuze/ha-propsense/actions/workflows/validate.yml/badge.svg)](https://github.com/tmeuze/ha-propsense/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/tmeuze/ha-propsense)](https://github.com/tmeuze/ha-propsense/releases)
[![HACS](https://img.shields.io/badge/HACS-custom-orange.svg)](https://hacs.xyz)

Rules for Home Assistant entities. A rule picks entities by label, area, integration, state and more, then does something with them: exposes them to voice assistants, keeps a group in sync, tags them, schedules them or shows them on a dashboard.

**Status: in testing.** The rules, actions and panel work and are covered by tests, but the project is young and the extension API for other integrations may still change.

This project comes with no warranty or guarantee of fitness for any purpose. Use it at your own risk.

**LLM use:** this project is built and maintained with substantial AI assistance (Claude Code). Decisions and reviews are by a human, and generated code is reviewed before merge.

<p align="center">
  <img src="https://raw.githubusercontent.com/tmeuze/ha-propsense/main/docs/images/how-it-works.svg" alt="Entity facts feed a rule's selector, and the selected entities go to the rule's actions" width="860">
</p>

## What this does

A PropSense rule has two parts: a selector and one or more actions. The selector describes a set of entities, for example "every switch labelled Outdoor, except the ones in the garage". The actions say what happens to that set. PropSense watches the registries and states in Home Assistant, so when a label, area or state changes, the set changes and every action follows.

Rules are the single source of truth. If a rule says three lights belong in a group, the group has those three lights, and a light someone added by hand is removed on the next apply. That is what makes the result reproducible, and it is also why you should read [Safe first run](#safe-first-run) before you switch it on.

## Use cases

- **Curated voice exposure.** Label entities `Expose: Voice` and only those reach your assistant. That keeps the prompt of an LLM conversation agent small.
- **Fewer labels.** Select by integration, manufacturer, model, name pattern or a label wildcard such as `Expose: *`, instead of tagging every entity yourself.
- **Dynamic groups.** Keep a light or cover group equal to a rule, such as the living room lights that can change color.
- **Timers and schedules.** Turn outlets off three hours after they were switched on, or lights on at sunset, and have it survive a restart.
- **Auto-tagging.** Give every low battery sensor a `Needs battery` label, then let other rules react to that label.
- **Guest and kiosk dashboards.** Build a dashboard from a rule and show it only to the people it is for.
- **Hygiene checks.** List entities that should have a label and don't, in Home Assistant's Repairs.

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

## Actions

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

A rule can carry several actions at once, and they all share its selection. Keep actions together when they should always apply to the same entities. Split them into separate rules when they need different selections, or when you want to switch one off on its own, because the on/off switch belongs to the rule. Rules can also feed each other through labels.

How a selector works (fields, wildcards, state conditions, and how rules combine) is in [Selectors and settings](docs/selectors.md).

## Documentation

| | |
|---|---|
| [Documentation index](docs/README.md) | Every document, with a line on what it covers. |
| [Actions](docs/actions.md) | What each action does and what it will not do. |
| [Selectors and settings](docs/selectors.md) | The selector fields, rule semantics and every setting. |
| [Dashboards](docs/dashboards.md) | Building a dashboard from rules, and what audiences do and don't protect. |
| [Metrics](docs/metrics.md) | Shipping numeric history, and the limits on it. |
| [Architecture](docs/architecture.md) | How the pieces fit, and the extension API for other integrations. |
| [Ownership](docs/ownership.md) | What PropSense controls, what it leaves alone, and how to change each thing. |
| [Security](docs/security.md) | Trust boundaries and what leaves your instance. |
| [Decisions](docs/decisions.md) | The significant choices, with the reasoning and the cost. |
| [Where this got to](docs/STATE.md) | Current state and known gaps. |
| [Changelog](CHANGELOG.md) | What changed in each release. |

## Services

| Service | Purpose |
|---|---|
| `propsense.resync` | Re-evaluate the rules and apply now. Pass `dry_run: true` to report without applying. |
| `propsense.preview` | Return the plan (what would be added and removed) as response data. |

A status sensor shows the last result, and diagnostics include the rules, settings and last result.

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

Other integrations add their own actions through the extension API. The module docstring in `custom_components/propsense/api.py` is the reference, and [Architecture](docs/architecture.md) explains the design. See also [AGENTS.md](AGENTS.md) for how contributors and AI agents should work in this repository.

## Licence

MIT. See [LICENSE](LICENSE).
