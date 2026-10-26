import { LitElement, html, css, nothing } from "lit";

const SELECTOR_FIELDS = [
  ["labels", "Labels"],
  ["areas", "Areas"],
  ["floors", "Floors"],
  ["domains", "Domains"],
  ["devices", "Devices"],
  ["entities", "Entities"],
  ["groups", "Groups"],
  ["capabilities", "Capabilities"],
  ["integrations", "Integrations"],
  ["manufacturers", "Manufacturers"],
  ["models", "Models"],
  ["entity_categories", "Entity categories"],
  ["name_patterns", "Name or entity id patterns"],
  ["label_patterns", "Label name patterns"],
  ["states", "Current state"],
  ["conditions", "Conditions on state or attributes"],
];
const STATE_FIELDS = ["states", "conditions"];
const STATE_OPTIONS = ["on", "off", "unavailable", "unknown", "open", "closed", "home", "not_home", "locked", "unlocked", "playing", "idle", "paused"];
const OPS = [
  ["<", "is below"], ["<=", "is at most"], [">", "is above"], [">=", "is at least"],
  ["=", "is"], ["!=", "is not"], ["between", "is between"],
];
function parseCond(text) {
  const [src = "state", op = "<", ...rest] = String(text).trim().split(/\s+/);
  const source = src === "state" ? "state" : "attr";
  const attr = src.startsWith("attr:") ? src.slice(5) : "";
  if (op === "between") return { source, attr, op, a: rest[0] || "", b: rest[1] || "" };
  return { source, attr, op, a: rest.join(" "), b: "" };
}
const condComplete = (c) =>
  (c.source === "state" || c.attr.trim()) && String(c.a).trim() && (c.op !== "between" || String(c.b).trim());
const condText = (c) =>
  `${c.source === "state" ? "state" : `attr:${c.attr.trim()}`} ${c.op} ${c.op === "between" ? `${String(c.a).trim()} ${String(c.b).trim()}` : String(c.a).trim()}`;
