"""Policy tests for the pure rules engine (no Home Assistant needed)."""
import pytest

from custom_components.propsense.engine import (
    EXPOSE_SPEC,
    EntityFacts,
    Rule,
    Selector,
    Settings,
    TOKENS_PER_ENTITY,
    estimated_tokens,
    evaluate,
    plan_changes,
)


def facts(entity_id, **kw):
    kw.setdefault("labels", frozenset())
    return EntityFacts(entity_id=entity_id, **{**kw})


def rule(rid="r1", include=None, exclude=None, assistants=None, enabled=True):
    return Rule.from_dict(
        {
            "id": rid,
            "name": rid,
            "enabled": enabled,
            "include": include or {},
            "exclude": exclude or {},
            "assistants": assistants or ["conversation"],
        }
    )


ENTITIES = [
    facts("light.kitchen", labels=frozenset({"expose_voice"}), area_id="kitchen", floor_id="l1"),
    facts("light.bedroom", labels=frozenset({"expose_voice"}), area_id="bedroom", floor_id="l2"),
    facts("switch.garage", labels=frozenset(), area_id="garage", floor_id="l1"),
    facts("lock.front", labels=frozenset({"expose_voice"}), area_id="entry", floor_id="l1"),
    facts("sensor.temp", labels=frozenset({"other"}), area_id="kitchen", floor_id="l1", device_class="temperature"),
    facts("light.hall", labels=frozenset(), area_id="hall", floor_id="l1", groups=frozenset({"group.downstairs"})),
]


def wanted(plan, assistant="conversation"):
    return plan.desired.get(assistant, set())


def test_empty_selector_matches_nothing():
    assert Selector().matches(ENTITIES[0]) is False
    plan = evaluate([rule(include={})], ENTITIES, Settings())
    assert wanted(plan) == set()


def test_exclude_only_rule_matches_nothing():
    plan = evaluate([rule(include={}, exclude={"areas": ["garage"]})], ENTITIES, Settings())
    assert wanted(plan) == set()


def test_label_selects_and_blocked_domain_is_dropped():
    plan = evaluate([rule(include={"labels": ["expose_voice"]})], ENTITIES, Settings())
    assert wanted(plan) == {"light.kitchen", "light.bedroom"}
    assert "lock.front" in plan.blocked
    assert "lock.front" not in wanted(plan)


def test_blocked_domain_applies_to_explicit_entities_too():
    plan = evaluate([rule(include={"entities": ["lock.front"]})], ENTITIES, Settings())
    assert wanted(plan) == set()
    assert "lock.front" in plan.blocked


def test_unblocking_a_domain_is_an_explicit_choice():
    settings = Settings(blocked_domains=frozenset())
    plan = evaluate([rule(include={"entities": ["lock.front"]})], ENTITIES, settings)
    assert wanted(plan) == {"lock.front"}


def test_fields_are_anded_values_are_ored():
    # label AND floor: the bedroom light has the label but is on the wrong floor
    plan = evaluate(
        [rule(include={"labels": ["expose_voice"], "floors": ["l1"]})], ENTITIES, Settings()
    )
    assert wanted(plan) == {"light.kitchen"}
    # two areas are an OR
    plan = evaluate([rule(include={"areas": ["kitchen", "bedroom"]})], ENTITIES, Settings())
    assert wanted(plan) == {"light.kitchen", "light.bedroom", "sensor.temp"}


def test_domain_and_device_class_selectors():
    plan = evaluate([rule(include={"domains": ["light"]})], ENTITIES, Settings())
    assert wanted(plan) == {"light.kitchen", "light.bedroom", "light.hall"}
    plan = evaluate([rule(include={"device_classes": ["temperature"]})], ENTITIES, Settings())
    assert wanted(plan) == {"sensor.temp"}


def test_groups_and_devices():
    plan = evaluate([rule(include={"groups": ["group.downstairs"]})], ENTITIES, Settings())
    assert wanted(plan) == {"light.hall"}
    with_dev = [facts("light.a", device_id="dev1"), facts("light.b", device_id="dev2")]
    plan = evaluate([rule(include={"devices": ["dev1"]})], with_dev, Settings())
    assert wanted(plan) == {"light.a"}


def test_exclude_subtracts_from_the_same_rule_only():
    plan = evaluate(
        [rule(include={"labels": ["expose_voice"]}, exclude={"areas": ["bedroom"]})],
        ENTITIES,
        Settings(),
    )
    assert wanted(plan) == {"light.kitchen"}
    # another rule can still pick the excluded entity back up
    plan = evaluate(
        [
            rule("a", include={"labels": ["expose_voice"]}, exclude={"areas": ["bedroom"]}),
            rule("b", include={"entities": ["light.bedroom"]}),
        ],
        ENTITIES,
        Settings(),
    )
    assert wanted(plan) == {"light.kitchen", "light.bedroom"}


