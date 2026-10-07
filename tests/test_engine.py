"""Policy tests for the pure rules engine (no Home Assistant needed)."""
from custom_components.propsense.engine import (
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
    facts("light.kitchen", labels=frozenset({"expose_novak"}), area_id="kitchen", floor_id="l1"),
    facts("light.bedroom", labels=frozenset({"expose_novak"}), area_id="bedroom", floor_id="l2"),
    facts("switch.garage", labels=frozenset(), area_id="garage", floor_id="l1"),
    facts("lock.front", labels=frozenset({"expose_novak"}), area_id="entry", floor_id="l1"),
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
    plan = evaluate([rule(include={"labels": ["expose_novak"]})], ENTITIES, Settings())
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
        [rule(include={"labels": ["expose_novak"], "floors": ["l1"]})], ENTITIES, Settings()
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
        [rule(include={"labels": ["expose_novak"]}, exclude={"areas": ["bedroom"]})],
        ENTITIES,
        Settings(),
    )
    assert wanted(plan) == {"light.kitchen"}
    # another rule can still pick the excluded entity back up
    plan = evaluate(
        [
            rule("a", include={"labels": ["expose_novak"]}, exclude={"areas": ["bedroom"]}),
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
    rules = [rule(include={"labels": ["expose_novak"]})]
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
