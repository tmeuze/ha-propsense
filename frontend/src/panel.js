import { LitElement, html, css, nothing } from "lit";

const SELECTOR_FIELDS = [
  ["labels", "Labels"],
  ["areas", "Areas"],
  ["floors", "Floors"],
  ["domains", "Domains"],
  ["devices", "Devices"],
  ["entities", "Entities"],
  ["groups", "Groups"],
  ["capabilities", "Light capabilities"],
];
const CAPABILITY_OPTIONS = [
  { value: "onoff", label: "On/off only" },
  { value: "brightness", label: "Brightness" },
  { value: "color_temp", label: "White temperature" },
  { value: "color", label: "Color" },
  { value: "white", label: "White channel" },
];
// The engine also matches device classes; the editor keeps them untouched.
const KEEP_FIELDS = ["device_classes"];
const TOKENS_PER_ENTITY = 26;
const TABS = [
  ["rules", "Rules"],
  ["status", "Status"],
  ["explain", "Explain"],
  ["settings", "Settings"],
];

const emptySelector = () =>
  Object.fromEntries([...SELECTOR_FIELDS.map(([k]) => k), ...KEEP_FIELDS].map((k) => [k, []]));

const newRule = () => ({
  name: "",
  enabled: true,
  include: emptySelector(),
  exclude: emptySelector(),
  actions: [{ type: "expose", config: { assistants: ["conversation"] } }],
});

const isEmptySel = (sel) => !Object.values(sel || {}).some((v) => v && v.length);

// Home Assistant lazy-loads its pickers; make sure they exist before we use them.
async function loadHaComponents() {
  try {
    if (customElements.get("ha-selector") && customElements.get("ha-form")) return;
    const helpers = await window.loadCardHelpers?.();
    const card = await helpers?.createCardElement({ type: "entities", entities: [] });
    await card?.constructor?.getConfigElement?.();
  } catch (_) {
    /* fall through: components may already be available */
  }
}

class PropSensePanel extends LitElement {
  static properties = {
    hass: { attribute: false },
    narrow: { type: Boolean },
    panel: { attribute: false },
    _tab: { state: true },
    _data: { state: true },
    _error: { state: true },
    _busy: { state: true },
    _editing: { state: true },
    _preview: { state: true },
    _applyResult: { state: true },
    _explain: { state: true },
    _explainEntity: { state: true },
    _settingsDraft: { state: true },
    _showAll: { state: true },
  };

  constructor() {
    super();
    this._tab = "rules";
    this._data = null;
    this._error = "";
    this._busy = false;
    this._editing = null;
    this._preview = null;
    this._applyResult = null;
    this._explain = null;
    this._explainEntity = "";
    this._settingsDraft = null;
    this._showAll = false;
    this._previewTimer = null;
  }

  async connectedCallback() {
    super.connectedCallback();
    await loadHaComponents();
    await Promise.all([this._load(), this._loadNames()]);
  }

  // ------------------------------------------------------------------ data

  _ws(msg) {
    return this.hass.callWS(msg);
  }

  async _load() {
    try {
      this._data = await this._ws({ type: "propsense/overview" });
      this._settingsDraft = { ...this._data.settings };
      this._error = "";
    } catch (err) {
      this._error = err.message || String(err);
    }
  }

  async _run(fn) {
    this._busy = true;
    try {
      await fn();
      this._error = "";
    } catch (err) {
      this._error = err.message || String(err);
    } finally {
      this._busy = false;
    }
  }

  // ---------------------------------------------------------------- names

  // The frontend only fills hass.labels/areas/floors once something subscribes,
  // so fetch the registries ourselves for display names.
  async _loadNames() {
    this._names = { labels: {}, areas: {}, floors: {} };
    const calls = [
      ["labels", "config/label_registry/list", "label_id"],
      ["areas", "config/area_registry/list", "area_id"],
      ["floors", "config/floor_registry/list", "floor_id"],
    ];
    await Promise.all(
      calls.map(async ([key, type, idKey]) => {
        try {
          for (const item of await this._ws({ type })) this._names[key][item[idKey]] = item.name;
        } catch (_) {
          /* fall back to ids */
        }
      })
    );
    this.requestUpdate();
  }