def test_disabled_rules_do_nothing():
    plan = evaluate([rule(include={"areas": ["kitchen"]}, enabled=False)], ENTITIES, Settings())
    assert wanted(plan) == set()


def test_rules_are_additive_and_counted_per_rule():
    plan = evaluate(
        [rule("a", include={"entities": ["light.kitchen"]}), rule("b", include={"areas": ["kitchen"]})],
        ENTITIES,
        Settings(),
    )
    assert wanted(plan) == {"light.kitchen", "sensor.temp"}
    assert plan.by_rule["a"] == {"light.kitchen"}
    assert plan.by_rule["b"] == {"light.kitchen", "sensor.temp"}


def test_managed_assistant_with_no_rules_wants_nothing():
    # single source of truth: with no rules, the managed assistant is emptied
    plan = evaluate([], ENTITIES, Settings(managed_assistants=frozenset({"conversation"})))
    assert plan.desired == {"conversation": set()}
    assert plan.managed == {"conversation"}


def test_rule_targets_extend_the_managed_set():
    plan = evaluate(
        [rule(include={"entities": ["light.kitchen"]}, assistants=["conversation", "cloud.alexa"])],
        ENTITIES,
        Settings(),
    )
    assert plan.managed == {"conversation", "cloud.alexa"}
    assert wanted(plan, "cloud.alexa") == {"light.kitchen"}


def test_evaluate_is_deterministic():
    rules = [rule(include={"labels": ["expose_voice"]})]
    assert evaluate(rules, ENTITIES, Settings()).desired == evaluate(rules, list(reversed(ENTITIES)), Settings()).desired


def test_plan_changes_diff():
    changes = plan_changes({"light.old", "light.keep"}, {"light.keep", "light.new"}, 100)
    assert changes.add == {"light.new"}
    assert changes.remove == {"light.old"}
    assert changes.refused is False


def test_plan_changes_refuses_oversized_plans_and_changes_nothing():
    desired = {f"light.l{i}" for i in range(11)}
    changes = plan_changes({"light.old"}, desired, 10)
    assert changes.refused is True
    assert changes.add == frozenset() and changes.remove == frozenset()
    assert changes.desired_count == 11


def test_max_zero_disables_the_guard():
    desired = {f"light.l{i}" for i in range(500)}
    assert plan_changes(set(), desired, 0).refused is False


def test_roundtrip_serialisation():
    r = rule(
        "x",
        include={"labels": ["a", "b"], "floors": ["l1"]},
        exclude={"areas": ["z"]},
        assistants=["conversation", "cloud.alexa"],
    )
    assert Rule.from_dict(r.to_dict()) == r
    s = Settings(max_exposed=42, dry_run=True, blocked_domains=frozenset({"lock"}))
    assert Settings.from_dict(s.to_dict()) == s


def test_settings_defaults_block_the_sensitive_domains():
    s = Settings()
    assert {"lock", "alarm_control_panel", "camera"} <= s.blocked_domains
    assert s.max_exposed == 100


def test_token_estimate():
    assert estimated_tokens(60) == 60 * TOKENS_PER_ENTITY


# ---------------------------------------------------------------- actions

from custom_components.propsense.engine import Action, ActionSpec  # noqa: E402

GRANT = ActionSpec(
    type_id="grant",
    targets=lambda cfg: frozenset(cfg.get("children", [])),
    respects_blocked_domains=False,
)


def action_rule(rid, include, actions):
    return Rule.from_dict(
        {"id": rid, "name": rid, "include": include, "actions": actions}
    )


def test_legacy_assistants_become_an_expose_action():
    r = Rule.from_dict({"id": "x", "name": "x", "assistants": ["cloud.alexa"]})
    assert r.actions == (Action("expose", {"assistants": ["cloud.alexa"]}),)
    assert r.assistants == frozenset({"cloud.alexa"})
    assert Rule.from_dict(r.to_dict()) == r


def test_explicit_empty_actions_do_nothing():
    r = Rule.from_dict(
        {"id": "x", "name": "x", "include": {"labels": ["expose_voice"]}, "actions": []}
    )
    plan = evaluate([r], ENTITIES, Settings())
    assert wanted(plan) == set()
    assert plan.by_rule["x"] == set()


