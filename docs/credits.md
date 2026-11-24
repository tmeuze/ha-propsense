# Credits

## Dependencies

| Dependency | Used for | Licence |
|---|---|---|
| [Home Assistant](https://www.home-assistant.io) | The platform. PropSense is an integration for it and uses its registries, storage, issue registry and frontend | Apache 2.0 |
| [Lit](https://lit.dev) | The panel's web component | BSD-3-Clause |
| [esbuild](https://esbuild.github.io) | Bundling the panel (development only) | MIT |
| [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) | Running the tests against a real Home Assistant core (development only) | MIT |
| [home-assistant-frontend](https://github.com/home-assistant/frontend) | Needed by the tests, because the panel integration depends on it (development only) | Apache 2.0 |

PropSense has no runtime Python dependencies beyond Home Assistant, and `manifest.json` lists no requirements.

The panel uses Home Assistant's own form and selector components, so it looks like the rest of the interface.

## Ideas this builds on

Label-based voice exposure and entity filtering already exist in community integrations, and PropSense's approach is shaped by them. It aims to be a general rules engine with one selector model, safety limits and an API other integrations can build on.

## Rejected

- **Writing dashboard configuration to Home Assistant's storage.** It overwrites hand edits and drifts. See [decisions](decisions.md).
- **A general sidebar organizer.** There is no clean extension point in Home Assistant, and the usual approach patches the frontend's DOM, which breaks between releases. See [decisions](decisions.md).