  _labelName(id) {
    return this._names?.labels?.[id] ?? this.hass.labels?.[id]?.name ?? id;
  }
  _areaName(id) {
    return this._names?.areas?.[id] ?? this.hass.areas?.[id]?.name ?? id;
  }
  _floorName(id) {
    return this._names?.floors?.[id] ?? this.hass.floors?.[id]?.name ?? id;
  }
  _deviceName(id) {
    const d = this.hass.devices?.[id];
    return d?.name_by_user || d?.name || id;
  }
  _entityName(id) {
    return this.hass.states?.[id]?.attributes?.friendly_name || id;
  }
  _valueName(field, v) {
    switch (field) {
      case "labels":
        return this._labelName(v);
      case "areas":
        return this._areaName(v);
      case "floors":
        return this._floorName(v);
      case "devices":
        return this._deviceName(v);
      case "capabilities":
        return CAPABILITY_OPTIONS.find((o) => o.value === v)?.label ?? v;
      case "entities":
      case "groups":
        return this._entityName(v);
      default:
        return v;
    }
  }
  _targetName(type, target) {
    const a = this._data?.assistants?.find((x) => x.value === target);
    return type === "expose" && a ? a.label : target;
  }
  _typeName(type) {
    return this._data?.actions?.find((a) => a.type === type)?.name || type;
  }

  _summarise(sel) {
    const parts = SELECTOR_FIELDS.filter(([k]) => sel?.[k]?.length).map(
      ([k, label]) => `${label}: ${sel[k].map((v) => this._valueName(k, v)).join(", ")}`
    );
    return parts.length ? parts.join(" · ") : "";
  }

  // ----------------------------------------------------------------- rules

  _countFor(rule) {
    const n = this._data?.last?.rules?.[rule.name];
    return n === undefined ? "–" : n;
  }

  async _toggle(rule) {
    await this._run(async () => {
      await this._ws({
        type: "propsense/rule/save",
        rule: { ...rule, enabled: !rule.enabled },
      });
      await this._applyAfterChange();
    });
  }

  async _delete(rule) {
    if (!confirm(`Delete the rule "${rule.name}"?`)) return;
    await this._run(async () => {
      await this._ws({ type: "propsense/rule/delete", rule_id: rule.id });
      await this._applyAfterChange();
    });
  }

  async _applyAfterChange() {
    // Saving a rule applies it (unless dry run is on) so the panel shows the truth.
    await this._ws({ type: "propsense/apply", dry_run: false });
    await this._load();
  }

  _edit(rule) {
    this._editing = JSON.parse(JSON.stringify(rule || newRule()));
    for (const key of ["include", "exclude"]) {
      this._editing[key] = { ...emptySelector(), ...this._editing[key] };
    }
    this._preview = null;
    this._showAll = false;
    this._schedulePreview();
  }

  _setEditing(patch) {
    this._editing = { ...this._editing, ...patch };
    this._schedulePreview();
  }

  _setSelector(which, field, value) {
    this._setEditing({
      [which]: { ...this._editing[which], [field]: value || [] },
    });
  }

  _schedulePreview() {
    clearTimeout(this._previewTimer);
    this._previewTimer = setTimeout(() => this._runPreview(), 400);
  }

  async _runPreview() {
    if (!this._editing) return;
    const rule = this._cleanRule();
    if (!rule.name) rule.name = "(draft)";
    try {
      this._preview = await this._ws({ type: "propsense/preview", rule });
    } catch (err) {
      this._preview = { error: err.message || String(err) };
    }
  }

  _cleanRule() {
    const { id, name, enabled, include, exclude, actions } = this._editing;
    return {
      ...(id ? { id } : {}),
      name: (name || "").trim(),
      enabled,
      include,
      exclude,
      actions,
    };
  }

  async _save() {
    const rule = this._cleanRule();
    if (!rule.name) {
      this._error = "Give the rule a name.";
      return;
    }
    await this._run(async () => {
      await this._ws({ type: "propsense/rule/save", rule });
      this._editing = null;
      await this._applyAfterChange();
    });
  }

  _addAction() {
    const type =
      this._data.actions.find((a) => a.available)?.type || this._data.actions[0].type;
    const defaults = this._defaultConfig(type);
    this._setEditing({
      actions: [...this._editing.actions, { type, config: defaults }],
    });
  }

