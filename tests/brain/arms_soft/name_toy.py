# edit: Claude (Opus 5.5), 2026-09-26 12:57 +0400 — the NAME toy every B1 learner must be able to run end to end (teach three
# names on two renderings each, a SLEEP, N rounds of NAME training asks with the right answer as FEEDBACK, SLEEP every 10
# rounds, then NAME test asks on the six renderings). Found missing on 09-26: no test had asked A1, A2 or A3 to NAME, and
# all three answered UNKNOWN to every NAME test ask of B1's first graded run.
from brain.protocol import HarnessContract, make_row, op_row


def run_name_toy(arm, rows, rounds=40, sleep_every=10):
    seq = [0]

    def row(kind, phase, item, payload):
        seq[0] += 1
        return make_row(seq[0], kind, phase, item, payload)

    for ch in "abc":
        for v in (0, 1):
            HarnessContract.teach(arm, row("TEACH", "L1", ch, {"glance_row": rows[ch][v], "name": ch}))
    HarnessContract.sleep(arm, row("SLEEP", "L1", "-", {"steps": 64}))
    for r in range(rounds):
        for ch in "abc":
            for v in (0, 1):
                ask = row("ASK", "L4", f"{ch}-n", {"cues": ["NAME"], "operands": [op_row(rows[ch][v])],
                                                    "candidate_rows": None, "answer_kind": "NAME"})
                a = HarnessContract.training_ask(arm, ask)
                HarnessContract.feedback(arm, row("FEEDBACK", "L4", f"{ch}-n", {"ask_seq": ask["seq"], "right": ch}), a, "NAME")
        if (r + 1) % sleep_every == 0:
            HarnessContract.sleep(arm, row("SLEEP", "L4", "-", {"steps": 64}))
    out = []
    for ch in "abc":
        for v in (0, 1):
            ask = row("ASK", "T_L", f"{ch}-t", {"cues": ["NAME"], "operands": [op_row(rows[ch][v])],
                                                 "candidate_rows": None, "answer_kind": "NAME"})
            a = HarnessContract.test_ask(arm, ask)
            out.append((ch, a.kind, a.value))
    return out
