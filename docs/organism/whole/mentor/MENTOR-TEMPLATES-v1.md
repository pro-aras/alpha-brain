# MENTOR-TEMPLATES-v1 — the mentor world's frozen template set (PREREG-W2 §2, SIGNED x3 at t-l4-1003 5b32d03)
# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:01 +0400 — rendered from creature/senses/mentor.py's
# TEMPLATES_V1 by M.render_templates_v1(); the set is FROZEN at the law's signature (seat decision 8(d)) and grows only by
# signed laws (v2+). The equality of this file with the code table is pinned by tests/tools/test_w2_templates.py.

# tpl | surface | truth rule (the record)
M-A1 | alpha sees <NP> (confirm) | after a say TRUE of the attended thing; the attended thing named truly
M-A2 | alpha sees <NP> (correct) | after a say NOT true of the attended thing; the attended thing named truly
M-A3 | alpha sees <NP> (re-name / the answer to an ask) | the asked thing named truly
M-C1-T1 | alpha sees <shape> | the referent is in the canvas's truth spec and fixated
M-C1-T2 | alpha sees <colour> <shape> | the referent is in the canvas's truth spec and fixated
M-C1-T3 | alpha sees <size> <shape> | the referent is in the canvas's truth spec and fixated
M-C1-T4 | alpha sees <size> <colour> <shape> | the referent is in the canvas's truth spec and fixated
M-C2-T1 | alpha does not see <shape> | a thing matching the NP is in the truth spec and never fixated
M-C2-T2 | alpha does not see <colour> <shape> | a thing matching the NP is in the truth spec and never fixated
M-C2-T3 | alpha does not see <size> <shape> | a thing matching the NP is in the truth spec and never fixated
M-C2-T4 | alpha does not see <size> <colour> <shape> | a thing matching the NP is in the truth spec and never fixated
M-C3 | a run of >= 3 «alpha sees <NP>» rows, one carrier, one position changed, over the canvas's different things | each row of the run passes its own M-C1 rule
M-M1 | unsure | doubt at the same canvas (no mature word holds the leading thing)
M-M2 | fresh | young at the same canvas (the name just heard met < 3 times)
M-M3 | asked | the previous canvas's act was ASK
