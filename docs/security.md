# Security

This is PropSense's own security posture. To report a vulnerability, open a private security advisory on the GitHub repository.

## Who can do what

- The panel and every administrative websocket command (`propsense/overview`, rule and settings changes, preview, explain, apply) require an administrator.
- `propsense/dashboard/resolve` is open to any logged-in user, because the dashboard strategy runs in their browser. It returns only entity ids the caller can already read through Home Assistant's state API, filtered by each section's audience. It exposes nothing new.
- A rule can run Home Assistant actions (the run action), so anyone who can edit rules can cause actions. That is why editing is restricted to administrators.

## What an audience protects

Audiences on dashboards are a presentation filter. Every logged-in user can still read every state through the API, and Home Assistant has no per-entity permissions. The voice expose action is the only boundary PropSense enforces, and it limits what an assistant can see. See [Dashboards](dashboards.md).

## What leaves your instance

Only the metrics action sends anything out, and only when you have set a Metrics URL and turned on **Allow sending data off this instance**. It sends to that one URL, uses no credentials, and checks the endpoint's TLS certificate without ever relaxing the check. Other actions never send data off the instance.

## Safety limits

- Locks, alarm panels and cameras are blocked by default for every action, even when a rule names them.
- A plan that would expose more than `max_exposed` entities changes nothing and raises a Repairs issue.
- The loop breaker pauses applying when rules keep changing each other's results.
- Third-party actions are off by default, and actions that send data need a second permission.
- A dry run reports the plan without applying anything.

## What PropSense does not touch

It never creates or edits users, never edits `configuration.yaml` or the stored dashboard configuration, and never stores credentials.

## Dependency updates

Dependabot waits 7 days before proposing a release (14 for a major npm or Python version) and proposes security updates immediately. See [decisions](decisions.md) #11 for what this cannot cover.
