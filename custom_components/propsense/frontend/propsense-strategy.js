/*
 * PropSense dashboard strategy.
 *
 * Use it in a dashboard's raw configuration:
 *
 *   strategy:
 *     type: custom:propsense
 *     dashboard: guest        # the name used by "Show on a dashboard" actions
 *     title: Guest            # optional
 *
 * Home Assistant calls generate() each time the dashboard loads. The sections come
 * from PropSense's rules (propsense/dashboard/resolve), already filtered to what this
 * user's audience may see, so the dashboard cannot drift from the rules.
 *
 * Loaded for every user, so it is plain JavaScript with no dependencies.
 */
class PropSenseDashboardStrategy extends HTMLElement {
  static async generate(config, hass) {
    const name = config.dashboard;
    if (!name) {
      return PropSenseDashboardStrategy._message(
        config,
        "Set `dashboard:` in the strategy to the name used by your PropSense rules."
      );
    }
    let result;
    try {
      result = await hass.callWS({ type: "propsense/dashboard/resolve", dashboard: name });
    } catch (err) {
      return PropSenseDashboardStrategy._message(
        config,
        `PropSense could not be reached: ${err && err.message ? err.message : err}`
      );
    }
    const sections = result.sections || [];
    if (!sections.length) {
      return PropSenseDashboardStrategy._message(
        config,
        `No rule shows anything on the “${name}” dashboard for you yet.`
      );
    }
    const views = sections.map((section, index) => ({
      title: section.title,
      path: PropSenseDashboardStrategy._path(section.title, index),
      type: "sections",
      max_columns: 4,
      sections: section.groups
        .filter((group) => group.entities.length)
        .map((group) => ({
          type: "grid",
          cards: [
            ...(group.name
              ? [{ type: "heading", heading: group.name, heading_style: "subtitle" }]
              : []),
            ...group.entities.map((entity) => ({ type: "tile", entity })),
          ],
        })),
    }));
    return { title: config.title || "PropSense", views };
  }

  static _path(title, index) {
    const slug = String(title).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    return slug || `section-${index + 1}`;
  }

  static _message(config, text) {
    return {
      title: config.title || "PropSense",
      views: [
        {
          title: "PropSense",
          path: "propsense",
          type: "sections",
          sections: [{ type: "grid", cards: [{ type: "markdown", content: text }] }],
        },
      ],
    };
  }
}

if (!customElements.get("ll-strategy-dashboard-propsense")) {
  customElements.define("ll-strategy-dashboard-propsense", PropSenseDashboardStrategy);
}
