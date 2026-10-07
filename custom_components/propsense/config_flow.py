"""Config and options flows: the UI for managing rules.

Setup is a single confirmation. Everything else is done in the options flow
("Configure" on the integration): a menu to add, edit, enable or disable and
delete rules, change settings, and preview what the rules would do before
anything is applied.
"""
from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, selector

from .const import ASSISTANT_LABELS, ASSISTANTS, CONF_RULES, CONF_SETTINGS, DOMAIN
from .engine import (
    SELECTOR_FIELDS,
    Rule,
    Selector,
    Settings,
    estimated_tokens,
)

# Selector fields that the UI offers directly, and how to pick them.
_UI_FIELDS = ("labels", "areas", "floors", "domains", "devices", "entities", "groups")


def _field_selector(name: str, domains: list[str]) -> selector.Selector:
    if name == "labels":
        return selector.LabelSelector(selector.LabelSelectorConfig(multiple=True))
    if name == "areas":
        return selector.AreaSelector(selector.AreaSelectorConfig(multiple=True))
    if name == "floors":
        return selector.FloorSelector(selector.FloorSelectorConfig(multiple=True))
    if name == "devices":
        return selector.DeviceSelector(selector.DeviceSelectorConfig(multiple=True))
    if name == "entities":
        return selector.EntitySelector(selector.EntitySelectorConfig(multiple=True))
    if name == "groups":
        return selector.EntitySelector(selector.EntitySelectorConfig(multiple=True))
    # domains
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=domains,
            multiple=True,
            custom_value=True,
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _selector_fields(
    prefix: str, current: Selector, domains: list[str]
) -> dict[Any, Any]:
    fields: dict[Any, Any] = {}
    existing = current.to_dict()
    for name in _UI_FIELDS:
        key = f"{prefix}_{name}"
        values = existing.get(name) or []
        fields[
            vol.Optional(key, description={"suggested_value": values})
        ] = _field_selector(name, domains)
    return fields


def _selector_from_input(prefix: str, user_input: dict[str, Any], keep: Selector) -> Selector:
    data = keep.to_dict()  # keeps fields the UI does not edit (device classes)
    for name in _UI_FIELDS:
        data[name] = user_input.get(f"{prefix}_{name}") or []
    return Selector.from_dict(data)


class PropSenseConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(
                title="PropSense",
                data={},
                options={CONF_RULES: [], CONF_SETTINGS: Settings().to_dict()},
            )
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return PropSenseOptionsFlow()


