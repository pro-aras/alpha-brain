# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:43 +0400 (the file's own mtime; the first draft of this header said 21:44 «from `date`», typed ahead of the clock — corrected) — the seat's step (1) of 21:34 for brain-long-3's production FALLBACK ORIGIN: «build the SOURCE COPY of brain-long-3's tape from the live root (read-only opens), timed, and
# print its size; no child runs». This script calls the reader's own `build_source_copy` (the function the origin run calls first) and nothing else: it opens the life's tape, journal, truth and genomes read-only, writes ONLY under --dest, and prints
# one JSON line (rows, files, bytes, build seconds, this process's own peak RSS, the manifest hash, and the copy's re-verification). Run BY PATH with -B -I, through slot; usage:
#   python3 -B -I measure_source_copy.py --reader <a checkout of the reader> --root <life> --grader-code <pinned grader checkout> --dest <an empty dir outside every life>
import argparse
import json
import resource
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--reader", required=True)
ap.add_argument("--root", required=True)
ap.add_argument("--grader-code", required=True)
ap.add_argument("--dest", required=True)
a = ap.parse_args()
sys.path.insert(0, str(Path(a.reader) / "tools" / "brain"))
import resit as R                                   # noqa: E402  (the reader: the standard library only)

root, dest = Path(a.root), Path(a.dest)
assert not str(dest).startswith(str(root)), "the destination must be outside the life"
t0 = time.time()
dax = R.dax_index_of(a.grader_code)
sc = R.build_source_copy(root, dest, dax_index=dax)
t1 = time.time()
problems = R.verify_source_copy(dest, sc["source_copy_sha256"])
t2 = time.time()
out = {k: sc[k] for k in ("cut_seq", "rows", "torn_lines_tape", "torn_lines_journal", "payloads_kept", "truth_files", "journal_files", "genomes", "n_manifest_entries", "bytes", "source_copy_sha256", "sitting_sets", "build_s")}
out.update({"dax_index": dax, "wall_build_s": round(t1 - t0, 3), "verify_s": round(t2 - t1, 3), "verify_problems": problems,
            "self_maxrss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1), "reader_sha256": R.sha256_file(R.RESIT_PY)})
print(json.dumps(out, sort_keys=True))
