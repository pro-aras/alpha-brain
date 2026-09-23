# READER-LAG-0923 item 2: the LAG root read by the old and the new reader — the facts the brief names, read from results.json and the out dirs.
import json, sys
from pathlib import Path
old_d, new_d, root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, "/data/dev/genome-wt-reader-lag")
from creature.replay import compare, read_mind_journal
B = json.load(open(old_d / "results.json")); A = json.load(open(new_d / "results.json"))
jr = [json.loads(l) for l in open(root / "journal" / "2026-09-22.jsonl")]
mind_rows_root = [r for r in jr if r.get("event") not in ("start", "snapshot", "stop", "exam")]
live_old = sum(1 for _ in open(old_d / "live-journal.jsonl")); live_new = sum(1 for _ in open(new_d / "live-journal.jsonl"))
all_old = [json.loads(l) for l in open(old_d / "tape" / "ALL.jsonl")]; all_new = [json.loads(l) for l in open(new_d / "tape" / "ALL.jsonl")]
last_eye_le_750 = max(r["seq"] for r in all_old if r["sense"] == "eye" and r["seq"] <= 750)
# the OLD reader replayed the WHOLE 850-row tape and closed at its head: its first divergence from the live journal (which ends at the mind's last
# consumed seq 750) is the lag's — either AT the last eye row ≤ 750 (a row-count difference: the live close() landed a pending think there and
# the whole-tape replay did not) or at the FIRST replayed row past 750 («missing from --against»). Which one is read off the record: a `think`
# row at the last eye row ≤ 750 in the root's journal that carries no `launched_at` boundary at a think boundary... simpler and exact: compare
# the old replay's rows ≤ 750 with the live rows ≤ 750 (must be identical — the divergence is never the mind's), then the first replay seq > 750.
u1_old = read_mind_journal(old_d / "twins" / "unblinded-1" / "mind-journal.jsonl"); live_o = read_mind_journal(old_d / "live-journal.jsonl")
below = compare([r for r in u1_old if int(r["seq"]) <= 750], [r for r in live_o if int(r["seq"]) <= 750], ignore={"hash"})
first_past = min((int(r["seq"]) for r in u1_old if int(r["seq"]) > 750), default=None)
expected_old = (first_past, "<missing from --against>") if below is None else below
print(json.dumps({
  "root_journal": {"mind_rows": len(mind_rows_root), "last_mind_seq": max(int(r["seq"]) for r in mind_rows_root), "rows_at_last_eye": [sorted(k for k in r if k != "seq") for r in mind_rows_root if int(r["seq"]) == last_eye_le_750]},
  "OLD": {"REPLAY": {k: B["REPLAY"].get(k) for k in ("pass", "vs_live", "two_replays", "mind_rows", "closed_whole", "plant_seq", "plant_caught", "hash_masked")},
          "tape_rows": B["tape_rows"], "live_journal_rows": live_old, "ALL_jsonl_last_seq": all_old[-1]["seq"], "ALIVE_hours": B["ALIVE"]["hours_on_tape"], "verdict": B["verdict"], "failed": B["marks_failed"]},
  "NEW": {"REPLAY": {k: A["REPLAY"].get(k) for k in ("pass", "vs_live", "two_replays", "mind_rows", "closed_whole", "plant_seq", "plant_caught", "hash_masked", "cut_seq")},
          "tape_rows": A["tape_rows"], "tape_rows_world": A.get("tape_rows_world"), "live_journal_rows": live_new, "ALL_jsonl_last_seq": all_new[-1]["seq"], "ALIVE_hours": A["ALIVE"]["hours_on_tape"],
          "ALIVE_reach": {k: A["ALIVE"].get(k) for k in ("mind_reach_full_hours", "hours_beyond_the_minds_reach")}, "verdict": A["verdict"], "failed": A["marks_failed"],
          "LAG": {k: A["LAG"].get(k) for k in ("cut", "mind_last_seq", "source", "time_cut_seq", "tape_head_seq", "cut_seq", "rows_unconsumed", "rows_cut_by_lag", "world_hours_unconsumed", "hours_lived", "hours_on_tape_world", "status_backlog_rows", "backlog_reconciles")},
          "backlog_series": {k: A["LAG"]["backlog_series"].get(k) for k in ("n", "max", "last", "first_over_100", "per_hour_max")},
          "COST_sleeps_window_end_is": ((A["marks"]["viii_cost"].get("lag") or {}).get("sleeps_window_end_is")),
          "QUESTION_hours_lived": A["marks"]["QUESTION"].get("hours_lived"), "EVOLVE_hours_lived": A["marks"]["EVOLVE"].get("hours_lived"), "THREAD_lag_note": bool(A["marks"]["THREAD"].get("lag_note"))},
  "old_replay_vs_live_below_750": below, "old_replay_first_seq_past_750": first_past,
  "expected": {"old_vs_live": expected_old, "new_vs_live": None, "new_closed_whole": True, "old_closed_whole": True, "lag_rows": 100}}, indent=1, default=str))
ok = (B["REPLAY"]["vs_live"] is not None and tuple(B["REPLAY"]["vs_live"]) == tuple(expected_old) and below is None and B["REPLAY"]["closed_whole"] is True
      and A["REPLAY"]["vs_live"] is None and A["REPLAY"]["closed_whole"] is True and A["LAG"]["rows_unconsumed"] == 100 and A["LAG"]["cut"] is True
      and A["LAG"]["backlog_reconciles"] is True and A["REPLAY"]["two_replays"] is None and A["REPLAY"]["plant_caught"] is True)
print("LAG E2E:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