def test_actions_of_unknown_type_are_dormant_and_touch_nothing():
    r = action_rule(
        "g",
        {"labels": ["expose_voice"]},
        [{"type": "grant", "config": {"children": ["kid1"]}}],
    )
    plan = evaluate([r], ENTITIES, Settings())  # only built-in specs
    assert plan.dormant == {"g": {"grant"}}
    assert "grant" not in plan.targets
    assert plan.by_rule["g"] == set()


def test_third_party_targets_and_block_list_opt_out():
    r = action_rule(
        "g",
        {"labels": ["expose_voice"]},
        [{"type": "grant", "config": {"children": ["kid1"]}}],
    )
    plan = evaluate([r], ENTITIES, Settings(), specs={"grant": GRANT})
    # lock.front is allowed because this action type opted out of the block list
    assert plan.targets["grant"]["kid1"] == {
        "light.kitchen",
        "light.bedroom",
        "lock.front",
    }
    assert plan.blocked == {}


def test_one_rule_can_run_several_actions():
    r = action_rule(
        "both",
        {"labels": ["expose_voice"], "domains": ["light"]},
        [
            {"type": "expose", "config": {"assistants": ["conversation"]}},
            {"type": "grant", "config": {"children": ["kid1"]}},
        ],
    )
    plan = evaluate([r], ENTITIES, Settings(), specs={"expose": EXPOSE_SPEC, "grant": GRANT})
    both = {"light.kitchen", "light.bedroom"}
    assert plan.desired["conversation"] == both
    assert plan.targets["grant"]["kid1"] == both


def test_remembered_targets_stay_managed_without_rules():
    plan = evaluate(
        [], ENTITIES, Settings(), specs={"grant": GRANT}, extra_managed={"grant": ["kid1"]}
    )
    assert plan.targets["grant"] == {"kid1": set()}


def test_capabilities_selector_is_any_of_and_anded_with_other_fields():
    lamps = [
        facts("light.a", capabilities=frozenset({"brightness", "color_temp"}), area_id="k"),
        facts("light.b", capabilities=frozenset({"onoff"}), area_id="k"),
        facts("light.c", capabilities=frozenset({"brightness", "color"}), area_id="b"),
    ]
    r = rule("c", include={"capabilities": ["color_temp", "color"], "areas": ["k"]})
    plan = evaluate([r], lamps, Settings())
    assert plan.desired["conversation"] == {"light.a"}


def test_accepts_filter_reports_why_an_entity_was_skipped():
    spec = ActionSpec(
        type_id="g",
        targets=lambda cfg: frozenset({"grp"}),
        accepts=lambda cfg, entity_id: (
            None if entity_id.startswith("light.") else "not a light"
        ),
    )
    r = action_rule(
        "g",
        {"labels": ["expose_voice"]},
        [{"type": "g", "config": {}}],
    )
    plan = evaluate([r], ENTITIES, Settings(), specs={"g": spec})
    assert plan.targets["g"]["grp"] == {"light.kitchen", "light.bedroom"}
    assert plan.blocked["lock.front"] == "domain 'lock' is blocked"


# ------------------------------------------------- registry-based selectors


def _f(entity_id="light.a", **kw):
    return EntityFacts(entity_id=entity_id, **kw)


def test_integration_matches_case_insensitively_and_any_of():
    s = Selector.from_dict({"integrations": ["Hue", "zha"]})
    assert s.matches(_f(integration="hue"))
    assert s.matches(_f(integration="ZHA"))
    assert not s.matches(_f(integration="mqtt"))
    assert not s.matches(_f())  # no integration (state-only entity)


def test_manufacturer_and_model_support_wildcards():
    assert Selector.from_dict({"manufacturers": ["ikea*"]}).matches(_f(manufacturer="IKEA of Sweden"))
    assert not Selector.from_dict({"manufacturers": ["ikea*"]}).matches(_f(manufacturer="Philips"))
    assert not Selector.from_dict({"manufacturers": ["ikea*"]}).matches(_f())
    assert Selector.from_dict({"models": ["TRADFRI*bulb*"]}).matches(_f(model="TRADFRI bulb E27"))


def test_entity_category_primary_is_the_default():
    primary = Selector.from_dict({"entity_categories": ["primary"]})
    diag = Selector.from_dict({"entity_categories": ["diagnostic", "config"]})
    assert primary.matches(_f())
    assert not primary.matches(_f(entity_category="diagnostic"))
    assert diag.matches(_f(entity_category="config"))
    assert not diag.matches(_f())


