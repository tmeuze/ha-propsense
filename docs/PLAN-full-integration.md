# Plan: PropSense as a full integration

Branch: `feat/full-integration`. Status: **proposal, nothing implemented.**

## Goals

1. Rules select entities by labels and metadata; **actions** do something with the selection. Exposure to Assist/Alexa/Google is the first action, not a special case.
2. A panel UI (sidebar, admin only) replaces the options-flow menu as the main way to manage rules.
3. A small, versioned Python API lets other integrations (ha-unity: "grant to child instance") register action types and reuse the tagging/rules logic.
4. Existing 0.1 behaviour and safety semantics are unchanged (38 tests keep passing).

## 1. Engine and action model

Today a `Rule` hardcodes `assistants`. New shape:

```
Rule: id, name, enabled, include: Selector, exclude: Selector,
      actions: [ {type: "expose", config: {assistants: [...]}}, ... ]
```

Legacy rules (`assistants` key) migrate on load to one `expose` action. Selector semantics are unchanged (any-of within a field, and across fields, empty matches nothing, exclude is per rule).

### Two action modes

| Mode | Meaning | Examples |
|---|---|---|
| `state` | Reconciled: propsense computes the desired entity set per *target* and the provider makes reality match. Anything unselected is removed, the single-source-of-truth rule. | expose to assistant, grant to child instance |
| `edge` | Fires when an entity *enters* or *leaves* the selection. Propsense persists the last selection so restarts don't re-fire. | add a label, set voice aliases, call a service |

A **target** is what the action config names (an assistant, a child instance id). Propsense unions the selected entities of all rules that name the same (action type, target), then diffs against the provider's `async_current(target)`.

### What the core does so providers don't have to

Dry run, the per-target `max_exposed`-style size guard and its Repairs issue, debounce and triggers, blocked domains, per-rule reporting, "why is this entity selected" explanations, and diagnostics.

## 2. Extension API (for ha-unity)

Module `custom_components/propsense/api.py`, `API_VERSION = 1`:

```python
class ActionType(Protocol):
    type_id: str                      # "unity.grant"
    name: str
    mode: Literal["state", "edge"]
    respects_blocked_domains: bool    # default True
    def config_schema(self) -> vol.Schema: ...      # also drives the UI form
    def targets(self, config) -> set[str]: ...
    async def async_current(self, target) -> set[str]: ...          # state mode
    async def async_apply(self, target, add: set[str], remove: set[str], *, dry_run: bool) -> None: ...

def async_register_action(hass, action: ActionType) -> Callable[[], None]   # returns unregister
```

- Registration happens in propsense's `async_setup` (not per entry), so a provider declares `dependencies: ["propsense"]` and registers in its own setup.
- Rules naming an unregistered type are kept but **dormant**: reported as unavailable, never applied. A missing provider must not cause removals, so unexposing/revoking only happens while the provider is present.
- Events: `propsense_plan_updated` (bus) with a summary, and the same data over the websocket API.
- Contract tests use a fake provider, so ha-unity's needs are pinned without depending on it.

## 3. Storage

Rules move from `entry.options` to `helpers.storage.Store` (`propsense.rules`, versioned, with a migration from options). Reason: the panel edits rules over websocket, rules grow, and options updates trigger entry reloads. Settings stay in options. The options flow shrinks to settings plus a pointer to the panel until the panel reaches parity, then it is trimmed.

## 4. Websocket API

All admin only, under `propsense/`:
`rules/list|create|update|delete`, `settings/get|update`, `actions/list` (types, modes, serialized schemas), `preview` (plan for saved rules or a draft rule, with per-entity reasons), `explain` (why entity X is or isn't selected), `status`, `resync`.

## 5. Panel UI

- Registered with `panel_custom` (`require_admin=True`, sidebar "Properties Sense"). Note: "ingress" is an add-on concept. A custom panel gives the same result for an integration.
- Lit web component. Built bundle committed under `custom_components/propsense/frontend/` so HACS installs need no build step. Sources and build in `frontend/` at the repo root (Vite).
- Reuses HA's own `ha-selector` and pickers for labels, areas, floors, entities and devices.
- Screens: rule list (selector summaries, match count, enable toggle), rule editor (include/exclude, actions with forms from `config_schema`, live preview), settings, status and dry-run diff, entity explainer.

## 6. Phases (each ends green and commits on the branch)

1. **Core refactor:** `Rule.actions`, registry, state/edge modes, expose as the first provider, Store plus migration. All existing tests pass, new engine/registry tests.
2. **Websocket API and services**, with tests in the HA harness.
3. **Panel UI:** skeleton, rule CRUD, live preview, explainer.
4. **Extension API docs and fake-provider contract tests.**
5. **Release 0.2:** README update, CI (including a frontend build check), live install per the dry-run procedure.

Later: built-in edge actions (labels, aliases, call service), YAML import/export, token budget display.

## Decisions (2026-10-21)

1. Rules move to `Store`. Agreed.
2. Lit + Vite with a committed bundle. Agreed.
3. Third-party actions are **opt-in**: an integration option "Allow third-party actions" (off by default) with a warning that providers can change things beyond exposure. Dormant until enabled. Blocked domains still apply unless a type opts out and the option is on.
4. Name stays "PropSense", domain `propsense`.
5. Publish and install via HACS so updates are easy. Publishing is **step 0**: tag a `v0.1.0` release of what exists now, install it in a dry-run, then ship the phases below as later releases. Pushing and tagging need the user's go-ahead.