// Shown under "More filters" so the common ones stay uncluttered.
const ADVANCED_FIELDS = [
  "integrations", "manufacturers", "models", "entity_categories", "name_patterns", "label_patterns",
];
const FIELD_HELP = {
  integrations: "Where the entity comes from, for example hue or zha.",
  manufacturers: "Of the entity's device. Wildcards work: IKEA*.",
  models: "Of the entity's device. Wildcards work.",
  entity_categories: "Primary entities are the ones with no category. Config and diagnostic entities are the extras integrations add.",
  name_patterns: "Matches the entity id or its name, ignoring case. Use * for any text and ? for one character, for example switch.*_plug or *outlet*.",
  label_patterns: "Matches label names, ignoring case, for example Expose: * for every label that starts that way.",
  states: "The entity's state right now, for example on or unavailable. Any of the values will do.",
  conditions: "Matches if any of these hold. The rule re-checks whenever an entity's state changes across a condition.",
};
const CATEGORY_OPTIONS = [
  { value: "primary", label: "Primary (no category)" },
  { value: "config", label: "Config" },
  { value: "diagnostic", label: "Diagnostic" },
];
const CAPABILITY_OPTIONS = [
  { value: "onoff", label: "Light: on/off only" },
  { value: "brightness", label: "Light: brightness" },
  { value: "color_temp", label: "Light: white temperature" },
  { value: "color", label: "Light: color" },
  { value: "white", label: "Light: white channel" },
  { value: "position", label: "Cover: set position" },
  { value: "tilt", label: "Cover: set tilt" },
  { value: "speed", label: "Fan: speed" },
  { value: "oscillate", label: "Fan: oscillate" },
  { value: "direction", label: "Fan: direction" },
  { value: "preset", label: "Fan: preset modes" },
  { value: "heat", label: "Climate: heat" },
  { value: "cool", label: "Climate: cool" },
  { value: "heat_cool", label: "Climate: heat/cool" },
  { value: "auto", label: "Climate: auto" },
  { value: "dry", label: "Climate: dry" },
  { value: "fan_only", label: "Climate: fan only" },
  { value: "target_temp", label: "Climate: target temperature" },
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

const DUR = (hours, minutes = 0) => ({ hours, minutes, seconds: 0 });
const TEMPLATES = [
  {
    id: "auto_off",
    title: "Auto-off timer",
    text: "Turn outlets off after they have been on for a while. Survives restarts and respects manual switching.",
    make: () => ({
      name: "Auto-off outlets",
      include: { domains: ["switch"] },
      actions: [{ type: "schedule", config: { trigger: "state_for", state: "on", do: "turn_off", duration: DUR(3) } }],
    }),
  },
  {
    id: "sunset_on",
    title: "Lights on at sunset",
    text: "Turn lights on at sunset, with an optional offset.",
    make: () => ({
      name: "Lights on at sunset",
      include: { domains: ["light"] },
      actions: [{ type: "schedule", config: { trigger: "sun", event: "sunset", offset_minutes: 0, do: "turn_on", catch_up_minutes: 30 } }],
    }),
  },
  {
    id: "night_off",
    title: "Lights off at night",
    text: "Turn lights off at a set time of day.",
    make: () => ({
      name: "Lights off at night",
      include: { domains: ["light"] },
      actions: [{ type: "schedule", config: { trigger: "time", at: "23:00:00", do: "turn_off", catch_up_minutes: 0 } }],
    }),
  },
  {
    id: "expose",
    title: "Expose to a voice assistant",
    text: "Let Assist, Alexa or Google see the entities with a label.",
    make: () => ({
      name: "Voice assistant exposure",
      include: {},
      actions: [{ type: "expose", config: { assistants: ["conversation"] } }],
    }),
  },
  {
    id: "group",
    title: "Keep a group in sync",
    text: "Fill a group with the entities a rule selects, for example every light with white temperature.",
    make: () => ({
      name: "Dynamic group",
      include: {},
      actions: [{ type: "group", config: { create_name: "", group_type: "light" } }],
    }),
  },
  {
    id: "metrics",
    title: "Ship numeric history",
    text: "Send the numeric history of entities (by label, integration, name…) to your metrics endpoint. Needs the permission in Settings.",
    make: () => ({
      name: "Ship metrics",
      include: {},
      actions: [{ type: "metrics", config: { min_interval_seconds: 60, include_booleans: false, tag_area: true, tag_device_class: true, tag_unit: true, max_entities: 200 } }],
    }),
  },
  { id: "blank", title: "Start from scratch", text: "An empty rule.", make: () => ({}) },
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
    _choosing: { state: true },
    _toastMsg: { state: true },
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
    this._choosing = false;
    this._toastMsg = "";
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

  _toast(msg) {
    this._toastMsg = msg;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => (this._toastMsg = ""), 3500);
  }

  _rel(iso) {
    const ms = new Date(iso).getTime() - Date.now();
    const abs = Math.abs(ms);
    const mins = Math.round(abs / 60000);
    const text = mins >= 60 ? `${Math.floor(mins / 60)} h ${mins % 60} min` : `${mins} min`;
    return ms >= 0 ? `in ${text}` : `${text} ago (waiting)`;
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
      this._toast(rule.enabled ? `Disabled “${rule.name}”` : `Enabled “${rule.name}”`);
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
    this._choosing = false;
    this._condDrafts = null;
    this._editing = { ...newRule(), ...JSON.parse(JSON.stringify(rule || newRule())) };
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
      this._toast(`Saved “${rule.name}”`);
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
      ${this._toastMsg ? html`<div class="toast">${this._toastMsg}</div>` : nothing}
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
        <button class="primary" @click=${() => (this._choosing = !this._choosing)}>Add rule</button>
      </div>
      ${this._choosing ? this._renderChooser() : nothing}
      ${rules.length
        ? rules.map((rule) => this._renderRuleCard(rule))
        : html`<p class="muted">No rules yet. A rule selects entities, for example everything labelled
            “Expose: Novak”, and applies actions such as exposing them to Assist.</p>`}
    `;
  }

  _renderChooser() {
    return html`<div class="templates">
      ${TEMPLATES.map(
        (t) => html`<button class="template" @click=${() => this._edit(t.make())}>
          <div class="rule-name">${t.title}</div>
          <div class="muted">${t.text}</div>
        </button>`
      )}
    </div>`;
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
          <div class="muted">${this._countFor(rule)} ${this._countFor(rule) === 1 ? "entity" : "entities"}</div>
          <ul class="summary">
            ${(this._data.summaries?.[rule.id] || []).map((line) => html`<li>${line}</li>`)}
          </ul>
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
        ? html`<div class="warn-text">Dormant action: ${dormant.join(", ")}. Needs the provider, and the matching permission in Settings.</div>`
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
      case "entity_categories":
        return { select: { multiple: true, options: CATEGORY_OPTIONS } };
      case "integrations":
      case "manufacturers":
      case "models":
        return { select: { multiple: true, custom_value: true, options: this._data?.choices?.[field] || [] } };
      case "name_patterns":
      case "label_patterns":
        return { select: { multiple: true, custom_value: true, options: [] } };
      case "states":
        return { select: { multiple: true, custom_value: true, options: STATE_OPTIONS } };
      default: {
        const domains = [...new Set(Object.keys(this.hass.states).map((e) => e.split(".")[0]))].sort();
        return { select: { multiple: true, custom_value: true, options: domains } };
      }
    }
  }

  _renderSelectorFields(which) {
    const sel = this._editing[which];
    const field = ([name, label]) => html`<div class="field">
      <div class="label">${label}</div>
      ${FIELD_HELP[name] ? html`<div class="muted help">${FIELD_HELP[name]}</div>` : nothing}
      <ha-selector
        .hass=${this.hass}
        .selector=${this._selectorFor(name)}
        .value=${sel[name] || []}
        @value-changed=${(ev) => this._setSelector(which, name, ev.detail.value)}
      ></ha-selector>
    </div>`;
    const main = SELECTOR_FIELDS.filter(([k]) => !ADVANCED_FIELDS.includes(k) && !STATE_FIELDS.includes(k));
    const more = SELECTOR_FIELDS.filter(([k]) => ADVANCED_FIELDS.includes(k));
    const anyMore = more.some(([k]) => sel[k]?.length);
    const anyState = STATE_FIELDS.some((k) => sel[k]?.length);
    const stateField = ([name, label]) => name === "conditions" ? this._renderConditions(which, label) : field([name, label]);
    return html`${main.map(field)}
      <details class="more" ?open=${anyMore}>
        <summary>More filters: integration, manufacturer, name patterns…</summary>
        ${more.map(field)}
      </details>
      <details class="more" ?open=${anyState}>
        <summary>Current state and attributes: battery below 20%, currently on…</summary>
        ${SELECTOR_FIELDS.filter(([k]) => STATE_FIELDS.includes(k)).map(stateField)}
      </details>`;
  }

  _condRows(which) {
    // Rows live here (not only in the rule) so half-filled ones survive edits.
    if (!this._condDrafts) {
      this._condDrafts = {
        include: (this._editing.include.conditions || []).map(parseCond),
        exclude: (this._editing.exclude.conditions || []).map(parseCond),
      };
    }
    return this._condDrafts[which];
  }

  _setCondRows(which, rows) {
    this._condDrafts[which] = rows;
    this._setSelector(which, "conditions", rows.filter(condComplete).map(condText));
  }

  _renderConditions(which, label) {
    const rows = this._condRows(which);
    const edit = (i, patch) => this._setCondRows(which, rows.map((r, j) => (i === j ? { ...r, ...patch } : r)));
    return html`<div class="field">
      <div class="label">${label}</div>
      <div class="muted help">${FIELD_HELP.conditions}</div>
      ${rows.map((r, i) => html`<div class="line cond">
        <select @change=${(e) => edit(i, { source: e.target.value })}>
          <option value="state" ?selected=${r.source === "state"}>State</option>
          <option value="attr" ?selected=${r.source === "attr"}>Attribute</option>
        </select>
        ${r.source === "attr"
          ? html`<input type="text" class="attr" placeholder="battery_level" .value=${r.attr}
              @input=${(e) => edit(i, { attr: e.target.value })} />`
          : nothing}
        <select @change=${(e) => edit(i, { op: e.target.value })}>
          ${OPS.map(([v, t]) => html`<option value=${v} ?selected=${r.op === v}>${t}</option>`)}
        </select>
        <input type="text" class="val" .value=${r.a} placeholder=${r.op === "between" ? "from" : "value"}
          @input=${(e) => edit(i, { a: e.target.value })} />
        ${r.op === "between"
          ? html`<span>and</span><input type="text" class="val" .value=${r.b} placeholder="to"
              @input=${(e) => edit(i, { b: e.target.value })} />`
          : nothing}
        <button class="danger" type="button" @click=${() => this._setCondRows(which, rows.filter((_, j) => j !== i))}>Remove</button>
        ${condComplete(r) ? nothing : html`<span class="warn-text">Incomplete: not used yet.</span>`}
      </div>`)}
      <button type="button" @click=${() => this._setCondRows(which, [...rows, { source: "state", attr: "", op: "<", a: "", b: "" }])}>Add condition</button>
    </div>`;
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
            <h3>1 · What does it apply to?</h3>
            <p class="muted">Every field you fill in must match (and); within a field any value will do (or). The live preview shows what is selected.</p>
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
            <div class="row"><h3>2 · What should happen?</h3>
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
              ${t.name}${t.available ? "" : t.requires === "external_data" ? " (allow sending data in Settings)" : " (enable third-party actions)"}
            </option>`
          )}
          ${current ? nothing : html`<option selected>${action.type} (not installed)</option>`}
        </select>
        <button class="danger" @click=${() => this._removeAction(i)}>Remove</button>
      </div>
      ${action.type === "schedule" ? this._renderSchedule(action, i) : nothing}
      ${current && action.type !== "schedule"
        ? html`${current.available ? nothing : html`<div class="warn-text">${current.requires === "external_data"
            ? "Dormant: allow sending data off this instance in Settings first. Nothing is sent until you do."
            : "Dormant until third-party actions are allowed in Settings."}</div>`}
          <ha-form
            .hass=${this.hass}
            .schema=${current.schema}
            .data=${action.config}
            .computeLabel=${labelFor}
            @value-changed=${(e) => this._setAction(i, { config: e.detail.value })}
          ></ha-form>`
        : action.type === "schedule" || current
          ? nothing
          : html`<div class="warn-text">This action type is not installed, so the rule is dormant.</div>`}
    </div>`;
  }

  _renderSchedule(action, i) {
    const c = {
      trigger: "state_for", do: "turn_off", state: "on", event: "sunset",
      offset_minutes: 0, catch_up_minutes: 0, days: [], ...action.config,
    };
    const set = (patch) => this._setAction(i, { config: { ...c, ...patch } });
    const dur = { hours: 0, minutes: 0, seconds: 0, ...(c.duration || {}) };
    const num = (v) => Math.max(0, parseInt(v || "0", 10) || 0);
    const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
    return html`<div class="sentence">
      <div class="line">
        <select .value=${c.do} @change=${(e) => set({ do: e.target.value })}>
          <option value="turn_off" ?selected=${c.do === "turn_off"}>Turn off</option>
          <option value="turn_on" ?selected=${c.do === "turn_on"}>Turn on</option>
        </select>
        <span>the selected entities</span>
        <select .value=${c.trigger} @change=${(e) => set({ trigger: e.target.value })}>
          <option value="state_for" ?selected=${c.trigger === "state_for"}>after they have been</option>
          <option value="time" ?selected=${c.trigger === "time"}>at a time of day</option>
          <option value="sun" ?selected=${c.trigger === "sun"}>at sunrise or sunset</option>
        </select>
      </div>
      ${c.trigger === "state_for"
        ? html`<div class="line">
            <select .value=${c.state} @change=${(e) => set({ state: e.target.value })}>
              <option value="on" ?selected=${c.state === "on"}>on</option>
              <option value="off" ?selected=${c.state === "off"}>off</option>
            </select>
            <span>for</span>
            <input class="small" type="number" min="0" .value=${String(dur.hours)}
              @input=${(e) => set({ duration: { ...dur, hours: num(e.target.value) } })} />
            <span>hours</span>
            <input class="small" type="number" min="0" max="59" .value=${String(dur.minutes)}
              @input=${(e) => set({ duration: { ...dur, minutes: num(e.target.value) } })} />
            <span>minutes</span>
          </div>
          <p class="muted">Watches the entity's state, so it makes no difference whether it was switched in Home
            Assistant or by hand. If it goes ${c.state === "on" ? "off" : "on"} first, the timer is cancelled.
            Deadlines are stored, so restarts don't reset them. Entities already ${c.state} when PropSense first
            sees them start their timer then.</p>`
        : nothing}
      ${c.trigger === "time"
        ? html`<div class="line"><span>at</span>
            <input type="time" step="60" .value=${(c.at || "").slice(0, 5)}
              @input=${(e) => set({ at: e.target.value ? `${e.target.value}:00` : "" })} /></div>`
        : nothing}
      ${c.trigger === "sun"
        ? html`<div class="line"><span>at</span>
            <select .value=${c.event} @change=${(e) => set({ event: e.target.value })}>
              <option value="sunrise" ?selected=${c.event === "sunrise"}>sunrise</option>
              <option value="sunset" ?selected=${c.event === "sunset"}>sunset</option>
            </select>
            <input class="small" type="number" .value=${String(c.offset_minutes)}
              @input=${(e) => set({ offset_minutes: parseInt(e.target.value || "0", 10) || 0 })} />
            <span>minutes (negative is before)</span></div>`
        : nothing}
      ${c.trigger !== "state_for"
        ? html`<div class="line"><span>on</span>
            ${DAYS.map((d) => html`<button class="chip ${c.days.includes(d) ? "on" : ""}" type="button"
              @click=${() => set({ days: c.days.includes(d) ? c.days.filter((x) => x !== d) : [...c.days, d] })}>
              ${d}</button>`)}
            <span class="muted">${c.days.length ? "" : "(every day)"}</span></div>
          <div class="line"><span>If Home Assistant was down at that time, still run it up to</span>
            <input class="small" type="number" min="0" .value=${String(c.catch_up_minutes)}
              @input=${(e) => set({ catch_up_minutes: num(e.target.value) })} />
            <span>minutes late (0 = skip)</span></div>
          <p class="muted">Entities already ${c.do === "turn_on" ? "on" : "off"} are left alone, and a light someone turned
            off by hand stays off until the next time.</p>`
        : nothing}
    </div>`;
  }

  _labels = {
    assistants: "Expose to",
    group: "Existing group (to edit)",
    create_name: "Or create a group named",
    group_type: "Type of group to create",
    min_interval_seconds: "Seconds between points per entity (at least)",
    include_booleans: "Also send on/off as 1/0",
    tag_area: "Tag points with the area",
    tag_device_class: "Tag points with the device class",
    tag_unit: "Tag points with the unit",
    max_entities: "Most entities this rule may ship",
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
      ${draft?.skipped && Object.keys(draft.skipped).length
        ? html`<div class="warn-text">Skipped: ${Object.entries(draft.skipped).map(([e, why]) => `${e} (${why})`).join("; ")}</div>`
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
      ${this._data.settings.dry_run ? html`<div class="notice">Dry run is on: “Apply now” changes nothing, and timers and schedules don't fire.</div>` : nothing}
      ${this._renderRuntime()}
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

  _renderMetrics() {
    const m = this._data.runtime?.metrics;
    if (!m || !m.targets?.length) return nothing;
    return html`<ha-card class="pad">
      <h3>Metrics shipping</h3>
      <div class="muted">Sending to <code>${m.url}</code> and nowhere else.</div>
      ${m.targets.map((t) => html`<div>${t.label} · ${t.entities} entities</div>`)}
      <div>Sent ${m.sent} points · waiting to send ${m.buffered}${m.dropped ? html` · <span class="warn-text">dropped ${m.dropped}</span>` : nothing}</div>
      ${m.last_error
        ? html`<div class="warn-text">Last send failed: ${m.last_error}. Points wait in memory and are retried every 30 seconds.</div>`
        : m.last_success ? html`<div class="muted">Last success ${new Date(m.last_success).toLocaleString()}</div>` : nothing}
    </ha-card>`;
  }

  _renderRuntime() {
    const items = this._data.runtime?.schedule?.schedules || [];
    if (!items.length) return this._renderMetrics();
    return html`${this._renderMetrics()}<ha-card class="pad">
      <h3>Timers and schedules</h3>
      ${items.map((it) => html`<div class="runtime">
        <div><b>${it.label}</b> <span class="muted">· ${it.entities.length} entities</span></div>
        ${it.timers?.length
          ? html`<ul class="summary">${it.timers.map((t) => html`<li>${this._entityName(t.entity_id)}: ${this._rel(t.due)}</li>`)}</ul>`
          : it.trigger === "state_for"
            ? html`<div class="muted">No running timers: none of them is in that state.</div>`
            : nothing}
        ${it.next ? html`<div class="muted">Next run ${new Date(it.next).toLocaleString()} (${this._rel(it.next)})</div>` : nothing}
      </div>`)}
    </ha-card>`;
  }

  _renderTargets(type, targets) {
    return Object.entries(targets || {}).map(
      ([target, r]) => html`<ha-card class="pad">
        <div class="row">
          <div><b>${this._typeName(type)}</b> → ${r.label || this._targetName(type, target)}</div>
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
          <div><b>Capabilities</b>: ${ex.capabilities.map((c) => this._valueName("capabilities", c)).join(", ") || "none"}</div>
          <div><b>Integration</b>: ${ex.integration || "none"}
            · <b>Manufacturer</b>: ${ex.manufacturer || "none"} · <b>Model</b>: ${ex.model || "none"}</div>
          <div><b>Category</b>: ${ex.entity_category} · <b>Name</b>: ${ex.name || "none"}</div>
          <div><b>Label names</b>: ${ex.label_names.join(", ") || "none"}</div>
          <div><b>State</b>: ${ex.state ?? "none"}</div>
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
        ${check("allow_external_data", "Allow sending data off this instance",
          "Warning: lets rules send entity data (numeric history) to the metrics URL below, and nowhere else. Nothing is sent until this is on and a rule uses it. There are no credentials: the endpoint should only accept posts from your network.")}
        <div class="field">
          <div class="label">Metrics URL</div>
          <div class="muted">The only address data is ever sent to (InfluxDB line protocol, for example a VictoriaMetrics /write endpoint).</div>
          <input type="text" .value=${s.metrics_url || ""}
            @input=${(e) => this._setSetting("metrics_url", e.target.value.trim())} />
        </div>
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
    .summary { margin: 4px 0 0; padding-left: 18px; }
    .help { margin: -2px 0 6px; }
    .line.cond { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 6px 0; }
    .line.cond select { width: auto; }
    .line.cond input.val { width: 110px; }
    .line.cond input.attr { width: 150px; }
    details.more { margin-top: 8px; }
    details.more > summary { margin-bottom: 8px; }
    .templates { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; margin-bottom: 16px; }
    .template { text-align: left; border-radius: 12px; padding: 14px; }
    .template:hover { border-color: var(--primary-color); }
    .sentence { margin-top: 8px; }
    .sentence .line { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
    .sentence select { width: auto; }
    .sentence input.small { width: 72px; }
    .sentence input[type="time"] { width: auto; padding: 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; }
    .chip { padding: 4px 10px; border-radius: 14px; text-transform: capitalize; }
    .chip.on { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }
    .runtime { padding: 8px 0; border-bottom: 1px solid var(--divider-color); }
    .runtime:last-child { border-bottom: none; }
    .toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); background: var(--primary-text-color); color: var(--card-background-color); padding: 10px 18px; border-radius: 20px; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
  `;
}

customElements.define("propsense-panel", PropSensePanel);
