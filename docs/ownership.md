# Ownership

For each thing PropSense manages: who controls it, how, and where an edit should be made. The rule that runs through all of it is that PropSense's rules are the single source of truth. A hand edit to something a rule manages is undone on the next apply.

| Thing | Owner | Mechanism | Why | Where to change it | Backup |
|---|---|---|---|---|---|
| Rules | PropSense | Stored in `propsense.rules`, edited in the panel | One place decides every action | The PropSense panel, Rules tab | Home Assistant backups include `.storage` |
| Settings | PropSense | Stored in the config entry options | They apply to every rule | The PropSense panel, Settings tab | Home Assistant backups |
| Assistant exposure (Assist, Alexa, Google) | PropSense, for the assistants it manages | Rewritten on every apply, so anything not selected is un-exposed | Exposure should follow the rules, not ticks made by hand | The rule. Remove an assistant from Managed assistants to hand it back | Home Assistant backups |
| Groups the action manages | PropSense, labelled `[PropSense]` | Members rewritten on every apply | The group should equal the selection | The rule. To stop PropSense managing a group, remove the action from the rule | Home Assistant backups |
| A label from the label action | PropSense | Added to selected entities, removed from the rest, including hand-labelled ones | The label should equal the selection | The rule | Home Assistant backups |
| Voice aliases from the alias action | PropSense | The listed aliases are added and removed. Other aliases are left alone | Only the aliases a rule names are managed | The rule | Home Assistant backups |
| Schedule and timer deadlines | PropSense | Stored as absolute times in `propsense.schedule` | A restart must neither reset nor lose them | The rule | Home Assistant backups |
| Dashboard sections | PropSense | Built live from the rules. Nothing is stored | The dashboard cannot drift from the rules | The rule. The dashboard itself holds only the strategy line | The strategy line is in the dashboard's own configuration |
| The dashboard that uses the strategy | The user | Created and named by you in Home Assistant | PropSense does not edit dashboard storage | Settings, Dashboards | Home Assistant backups |
| Repairs issues | PropSense | Created and cleared on each apply | They report the current state of the rules | Fix the cause, or change the rule | Not backed up, and recreated on the next run |
| The metrics buffer | PropSense | Held in memory only | It is a short retry queue, not a record | Not applicable | Not backed up. A restart loses unsent points |
| Users and their accounts | The user | Created in Home Assistant | PropSense never creates or changes users | Settings, People | Home Assistant backups |
| `configuration.yaml`, including `trusted_networks` | The user | Not touched | No integration can edit it | The file itself | Your own backups |

Nothing in PropSense is synced both ways. Everything flows from the rules outward, and if you want to keep a change you made by hand, you make it in the rule.
