# Decisions

Significant choices, with what each cost and what would justify revisiting it. Entries are added, not rewritten. If a decision is replaced, the old entry is marked as superseded.

## 1. Rules are the single source of truth

**Chosen:** For every target an action manages, PropSense makes reality equal to what the rules select, and removes the rest.

**Cost:** The first apply of a wrong or empty rule set removes things (for exposure, it un-exposes entities you ticked by hand). A dry run and the size limit exist to soften that.

**Rejected:** Additive-only rules, which never remove anything. They leave the result depending on history, and the same rules would give different outcomes on different instances.

**Revisit if:** Users keep losing hand edits and a per-target "only add" mode proves less confusing than the dry run.

## 2. An empty selector matches nothing

**Chosen:** A rule with no include fields, or only an exclude, selects no entities.

**Cost:** Nobody can write "everything" without naming a field, such as a domain list.

**Rejected:** Treating an empty selector as everything. A half-edited rule could then expose or modify every entity.

## 3. Third-party actions are off by default

**Chosen:** Actions from other integrations stay dormant until the user turns on a setting, with a warning that explains the risk. Actions that send data off the instance need a second permission.

**Cost:** An extra step for people who install an integration that provides actions.

**Rejected:** Trusting any installed integration. An action can change entities or send data, so that should be a deliberate choice.

## 4. No default Metrics URL

**Chosen:** The metrics action has no default URL. The permission to send data cannot be turned on without one.

**Cost:** One more setting to fill in.

**Why:** Versions 0.7.0 to 0.8.1 shipped a default that pointed at the author's own infrastructure. That was wrong for everyone else and exposed private names. Version 0.8.2 removed it and cleared saved copies of it. The Git history still contains the old address, and we chose to fix forward rather than rewrite history.

**Revisit:** Never as a default. Examples and tests use placeholder addresses.

## 5. Dashboards are built live by a strategy, not written to storage

**Chosen:** A dashboard strategy asks PropSense for the sections each time the dashboard loads.

**Cost:** The dashboard cannot be hand edited without taking control of it, which freezes it into an ordinary dashboard. The strategy relies on Home Assistant's custom strategy mechanism.

**Rejected:** Writing dashboard configuration to Home Assistant's storage. It overwrites hand edits, drifts from the rules, and has no stable API for integrations.

**Revisit if:** Home Assistant changes how custom strategies load, or users ask for editable output often enough to justify an export option.

## 6. Audiences are a presentation filter, not access control

**Chosen:** Audiences decide who is shown a dashboard section. Documentation says plainly that this does not restrict access.

**Cost:** It cannot protect anything. Every logged-in user can read all states through the API.

**Why:** Home Assistant has no per-entity permissions, so claiming more would be false. The voice expose action is the only enforced boundary.

## 7. PropSense does not create users

**Chosen:** Audiences take existing user ids. PropSense never creates or edits accounts.

**Why:** Account creation is a decision for the owner of the instance, and the integration that pushes configuration to other instances agreed not to do it either.

## 8. Dashboard and sidebar scope

**Chosen:** PropSense does dashboards driven by rules, with audiences. It does not build a general sidebar organizer.

**Cost:** People who want grouping and colors in the sidebar need another tool.

**Why:** The sidebar is about panels and users, not entities, and Home Assistant offers no clean extension point for it. Tools that restyle it patch the frontend's DOM and break between releases. A narrow feature, a sidebar per audience, might fit later and needs a feasibility check first.

## 9. A loop breaker for rules that chase each other

**Chosen:** If applying changes something 20 times within 60 seconds, PropSense pauses applying for 300 seconds, keeps reporting, and raises a Repairs issue.

**Cost:** A legitimate burst of changes can trigger a pause. The limits are constants and can be raised.

**Why:** Label rules can feed each other, and a loop that runs unattended is worse than a pause.

## 10. Documentation set

**Chosen:** PropSense follows the conformIT documentation standard: README, `AGENTS.md`, `docs/STATE.md`, `docs/decisions.md`, `docs/architecture.md`, `docs/ownership.md`, `docs/security.md`, `docs/credits.md` and a changelog. The deep reference lives under `docs/`, and the README stays short.

**Cost:** More files to keep accurate.
