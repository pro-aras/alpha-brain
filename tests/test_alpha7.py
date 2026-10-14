"""End-to-end verification suite for Alpha 7."""

import time
from alpha7 import Alpha7Body, Alpha7Organism, SandboxWorld, SensoryFrame


def test_million_neurons_hardware_efficiency() -> None:
    """Verifies that 1,000,000 dendritic neurons initialize with low memory and step in milliseconds."""
    org = Alpha7Organism(num_neurons=1_000_000, neurons_per_column=64)
    assert org.neuron_count == 1_000_000
    assert org.memory_footprint_mb < 75.0

    frame = org.body.build_frame(
        eyes=["pointy_ears", "whiskers"],
        ears=["purr"],
        hands=["soft_fur"],
        smell=["feline_scent"],
    )
    t0 = time.perf_counter()
    raw = org.brain.perceive_and_step(frame.to_neural_traits(), True)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 25.0, f"1M neuron step took {elapsed_ms:.2f} ms"
    assert "touched_neurons" in raw


def test_infant_one_and_two_shot_cat_learning() -> None:
    """Verifies that seeing a cat once or twice extracts core invariants and recognizes any unseen cat."""
    org = Alpha7Organism(num_neurons=100_000, neurons_per_column=64)

    # Exposure 1: Orange cat
    cat1 = SandboxWorld.cat_exposure_1(org.body)
    res1 = org.experience_object("cat", cat1, affordance=("gentle_pet", "ears:purr"), partner="user")
    assert res1["exposures"] == 1
    assert res1["familiarity"] > 0.60

    # Even after just 1 exposure, an unseen white cat shares enough traits to be recognized!
    white_cat = SandboxWorld.unseen_white_cat(org.body)
    recs_after_1 = org.recognize(white_cat)
    assert len(recs_after_1) >= 1
    assert recs_after_1[0]["concept_name"] == "cat"

    # Exposure 2: Black cat -> separates Core Invariants from Variable Traits (orange vs black fur)
    cat2 = SandboxWorld.cat_exposure_2(org.body)
    res2 = org.experience_object("cat", cat2, partner="user")
    assert res2["exposures"] == 2
    assert res2["familiarity"] >= 0.85
    assert "eyes:whiskers" in res2["core_invariants"]
    assert "eyes:pointy_ears" in res2["core_invariants"]
    assert "eyes:orange_fur" in res2["variable_traits"]
    assert "eyes:black_fur" in res2["variable_traits"]

    # Unseen white cat is recognized with even higher confidence after 2 exposures
    recs_after_2 = org.recognize(white_cat)
    assert recs_after_2[0]["concept_name"] == "cat"
    assert recs_after_2[0]["confidence"] > 0.85

    # Unseen dog does not falsely match 'cat' with high confidence
    dog = SandboxWorld.unseen_dog(org.body)
    dog_recs = org.recognize(dog)
    assert all(r["confidence"] < 0.45 for r in dog_recs)


def test_prediction_failure_analysis_and_goal_scenarios() -> None:
    """Verifies that Alpha 7 predicts what happens next, analyzes failed predictions, and plans toward goals."""
    org = Alpha7Organism(num_neurons=50_000, neurons_per_column=64)

    # 1. Learn normal causal sequence: press_switch -> light_on -> room_bright
    f_switch = org.body.build_frame(eyes=["switch_visible"], hands=["near_switch"])
    org.act_and_learn_from_surprise(f_switch, "press_switch", ["eyes:light_on"], partner="user")

    f_light = org.body.build_frame(eyes=["light_on"])
    org.act_and_learn_from_surprise(f_light, "read_book", ["eyes:knowledge_gained"], partner="user")

    # Verify prediction works
    preds = org.predict_before_acting(f_switch, "press_switch")
    assert preds and preds[0][0] == "eyes:light_on"

    # 2. Now something FAILS to happen: power is unplugged (`smell:power_off_marker`)
    f_unplugged = org.body.build_frame(
        eyes=["switch_visible"],
        hands=["near_switch"],
        smell=["power_unplugged"],
    )
    eval_fail = org.act_and_learn_from_surprise(
        f_unplugged,
        "press_switch",
        ["eyes:darkness_remains"],
        partner="user",
    )["evaluation"]

    assert eval_fail["prediction_failed"] is True
    assert "eyes:light_on" in eval_fail["failed_to_happen"]
    assert "PREDICTION FAILURE ANALYZED" in eval_fail["analysis_report"]

    # Next time power is unplugged, Alpha 7 predicts `eyes:darkness_remains` instead of `eyes:light_on`!
    new_preds = org.predict_before_acting(f_unplugged, "press_switch")
    assert new_preds[0][0] == "eyes:darkness_remains"

    # 3. Goal-directed scenario rollout: from normal switch state, how to reach `eyes:knowledge_gained`?
    scenarios = org.calculate_goal_scenarios(f_switch, "eyes:knowledge_gained", max_depth=3)
    assert any(s["reaches_goal"] and s["actions"] == ["press_switch", "read_book"] for s in scenarios)


def test_grounded_language_coding_and_user_memories() -> None:
    """Verifies grounded word understanding, small code learning, and direct user episodic memory."""
    org = Alpha7Organism(num_neurons=50_000, neurons_per_column=64)

    # Teach 'cat'
    org.experience_object(
        "cat",
        SandboxWorld.cat_exposure_1(org.body),
        affordance=("gentle_pet", "ears:purr"),
        partner="user",
    )

    # Practice small coding with hands & eyes:
    # 1st code snippet: valid addition
    res_ok = org.practice_coding("result = 2 + 3\nprint(result)", concept_label="addition_code")
    assert "eyes:printed_5" in res_ok["actual_outcomes"]

    # 2nd code snippet: syntax error triggers prediction failure analysis!
    res_err = org.practice_coding("result = 2 + * 3")
    assert "eyes:syntax_error" in res_err["actual_outcomes"]
    assert res_err["analysis"]["prediction_failed"] is True

    # Grounded language understanding: thinking on words evokes sensory-motor traits & memories
    thought = org.understand_words("kitty cat addition_code")
    assert "cat" in thought["activated_concepts"]
    assert "addition_code" in thought["activated_concepts"]
    assert "eyes:whiskers" in thought["evoked_sensory_traits"]
    assert len(thought["recalled_episodes"]) >= 2

    memories = org.user_memories(limit=5)
    assert len(memories) >= 2
    assert any(m["partner"] == "user" for m in memories)