  _defaultConfig(type) {
    const schema = this._data.actions.find((a) => a.type === type)?.schema || [];
    return Object.fromEntries(
      schema.filter((f) => f.default !== undefined).map((f) => [f.name, f.default])
    );
  }

  _setAction(i, patch) {
    const actions = this._editing.actions.map((a, j) => (i === j ? { ...a, ...patch } : a));
    this._setEditing({ actions });
  }

  _removeAction(i) {
    this._setEditing({ actions: this._editing.actions.filter((_, j) => j !== i) });
  }

  // ---------------------------------------------------------------- render

  render() {
    if (!this._data && !this._error) return html`<div class="loading">Loading…</div>`;
    return html`
      <div class="toolbar">
        ${this.narrow ? html`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>` : nothing}
        <div class="title">PropSense</div>
      </div>
      <div class="tabs">
        ${TABS.map(
          ([id, label]) => html`<button
            class="tab ${this._tab === id ? "active" : ""}"
            @click=${() => (this._tab = id)}
          >${label}</button>`
        )}
      </div>
      <div class="content">
        ${this._error ? html`<div class="error">${this._error}</div>` : nothing}
        ${this._data ? this._renderTab() : nothing}
      </div>
    `;
  }

  _renderTab() {
    if (this._editing && this._tab === "rules") return this._renderEditor();
    switch (this._tab) {
      case "status":
        return this._renderStatus();
      case "explain":
        return this._renderExplain();
      case "settings":
        return this._renderSettings();
      default:
        return this._renderRules();
    }
  }

  _renderRules() {
    const { rules, settings } = this._data;
    return html`
      ${!rules.length && !settings.dry_run
        ? html`<div class="notice warn">
            <b>Start with a dry run.</b> Rules are the single source of truth: with no rules,
            everything an assistant PropSense manages can see is un-exposed on the next apply.
            <button @click=${() => this._setDryRun(true)}>Turn on dry run</button>
          </div>`
        : nothing}
      ${settings.dry_run
        ? html`<div class="notice">
            Dry run is on: rules are evaluated but nothing is applied.
            <button @click=${() => this._setDryRun(false)}>Turn off</button>
          </div>`
        : nothing}
      <div class="row">
        <h2>Rules</h2>
        <button class="primary" @click=${() => this._edit(null)}>Add rule</button>
      </div>
      ${rules.length
        ? rules.map((rule) => this._renderRuleCard(rule))
        : html`<p class="muted">No rules yet. A rule selects entities, for example everything labelled
            “Expose: Novak”, and applies actions such as exposing them to Assist.</p>`}
    `;
  }

  async _setDryRun(on) {
    await this._run(async () => {
      await this._ws({ type: "propsense/settings/update", settings: { dry_run: on } });
      // settings changes reload the integration; give it a moment, then refetch
      await new Promise((r) => setTimeout(r, 1500));
      await this._load();
    });
  }

  _renderRuleCard(rule) {
    const include = this._summarise(rule.include);
    const exclude = this._summarise(rule.exclude);
    const dormant = this._data.last?.dormant?.[rule.name];
    return html`<ha-card class="rule ${rule.enabled ? "" : "off"}">
      <div class="rule-head">
        <div>
          <div class="rule-name">${rule.name}</div>
          <div class="muted">
            ${rule.actions.map((a) => this._typeName(a.type)).join(", ") || "No actions"}
            · ${this._countFor(rule)} entities
          </div>
        </div>
        <div class="rule-actions">
          <label class="switch" title="Enable or disable">
            <input type="checkbox" .checked=${rule.enabled} @change=${() => this._toggle(rule)} />
            ${rule.enabled ? "On" : "Off"}
          </label>
          <button @click=${() => this._edit(rule)}>Edit</button>
          <button class="danger" @click=${() => this._delete(rule)}>Delete</button>
        </div>
      </div>
      <div class="sel">${include || html`<span class="warn-text">Selects nothing (no include fields).</span>`}</div>
      ${exclude ? html`<div class="sel muted">Except: ${exclude}</div>` : nothing}
      ${dormant
        ? html`<div class="warn-text">Dormant action: ${dormant.join(", ")}. Needs a provider and “Allow third-party actions”.</div>`
        : nothing}
    </ha-card>`;
  }

