#!/usr/bin/env python3
"""Interactive demonstration of Alpha 7's 3-in-1 Bio-Inspired Architecture."""

import time
from alpha7 import Alpha7Organism, SandboxWorld


def main() -> None:
    print("=" * 76)
    print(" ALPHA 7 — THE PURE ROAD: EMBODIED SPARSE DENDRITIC & CONCEPT WEB ENGINE")
    print("=" * 76)

    t0 = time.perf_counter()
    org = Alpha7Organism(num_neurons=1_000_000, neurons_per_column=64)
    init_ms = (time.perf_counter() - t0) * 1000.0
    print(f"\n[1] BRAIN FABRIC INITIALIZED")
    print(f"    • Total Dendritic Neurons : {org.neuron_count:,}")
    print(f"    • Memory Footprint        : {org.memory_footprint_mb:.1f} MB")
    print(f"    • Allocation Time         : {init_ms:.1f} ms")

    # 2. Infant-like 1-2 shot learning ("Cat")
    print("\n[2] INFANT-LIKE 1-2 SHOT CONCEPT FORMATION ('cat')")
    t_step = time.perf_counter()
    exp1 = org.experience_object(
        "cat",
        SandboxWorld.cat_exposure_1(org.body),
        affordance=("gentle_pet", "ears:purr"),
        partner="user",
    )
    step_ms = (time.perf_counter() - t_step) * 1000.0
    print(f"    • Exposure #1 (Orange Cat): familiarity={exp1['familiarity']:.2f}, "
          f"touched={exp1['touched_neurons']} / {org.neuron_count:,} neurons ({step_ms:.2f} ms)")

    exp2 = org.experience_object("cat", SandboxWorld.cat_exposure_2(org.body), partner="user")
    print(f"    • Exposure #2 (Black Cat) : familiarity={exp2['familiarity']:.2f}")
    print(f"    • Core Invariant Traits   : {exp2['core_invariants']}")
    print(f"    • Variable Surface Traits : {exp2['variable_traits']}")

    white_cat_recs = org.recognize(SandboxWorld.unseen_white_cat(org.body))
    print(f"    • Unseen White Cat Test   : Recognized '{white_cat_recs[0]['concept_name']}' "
          f"(confidence={white_cat_recs[0]['confidence']:.2f})")

    # 3. Prediction & Surprise Failure Analysis
    print("\n[3] PREDICTIVE PROCESSING & FAILED-PREDICTION ANALYSIS")
    f_normal = org.body.build_frame(eyes=["switch_visible"], hands=["near_switch"])
    org.act_and_learn_from_surprise(f_normal, "press_switch", ["eyes:light_on"], partner="user")
    preds = org.predict_before_acting(f_normal, "press_switch")
    print(f"    • Learned Prediction      : press_switch -> {preds}")

    f_unplugged = org.body.build_frame(
        eyes=["switch_visible"], hands=["near_switch"], smell=["power_unplugged"]
    )
    fail_res = org.act_and_learn_from_surprise(
        f_unplugged, "press_switch", ["eyes:darkness_remains"], partner="user"
    )["evaluation"]
    print(f"    • When Prediction Fails   : {fail_res['analysis_report']}")
    updated_preds = org.predict_before_acting(f_unplugged, "press_switch")
    print(f"    • Updated Prediction      : press_switch (with power_unplugged) -> {updated_preds}")

    # 4. Small Coding Learning + Grounded Language + User Memories
    print("\n[4] SMALL CODING LEARNING & GROUNDED LANGUAGE THOUGHT")
    code_ok = org.practice_coding("result = 6 * 7\nprint(result)", concept_label="multiply_code")
    print(f"    • Code Practice #1        : {code_ok['actual_outcomes']} -> {code_ok['analysis']['analysis_report']}")
    code_err = org.practice_coding("result = 6 * * * 7")
    print(f"    • Code Practice #2 (Typo) : {code_err['actual_outcomes']} -> {code_err['analysis']['analysis_report']}")

    thought = org.understand_words("kitty cat multiply_code")
    print(f"    • Grounded Utterance      : '{thought['utterance']}'")
    print(f"      - Activated Concepts    : {thought['activated_concepts']}")
    print(f"      - Evoked Sensory Traits : {thought['evoked_sensory_traits'][:6]}")
    print(f"      - Direct User Memories  : {len(thought['recalled_episodes'])} episodes recalled")
    print("=" * 76)


if __name__ == "__main__":
    main()
