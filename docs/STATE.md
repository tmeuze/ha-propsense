# Where this got to

Current as of version 0.11.0. Read this first if you are picking the project up.

## What works

All nine built-in actions are implemented and covered by tests (expose, group, schedule, metrics, label, aliases, flag, run and dashboard). The sidebar panel has Rules, Status, Explain and Settings tabs. The dashboard strategy builds dashboards from rules. The loop breaker, dry run and size limit are in place. CI runs hassfest, the HACS check, the test suite and a check that the committed panel bundle is up to date.

## What was verified, and what was not

Verified in a running Home Assistant 2026.10 beta with throwaway local accounts: the panel, the metrics action against a local test endpoint, auto-off timers across a restart, group creation, label, alias and flag actions, the run action, and the dashboard strategy for an administrator.

Not verified:

- Home Assistant 2026.9.x. Everything was tested on the 2026.10 beta. VERIFY before relying on it.
- Sending metrics to a real VictoriaMetrics instance over HTTPS. VERIFY.
- Sunrise and sunset triggers firing in real time. They are covered by tests only.
- The dashboard audiences from a non-admin session in a browser. The filtering is covered by tests, and the websocket command was exercised with a read-only token.
- How the README's embedded diagram renders inside HACS. VERIFY.

## Known gaps

- Audiences take raw user ids, so choosing one in the panel means typing an id. A picker with user names would be better.
- The Python interpreter exits with a segmentation fault at shutdown on the Home Assistant 2026.10 beta with pyenv Python 3.14. It happens with and without PropSense loaded and is not understood. Development instances are stopped with `kill -9`.
- Grant to child instances belongs to ha-unity and is built on the extension API, not in this repository.
- Screenshots of the panel are not in the README yet.
- Conditions on another entity's state and "on for more than an hour" conditions are not supported.

## Ideas, not planned

A sidebar per audience (needs a feasibility check), shared named schedules, media player and humidifier capabilities, and a service action with data for schedules.