  // ---------------------------------------------------------------- editor

  _selectorFor(field) {
    switch (field) {
      case "labels":
        return { label: { multiple: true } };
      case "areas":
        return { area: { multiple: true } };
      case "floors":
        return { floor: { multiple: true } };
      case "devices":
        return { device: { multiple: true } };
      case "entities":
      case "groups":
        return { entity: { multiple: true } };
      case "capabilities":
        return { select: { multiple: true, options: CAPABILITY_OPTIONS } };
      default: {
        const domains = [...new Set(Object.keys(this.hass.states).map((e) => e.split(".")[0]))].sort();
        return { select: { multiple: true, custom_value: true, options: domains } };
      }
    }
  }

  _renderSelectorFields(which) {
    const sel = this._editing[which];
    return SELECTOR_FIELDS.map(
      ([field, label]) => html`<div class="field">
        <div class="label">${label}</div>
        <ha-selector
          .hass=${this.hass}
          .selector=${this._selectorFor(field)}
          .value=${sel[field] || []}
          @value-changed=${(ev) => this._setSelector(which, field, ev.detail.value)}
        ></ha-selector>
      </div>`
    );
  }

  _renderEditor() {
    const r = this._editing;
    return html`
      <div class="row">
        <h2>${r.id ? "Edit rule" : "New rule"}</h2>
        <div>
          <button @click=${() => (this._editing = null)}>Cancel</button>
          <button class="primary" ?disabled=${this._busy} @click=${this._save}>Save</button>
        </div>
      </div>
      <div class="editor">
        <div class="col">
          <ha-card class="pad">
            <div class="field">
              <div class="label">Name</div>
              <input
                type="text"
                .value=${r.name}
                placeholder="For example: Novak voice"
                @input=${(e) => this._setEditing({ name: e.target.value })}
              />
            </div>
            <label class="check">
              <input type="checkbox" .checked=${r.enabled}
                @change=${(e) => this._setEditing({ enabled: e.target.checked })} />
              Enabled
            </label>
          </ha-card>

          <ha-card class="pad">
            <h3>Include</h3>
            <p class="muted">Every field you fill in must match (and); within a field any value will do (or).</p>
            ${this._renderSelectorFields("include")}
          </ha-card>

          <ha-card class="pad">
            <details ?open=${!isEmptySel(r.exclude)}>
              <summary>Exclude (optional)</summary>
              <p class="muted">Entities matching all the fields you fill in here are removed from this rule.</p>
              ${this._renderSelectorFields("exclude")}
            </details>
          </ha-card>

          <ha-card class="pad">
            <div class="row"><h3>Actions</h3>
              <button @click=${this._addAction}>Add action</button></div>
            ${r.actions.length
              ? r.actions.map((a, i) => this._renderAction(a, i))
              : html`<p class="warn-text">No actions: this rule does nothing.</p>`}
          </ha-card>
        </div>
        <div class="col">${this._renderPreview()}</div>
      </div>
    `;
  }

  _renderAction(action, i) {
    const types = this._data.actions;
    const current = types.find((t) => t.type === action.type);
    const labelFor = (schema) => (this._labels[schema.name] ?? schema.name.replaceAll("_", " "));
    return html`<div class="action">
      <div class="row">
        <select @change=${(e) => this._setAction(i, { type: e.target.value, config: this._defaultConfig(e.target.value) })}>
          ${types.map(
            (t) => html`<option value=${t.type} ?selected=${t.type === action.type} ?disabled=${!t.available && t.type !== action.type}>
              ${t.name}${t.available ? "" : " (enable third-party actions)"}
            </option>`
          )}
          ${current ? nothing : html`<option selected>${action.type} (not installed)</option>`}
        </select>
        <button class="danger" @click=${() => this._removeAction(i)}>Remove</button>
      </div>
      ${current
        ? html`${current.available ? nothing : html`<div class="warn-text">Dormant until third-party actions are allowed in Settings.</div>`}
          <ha-form
            .hass=${this.hass}
            .schema=${current.schema}
            .data=${action.config}
            .computeLabel=${labelFor}
            @value-changed=${(e) => this._setAction(i, { config: e.detail.value })}
          ></ha-form>`
        : html`<div class="warn-text">This action type is not installed, so the rule is dormant.</div>`}
    </div>`;
  }

