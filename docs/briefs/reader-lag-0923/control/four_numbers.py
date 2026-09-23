# The premise, READ not quoted (#194): per closed root, the tape's last seq, the journal's last MIND seq, STATUS last_seq, ledger last_seq, a stop event, STATUS.crash.
import json, sys
from pathlib import Path
for root in map(Path, sys.argv[1:]):
    tape = []; 
    for f in sorted((root / "tape").glob("*.jsonl")): tape += [json.loads(l) for l in open(f) if l.strip()]
    J = []
    for f in sorted((root / "journal").glob("*.jsonl")): J += [json.loads(l) for l in open(f) if l.strip()]
    mind = [r for r in J if r.get("event") not in ("start", "sense_restart", "snapshot", "stop", "exam") and r.get("seq") is not None]
    st = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
    led = json.loads((root / "state" / "ledger.json").read_text())
    print(json.dumps({"root": root.name, "tape_last": tape[-1]["seq"], "tape_rows": len(tape), "journal_last_mind_seq": max(int(r["seq"]) for r in mind), "status_last_seq": st.get("last_seq"),
                      "ledger_last_seq": led.get("last_seq"), "stop_event": any(r.get("event") == "stop" for r in J), "status_crash": st.get("crash"), "status_backlog": st.get("mind_backlog_rows"),
                      "events": sorted({r["event"] for r in J if "event" in r}), "first_at": tape[0]["at"], "last_at": tape[-1]["at"]}))
