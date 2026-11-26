# Architecture

PropSense is a Home Assistant custom integration with a pure rules engine in the middle, a manager that applies the result, and a set of pluggable actions on the outside. A sidebar panel and a websocket API sit on top.

![PropSense overview](images/overview.svg)

## The pieces

| File | Role |
|---|---|
| `engine.py` | The rules engine. It has no Home Assistant imports. It evaluates selectors against a snapshot of facts and produces a plan, an explanation, or a list of changes. |
| `snapshot.py` | Builds the facts the engine needs (labels, areas, integration, state and so on) from Home Assistant's registries and state machine. |
| `manager.py` | Owns the rules and settings, listens for changes, debounces them, runs the engine, applies the plan through the actions, and enforces the safety limits and the loop breaker. |
| `api.py` | The extension API. It defines `ActionType` and the registry that built-in and third-party actions register with. |
| `*_action.py` | The built-in actions: expose, group, schedule, metrics, label, aliases, flag, run and dashboard. |
| `websocket_api.py` | The commands behind the panel (administrators only), plus `propsense/dashboard/resolve`, which any logged-in user may call. |
| `panel.py`, `frontend/` | The sidebar panel, a Lit web component, and the dashboard strategy script. |
| `config_flow.py`, `sensor.py`, `diagnostics.py` | The config entry, the status sensor and diagnostics. |

## How a run works

1. Something triggers a run: Home Assistant starting, a registry change, a state change that flips a rule using state, a group changing, or the hourly resync.
2. The manager builds a snapshot and asks the engine for the entities each rule selects.
3. For every action target (an assistant, a group, a label, a dashboard section), the manager unions what all rules want, compares that with what the action reports it currently has, and works out what to add and remove.
4. The safety checks run: blocked domains, the size limit, the loop breaker, and dry run. A plan that fails a check changes nothing for that target.
5. The action's `async_apply` receives the difference. A dry run never reaches this step.

Actions are either **state** (kept equal to the selection) or **edge** (fired when an entity enters or leaves it). See [Actions](actions.md).

## Extension API

Another integration can add an action type. It declares `dependencies: ["propsense"]` in its manifest, subclasses `ActionType`, and calls `async_register_action(hass, MyAction())` during its own setup. PropSense then evaluates the rules and tells the action what to add and remove for each target. A provider never sees the rules or the registries.

Third-party actions stay paused (the code calls this dormant) until the user turns on **Allow third-party actions**. Rules that name an action that is not installed are kept and reported as paused, and a missing provider never causes removals. Actions that send data off the instance must set `needs_external_data`, and stay dormant until sending is allowed too.

The module docstring in `custom_components/propsense/api.py` is the reference, and `API_VERSION` changes when something breaks.

## Where the state lives

Rules are in PropSense's own storage (`propsense.rules`). Settings are in the config entry options. Runtime state that has to survive a restart, such as schedule deadlines and what each edge action last saw, is in `propsense.state` and `propsense.schedule`. See [Ownership](ownership.md) for what each thing controls.

## Dashboards

The dashboard action keeps its sections in memory. The strategy script runs in the viewer's browser, calls `propsense/dashboard/resolve`, and builds the dashboard from the answer, so no dashboard layout is stored. See [Dashboards](dashboards.md).