  _labels = {
    assistants: "Expose to",
    group: "Existing group (to edit)",
    create_name: "Or create a group named",
    group_type: "Type of group to create",
  };

  _renderPreview() {
    const p = this._preview;
    const r = this._editing;
    return html`<ha-card class="pad sticky">
      <h3>Live preview</h3>
      ${isEmptySel(r.include)
        ? html`<p class="warn-text">Selects nothing: fill in at least one include field.</p>`
        : nothing}
      ${!p
        ? html`<p class="muted">Working…</p>`
        : p.error
          ? html`<p class="warn-text">${p.error}</p>`
          : this._renderPreviewBody(p)}
    </ha-card>`;
  }

  _renderPreviewBody(p) {
    const draft = p.draft;
    const entities = draft?.entities || [];
    const shown = this._showAll ? entities : entities.slice(0, 25);
    const expose = this._editing.actions.some((a) => a.type === "expose");
    return html`
      <div class="big">${draft?.count ?? 0} <span class="muted">entities selected</span></div>
      ${expose
        ? html`<div class="muted">About ${(draft?.count ?? 0) * TOKENS_PER_ENTITY} prompt tokens if exposed to an LLM agent.</div>`
        : nothing}
      ${Object.entries(p.assistants || {}).map(
        ([a, r]) => r.refused
          ? html`<div class="warn-text">${this._targetName("expose", a)}: over the size limit, nothing would change.</div>`
          : nothing
      )}
      ${p.blocked && Object.keys(p.blocked).length
        ? html`<div class="warn-text">Skipped: ${Object.entries(p.blocked).map(([e, why]) => `${e} (${why})`).join("; ")}</div>`
        : nothing}
      <ul class="entities">
        ${shown.map((e) => html`<li><span>${e.name}</span> <span class="muted">${e.entity_id}</span></li>`)}
      </ul>
      ${entities.length > shown.length
        ? html`<button @click=${() => (this._showAll = true)}>Show all ${entities.length}</button>`
        : nothing}
    `;
  }

  // ---------------------------------------------------------------- status

  _renderStatus() {
    const last = this._data.last;
    const result = this._applyResult || last;
    return html`
      <div class="row">
        <h2>Status</h2>
        <div>
          <button ?disabled=${this._busy} @click=${() => this._apply(true)}>Dry run</button>
          <button class="primary" ?disabled=${this._busy} @click=${() => this._apply(false)}>Apply now</button>
        </div>
      </div>
      ${this._data.settings.dry_run ? html`<div class="notice">Dry run is on: “Apply now” changes nothing.</div>` : nothing}
      ${!result
        ? html`<p class="muted">Nothing has been applied yet.</p>`
        : html`
            <p class="muted">${result.dry_run ? "Dry run" : "Last applied"} ${new Date(result.at).toLocaleString()}</p>
            ${this._renderTargets("expose", result.assistants)}
            ${Object.entries(result.actions || {}).map(([t, targets]) => this._renderTargets(t, targets))}
            ${Object.keys(result.dormant || {}).length
              ? html`<div class="notice warn">Dormant rules: ${Object.entries(result.dormant)
                  .map(([r, t]) => `${r} (${t.join(", ")})`).join("; ")}</div>`
              : nothing}
            ${Object.keys(result.blocked || {}).length
              ? html`<div class="notice">Skipped (matched a rule but never applied): ${Object.entries(result.blocked).map(([e, why]) => `${e} (${why})`).join("; ")}</div>`
              : nothing}
          `}
    `;
  }

  _renderTargets(type, targets) {
    return Object.entries(targets || {}).map(
      ([target, r]) => html`<ha-card class="pad">
        <div class="row">
          <div><b>${this._typeName(type)}</b> → ${this._targetName(type, target)}</div>
          <div>${r.count} entities${type === "expose" ? html` · ~${r.estimated_tokens} tokens` : nothing}</div>
        </div>
        ${r.refused ? html`<div class="warn-text">Refused: over the size limit. Nothing was changed.</div>` : nothing}
        ${r.error ? html`<div class="warn-text">Error: ${r.error}</div>` : nothing}
        ${r.added?.length ? html`<div>Adds ${r.added.length}: <span class="muted">${r.added.join(", ")}</span></div>` : nothing}
        ${r.removed?.length ? html`<div>Removes ${r.removed.length}: <span class="muted">${r.removed.join(", ")}</span></div>` : nothing}
      </ha-card>`
    );
  }