def test_name_patterns_match_the_entity_id_or_the_name():
    s = Selector.from_dict({"name_patterns": ["switch.*_plug", "*outlet*"]})
    assert s.matches(_f("switch.kitchen_plug"))
    assert s.matches(_f("switch.x", name="Garage Outlet"))
    assert not s.matches(_f("switch.kitchen_lamp", name="Lamp"))
    assert not Selector.from_dict({"name_patterns": ["a*"]}).matches(_f("light.a"))  # id starts with light.


def test_label_patterns_match_label_names_not_ids():
    s = Selector.from_dict({"label_patterns": ["Expose: *"]})
    assert s.matches(_f(labels=frozenset({"expose_voice"}), label_names=frozenset({"Expose: Voice"})))
    assert s.matches(_f(label_names=frozenset({"expose: alexa"})))
    assert not s.matches(_f(label_names=frozenset({"Needs battery"})))
    assert not s.matches(_f())


def test_new_fields_combine_with_the_old_ones_and_count_as_non_empty():
    assert Selector.from_dict({"name_patterns": ["*"]}).is_empty is False
    s = Selector.from_dict({"integrations": ["hue"], "domains": ["light"]})
    assert s.matches(_f("light.a", integration="hue"))
    assert not s.matches(_f("switch.a", integration="hue"))


# ------------------------------------------------------ state-based selectors

from custom_components.propsense.engine import parse_condition  # noqa: E402


def sf(state, entity_id="sensor.a", **attrs):
    return EntityFacts(entity_id=entity_id, state=state, attributes=attrs)


def test_states_match_any_of_ignoring_case():
    s = Selector.from_dict({"states": ["On", "unavailable"]})
    assert s.matches(sf("on")) and s.matches(sf("unavailable"))
    assert not s.matches(sf("off")) and not s.matches(EntityFacts(entity_id="x.y"))


@pytest.mark.parametrize(
    "text,state,attrs,expected",
    [
        ("state < 20", "15", {}, True),
        ("state < 20", "20", {}, False),
        ("state <= 20", "20", {}, True),
        ("state > 20.5", "21", {}, True),
        ("state >= 5", "abc", {}, False),
        ("state between 10 20", "15", {}, True),
        ("state between 20 10", "15", {}, True),  # order does not matter
        ("state between 10 20", "25", {}, False),
        ("state = on", "ON", {}, True),
        ("state != on", "off", {}, True),
        ("state != on", "on", {}, False),
        ("state = 21.0", "21", {}, True),  # numeric equality, not text
        ("attr:battery_level < 20", "on", {"battery_level": 12}, True),
        ("attr:battery_level < 20", "on", {"battery_level": "12"}, True),
        ("attr:battery_level < 20", "on", {}, False),  # missing never matches
        ("attr:battery_level != 5", "on", {}, False),
        ("attr:hvac_action = heating", "heat", {"hvac_action": "Heating"}, True),
        ("attr:friendly_name = Living room lamp", "on", {"friendly_name": "living room lamp"}, True),
    ],
)
def test_conditions(text, state, attrs, expected):
    assert Selector.from_dict({"conditions": [text]}).matches(sf(state, **attrs)) is expected


def test_conditions_are_any_of_and_malformed_ones_never_match():
    s = Selector.from_dict({"conditions": ["state < 5", "state > 90"]})
    assert s.matches(sf("3")) and s.matches(sf("95")) and not s.matches(sf("50"))
    for bad in ("garbage", "state ~ 3", "state < abc", "level < 3", "state between 1", "attr: < 3"):
        with pytest.raises(ValueError):
            parse_condition(bad)
        assert not Selector.from_dict({"conditions": [bad]}).matches(sf("1"))


def test_state_fields_make_a_selector_non_empty_and_flag_live_state():
    s = Selector.from_dict({"states": ["on"]})
    assert not s.is_empty and s.uses_state
    assert not Selector.from_dict({"labels": ["x"]}).uses_state


def test_metrics_url_has_no_default_and_clears_addresses_older_versions_saved(monkeypatch):
    import hashlib

    from custom_components.propsense import engine

    assert Settings().metrics_url == ""
    assert Settings.from_dict({}).metrics_url == ""
    # an address an earlier version saved as its default is cleared (compared by hash)
    legacy = "https://legacy.example/write"
    monkeypatch.setattr(
        engine, "LEGACY_METRICS_URL_HASHES", (hashlib.sha256(legacy.encode()).hexdigest(),)
    )
    assert Settings.from_dict({"metrics_url": legacy}).metrics_url == ""
    # an address the user chose is never touched
    custom = "http://10.1.2.3/write"
    assert Settings.from_dict({"metrics_url": custom}).metrics_url == custom
    assert Settings.from_dict(Settings(metrics_url=custom).to_dict()).metrics_url == custom
