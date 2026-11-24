# Dashboards

The **Show on a dashboard** action puts a rule's entities into a titled section of a named dashboard. Entities can be grouped by area, floor, domain, or not at all.

PropSense stores no dashboard layout. A small dashboard strategy asks PropSense for the current sections every time the dashboard loads, so a change to a rule changes the dashboard, and the same rules produce the same dashboard on any instance.

## Set one up

1. Add a rule with the **Show on a dashboard** action. Give it a dashboard name (for example `guest`), a section title, how to group the entities, and an audience.
2. Create a dashboard in Settings, Dashboards, Add. Open it, use the three-dot menu, choose Edit, then the raw configuration editor, and replace the contents with:

```yaml
strategy:
  type: custom:propsense
  dashboard: guest   # the name you gave in the rule
  title: Guest       # optional
```

Each rule section becomes a tab, and each group becomes a block of tiles. If nothing is shown for the person looking, the dashboard says so.

PropSense loads the strategy script for every user, not just administrators, so a guest or kiosk account sees the dashboard too.

## Audiences

An audience says who is shown a section. It is `everyone` (the default), `admins`, `non-admins`, or specific Home Assistant user ids, and you can combine them. A kiosk or guest account that is not an administrator sees only the sections whose audience includes it.

To make a dashboard reachable only by non-admins, also turn off **Require admin** in that dashboard's settings. Whether it shows in the sidebar is up to you.

PropSense never creates users. Audiences use accounts that already exist, which you create in Home Assistant yourself.

## What this does not protect

**An audience is not access control.** A dashboard only chooses what to show. Every logged-in user can still read every entity's state through Home Assistant's API, and Home Assistant has no per-entity permissions. Use audiences for tidy guest and kiosk views. When you need a boundary that is enforced, use the voice expose action, which does limit what an assistant can see.

Logging in by subnet uses the `trusted_networks` provider in `configuration.yaml`. No integration can change that file, so it is outside what PropSense can set up. See Home Assistant's authentication documentation.

## For integrations that push dashboards

Another integration can create the dashboard with Home Assistant's own `lovelace/dashboards/create` and `lovelace/config/save` websocket calls, using the strategy configuration above. PropSense must be installed on that instance, and the rules must exist there as well. The strategy reads them through the `propsense/dashboard/resolve` websocket command, which any logged-in user may call. It returns only entities the caller can already read, filtered by the caller's audience.