  async _apply(dry) {
    await this._run(async () => {
      const result = await this._ws({ type: "propsense/apply", dry_run: dry });
      this._applyResult = dry ? result : null;
      await this._load();
    });
  }

  // --------------------------------------------------------------- explain

  _renderExplain() {
    const ex = this._explain;
    return html`
      <h2>Explain an entity</h2>
      <p class="muted">Pick an entity to see which rules select it, and why not.</p>
      <ha-selector
        .hass=${this.hass}
        .selector=${{ entity: {} }}
        .value=${this._explainEntity}
        @value-changed=${(e) => this._doExplain(e.detail.value)}
      ></ha-selector>
      ${ex && !ex.found
        ? html`<p class="warn-text">PropSense doesn't know this entity (it may be disabled).</p>`
        : nothing}
      ${ex?.found ? html`
        <ha-card class="pad">
          <div><b>Labels</b>: ${ex.labels.map((l) => this._labelName(l)).join(", ") || "none"}</div>
          <div><b>Area</b>: ${ex.area_id ? this._areaName(ex.area_id) : "none"}
            · <b>Floor</b>: ${ex.floor_id ? this._floorName(ex.floor_id) : "none"}</div>
          <div><b>Groups</b>: ${ex.groups.map((g) => this._entityName(g)).join(", ") || "none"}</div>
        </ha-card>
        ${ex.rules.length ? ex.rules.map((r) => html`<ha-card class="pad">
          <div class="row"><b>${r.name}</b>
            <span class="muted">${!r.enabled ? "disabled" : r.included ? (r.excluded ? "matches, but excluded" : "included") : "not included"}</span></div>
          ${r.actions.map((a) => html`<div>${this._typeName(a.type)}
            ${a.targets.length ? html`→ ${a.targets.map((t) => this._targetName(a.type, t)).join(", ")}` : nothing}:
            <b class=${a.status === "applies" ? "ok" : "muted"}>${a.status}</b></div>`)}
        </ha-card>`) : html`<p class="muted">No rules.</p>`}` : nothing}
    `;
  }

  async _doExplain(entityId) {
    this._explainEntity = entityId;
    if (!entityId) {
      this._explain = null;
      return;
    }
    await this._run(async () => {
      this._explain = await this._ws({ type: "propsense/explain", entity_id: entityId });
    });
  }

  // -------------------------------------------------------------- settings

  _setSetting(key, value) {
    this._settingsDraft = { ...this._settingsDraft, [key]: value };
  }

  _renderSettings() {
    const s = this._settingsDraft;
    const domains = [...new Set(Object.keys(this.hass.states).map((e) => e.split(".")[0]))].sort();
    const check = (key, label, help) => html`<label class="check">
      <input type="checkbox" .checked=${!!s[key]} @change=${(e) => this._setSetting(key, e.target.checked)} />
      <span>${label}${help ? html`<div class="muted">${help}</div>` : nothing}</span>
    </label>`;
    return html`
      <div class="row">
        <h2>Settings</h2>
        <button class="primary" ?disabled=${this._busy} @click=${this._saveSettings}>Save</button>
      </div>
      <ha-card class="pad">
        <div class="field">
          <div class="label">Managed assistants</div>
          <p class="muted">For these, anything no rule selects is un-exposed, including entities ticked by hand.</p>
          ${this._data.assistants.map((a) => html`<label class="check">
            <input type="checkbox" .checked=${s.managed_assistants.includes(a.value)}
              @change=${(e) => this._setSetting("managed_assistants",
                e.target.checked ? [...new Set([...s.managed_assistants, a.value])]
                  : s.managed_assistants.filter((x) => x !== a.value))} />
            ${a.label}</label>`)}
        </div>
        <div class="field">
          <div class="label">Blocked domains</div>
          <p class="muted">Never exposed, even if a rule lists them explicitly.</p>
          <ha-selector .hass=${this.hass}
            .selector=${{ select: { multiple: true, custom_value: true, options: domains } }}
            .value=${s.blocked_domains}
            @value-changed=${(e) => this._setSetting("blocked_domains", e.detail.value || [])}></ha-selector>
        </div>
        <div class="field">
          <div class="label">Maximum exposed per assistant</div>
          <p class="muted">If a plan would exceed this, nothing changes and a repair issue is raised. 0 disables the guard.</p>
          <input type="number" min="0" .value=${String(s.max_exposed)}
            @input=${(e) => this._setSetting("max_exposed", Math.max(0, parseInt(e.target.value || "0", 10)))} />
        </div>
        ${check("inherit_device_labels", "Entities inherit their device's labels")}
        ${check("inherit_area_labels", "Entities inherit their area's labels")}
        ${check("dry_run", "Dry run", "Compute and report the plan without applying it.")}
        ${check("allow_third_party_actions", "Allow third-party actions",
          "Warning: other integrations can register actions that change things beyond voice exposure, such as granting entities to other Home Assistant instances. Rules using them stay dormant until this is on. Only enable it for integrations you trust.")}
      </ha-card>
    `;
  }

  async _saveSettings() {
    await this._run(async () => {
      await this._ws({ type: "propsense/settings/update", settings: this._settingsDraft });
      await new Promise((r) => setTimeout(r, 1500)); // the integration reloads
      await this._load();
    });
  }

  // ---------------------------------------------------------------- styles

  static styles = css`
    :host { display: block; min-height: 100vh; background: var(--primary-background-color); color: var(--primary-text-color); font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
    .toolbar { display: flex; align-items: center; height: 56px; padding: 0 16px; background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); }
    .title { font-size: 20px; margin-left: 8px; }
    .tabs { display: flex; gap: 4px; padding: 0 12px; border-bottom: 1px solid var(--divider-color); background: var(--card-background-color); overflow-x: auto; }
    .tab { background: none; border: none; border-bottom: 2px solid transparent; padding: 12px 14px; color: var(--secondary-text-color); font: inherit; cursor: pointer; }
    .tab.active { color: var(--primary-color); border-bottom-color: var(--primary-color); }
    .content { max-width: 1100px; margin: 0 auto; padding: 16px; box-sizing: border-box; }
    h2 { margin: 8px 0; font-weight: 500; } h3 { margin: 0 0 8px; font-weight: 500; }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .muted { color: var(--secondary-text-color); font-size: 0.9em; }
    .warn-text { color: var(--warning-color, #b26a00); margin: 6px 0; }
    .ok { color: var(--success-color, #2e7d32); }
    .error { background: var(--error-color, #c62828); color: #fff; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
    .notice { padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; background: var(--secondary-background-color); }
    .notice.warn { border-left: 4px solid var(--warning-color, #ff9800); }
    .notice button { margin-left: 8px; }
    ha-card { display: block; margin-bottom: 12px; }
    .pad { padding: 16px; }
    .rule { padding: 14px 16px; }
    .rule.off { opacity: 0.6; }
    .rule-head { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .rule-name { font-size: 1.1em; font-weight: 500; }
    .rule-actions { display: flex; align-items: center; gap: 8px; }
    .sel { margin-top: 8px; }
    .editor { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 16px; }
    @media (max-width: 800px) { .editor { grid-template-columns: 1fr; } }
    .sticky { position: sticky; top: 8px; }
    .field { margin-bottom: 14px; }
    .label { font-weight: 500; margin-bottom: 4px; }
    .check { display: flex; align-items: flex-start; gap: 8px; margin: 10px 0; }
    input[type="text"], input[type="number"], select { width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; }
    input[type="number"] { max-width: 160px; }
    button { padding: 8px 14px; border-radius: 18px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; cursor: pointer; }
    button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }
    button.danger { color: var(--error-color, #c62828); }
    button:disabled { opacity: 0.5; cursor: default; }
    .action { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .action .row select { flex: 1; }
    .big { font-size: 2em; font-weight: 500; }
    .entities { list-style: none; padding: 0; margin: 8px 0; max-height: 360px; overflow: auto; }
    .entities li { display: flex; justify-content: space-between; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--divider-color); }
    .loading { padding: 24px; }
    summary { cursor: pointer; font-weight: 500; }
  `;
}

customElements.define("propsense-panel", PropSensePanel);