class PropSenseOptionsFlow(OptionsFlowWithReload):
    """Manage rules and settings. Each save ends the flow and reloads."""

    def __init__(self) -> None:
        self._rule_id: str | None = None
        self._draft: dict[str, Any] = {}

    # ----------------------------------------------------------- helpers

    @property
    def _rules(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.config_entry.options.get(CONF_RULES, [])]

    @property
    def _settings(self) -> Settings:
        return Settings.from_dict(self.config_entry.options.get(CONF_SETTINGS))

    def _domains(self) -> list[str]:
        registry = er.async_get(self.hass)
        found = {e.domain for e in registry.entities.values()}
        found |= {s.domain for s in self.hass.states.async_all()}
        return sorted(found)

    def _save(self, rules: list[dict[str, Any]], settings: Settings | None = None):
        return self.async_create_entry(
            data={
                CONF_RULES: rules,
                CONF_SETTINGS: (settings or self._settings).to_dict(),
            }
        )

    # -------------------------------------------------------------- menu

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        options = ["add_rule"]
        if self._rules:
            options.append("pick_rule")
        options += ["settings", "preview"]
        self._rule_id = None
        self._draft = {}
        return self.async_show_menu(step_id="init", menu_options=options)

    # --------------------------------------------------- add / edit a rule

    async def async_step_add_rule(self, user_input=None) -> Any:
        self._rule_id = None
        self._draft = {}
        return await self.async_step_rule_include()

    async def async_step_pick_rule(self, user_input=None) -> Any:
        rules = self._rules
        if user_input is not None:
            self._rule_id = user_input["rule"]
            return await self.async_step_rule_menu()
        options = [
            selector.SelectOptionDict(
                value=r["id"],
                label=f'{r["name"]}{"" if r.get("enabled", True) else " (disabled)"}',
            )
            for r in rules
        ]
        return self.async_show_form(
            step_id="pick_rule",
            data_schema=vol.Schema(
                {
                    vol.Required("rule"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    async def async_step_rule_menu(self, user_input=None) -> Any:
        return self.async_show_menu(
            step_id="rule_menu",
            menu_options=["edit_rule", "toggle_rule", "delete_rule"],
        )

    async def async_step_edit_rule(self, user_input=None) -> Any:
        rule = next((r for r in self._rules if r["id"] == self._rule_id), None)
        self._draft = {}
        return await self.async_step_rule_include(rule=rule)

    async def async_step_toggle_rule(self, user_input=None) -> Any:
        rules = self._rules
        for r in rules:
            if r["id"] == self._rule_id:
                r["enabled"] = not r.get("enabled", True)
        return self._save(rules)

    async def async_step_delete_rule(self, user_input=None) -> Any:
        rules = [r for r in self._rules if r["id"] != self._rule_id]
        return self._save(rules)

    async def async_step_rule_include(
        self, user_input: dict[str, Any] | None = None, rule: dict[str, Any] | None = None
    ) -> Any:
        if rule is None and self._rule_id:
            rule = next((r for r in self._rules if r["id"] == self._rule_id), None)
        current = Rule.from_dict(rule) if rule else None
        errors: dict[str, str] = {}

        if user_input is not None:
            include = _selector_from_input(
                "include",
                user_input,
                current.include if current else Selector(),
            )
            if include.is_empty:
                errors["base"] = "empty_selector"
            else:
                self._draft = {
                    "name": user_input["name"].strip(),
                    "enabled": user_input.get("enabled", True),
                    "assistants": user_input.get("assistants") or ["conversation"],
                    "include": include.to_dict(),
                }
                return await self.async_step_rule_exclude()

        domains = self._domains()
        schema: dict[Any, Any] = {
            vol.Required(
                "name",
                description={"suggested_value": current.name if current else ""},
            ): selector.TextSelector(),
            vol.Required(
                "enabled", default=current.enabled if current else True
            ): selector.BooleanSelector(),
            vol.Required(
                "assistants",
                default=sorted(current.assistants) if current else ["conversation"],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=a, label=ASSISTANT_LABELS.get(a, a)
                        )
                        for a in ASSISTANTS
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
        schema.update(
            _selector_fields("include", current.include if current else Selector(), domains)
        )
        return self.async_show_form(
            step_id="rule_include", data_schema=vol.Schema(schema), errors=errors
        )

    async def async_step_rule_exclude(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        rule = next((r for r in self._rules if r["id"] == self._rule_id), None)
        current = Rule.from_dict(rule) if rule else None

        if user_input is not None:
            exclude = _selector_from_input(
                "exclude", user_input, current.exclude if current else Selector()
            )
            new_rule = {
                "id": self._rule_id or uuid.uuid4().hex[:8],
                **self._draft,
                "exclude": exclude.to_dict(),
            }
            rules = self._rules
            if self._rule_id:
                # keep the rule's position when editing
                rules = [new_rule if r["id"] == self._rule_id else r for r in rules]
            else:
                rules.append(new_rule)
            return self._save(rules)

        schema = _selector_fields(
            "exclude", current.exclude if current else Selector(), self._domains()
        )
        return self.async_show_form(
            step_id="rule_exclude", data_schema=vol.Schema(schema)
        )

    # ---------------------------------------------------------- settings

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        current = self._settings
        if user_input is not None:
            new = Settings.from_dict(
                {
                    **current.to_dict(),
                    "managed_assistants": user_input["managed_assistants"],
                    "blocked_domains": user_input.get("blocked_domains", []),
                    "max_exposed": int(user_input["max_exposed"]),
                    "inherit_device_labels": user_input["inherit_device_labels"],
                    "inherit_area_labels": user_input["inherit_area_labels"],
                    "dry_run": user_input["dry_run"],
                }
            )
            return self._save(self._rules, new)

        schema = vol.Schema(
            {
                vol.Required(
                    "managed_assistants",
                    default=sorted(current.managed_assistants),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=a, label=ASSISTANT_LABELS.get(a, a)
                            )
                            for a in ASSISTANTS
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Optional(
                    "blocked_domains",
                    description={"suggested_value": sorted(current.blocked_domains)},
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=self._domains(),
                        multiple=True,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    "max_exposed", default=current.max_exposed
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=1000, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Required(
                    "inherit_device_labels", default=current.inherit_device_labels
                ): selector.BooleanSelector(),
                vol.Required(
                    "inherit_area_labels", default=current.inherit_area_labels
                ): selector.BooleanSelector(),
                vol.Required(
                    "dry_run", default=current.dry_run
                ): selector.BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="settings", data_schema=schema)

    # ----------------------------------------------------------- preview

    async def async_step_preview(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            return await self.async_step_init()

        manager = self.config_entry.runtime_data
        result = await manager.async_apply(dry_run=True)
        lines: list[str] = []
        for assistant, res in sorted(result.assistants.items()):
            label = ASSISTANT_LABELS.get(assistant, assistant)
            note = " (refused: over the limit)" if res.refused else ""
            lines.append(
                f"**{label}**: would expose {res.count} entities, about "
                f"{estimated_tokens(res.count)} prompt tokens{note}. "
                f"Adds {len(res.added)}, removes {len(res.removed)}."
            )
        if result.by_rule:
            lines.append("")
            lines.append("**Per rule**")
            for rid, count in result.by_rule.items():
                lines.append(f"- {result.rule_names.get(rid, rid)}: {count}")
        if result.blocked:
            lines.append("")
            lines.append(
                "**Blocked** (matched a rule but never exposed): "
                + ", ".join(sorted(result.blocked))
            )
        if not lines:
            lines.append("No rules yet.")
        return self.async_show_form(
            step_id="preview",
            data_schema=vol.Schema({}),
            description_placeholders={"summary": "\n".join(lines)},
        )
