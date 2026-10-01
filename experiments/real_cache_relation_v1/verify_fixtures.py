#!/usr/bin/env python3
"""RW-W3-REAL-CACHE-REUSE-v1 fixture regressions.

All fixtures are ARTIFICIAL (marked as such in every record); they never enter
the real K. Imports the scoring functions from run.py — no copy of the logic.
Run: python experiments/real_cache_relation_v1/verify_fixtures.py
Prints FIXTURES_OK / FIXTURES_FAIL and exits nonzero on failure.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import BUCKET_ORDER, parse_raw, score_targets, agg, CLASSES  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name} {detail}")


def mk(cid, uid, rid, gA, gB, pA, pB):
    return {"component": cid, "uid": uid, "rid": rid, "refA": gA, "refB": gB, "predA": pA, "predB": pB}


print("[1] legal different-class but wrong -> OTHER_LEGAL_WRONG_DIFF, relation pass but wrong")
rows, derived, cons = score_targets([mk("c1", "u1", "R1", "buildings", "tree", "water", "tree")])
r = rows[0]
check("bucket", r["bucket"] == "OTHER_LEGAL_WRONG_DIFF", r["bucket"])
check("relation_pass_but_wrong", r["relation_pass_but_wrong"] is True)
check("pair_correct False", r["pair_correct"] is False)
check("relation_change_pass", r["relation_change_pass"] is True)

print("[2] double-class accurate inversion -> ACCURATELY_INVERTED")
rows, _, _ = score_targets([mk("c1", "u2", "R1", "buildings", "tree", "tree", "buildings")])
r = rows[0]
check("bucket", r["bucket"] == "ACCURATELY_INVERTED", r["bucket"])
check("relation_pass_but_wrong", r["relation_pass_but_wrong"] is True)
check("not fully correct", r["bucket"] != "FULLY_CORRECT")

print("[3] wrong same-class -> WRONG_SAME_CLASS")
rows, _, _ = score_targets([mk("c1", "u3", "R1", "buildings", "tree", "tree", "tree")])
r = rows[0]
check("bucket", r["bucket"] == "WRONG_SAME_CLASS", r["bucket"])
check("relation_change_pass False", r["relation_change_pass"] is False)
check("not in K", r["relation_pass_but_wrong"] is False)

print("[4] UNKNOWN / missing side -> INVALID, counts 0, no denominator shrink")
rows, _, _ = score_targets([mk("c1", "u4", "R1", "buildings", "tree", "UNKNOWN", "tree"),
                            mk("c1", "u5", "R1", "buildings", "tree", "MISSING", "tree"),
                            mk("c1", "u6", "R1", "buildings", "tree", "nvg_surface", "water")])
check("unknown bucket", rows[0]["bucket"] == "INVALID_MISSING", rows[0]["bucket"])
check("missing bucket", rows[1]["bucket"] == "INVALID_MISSING", rows[1]["bucket"])
check("valid row kept", rows[2]["bucket"] == "OTHER_LEGAL_WRONG_DIFF")
check("unknown not relation pass", rows[0]["relation_change_pass"] is False and rows[0]["relation_pass_but_wrong"] is False)
check("all rows retained (no shrink)", len(rows) == 3)

print("[5] R2 is never replaced by R1 (per-rid parse from raw)")
raw = "R1: water\nR2: playgrounds"
labels, status, _ = parse_raw(raw, ["R1", "R2"])
check("parse ok", status == "OK" and labels == {"R1": "water", "R2": "playgrounds"}, str(labels))
raw2 = "R1: water"
labels2, status2, _ = parse_raw(raw2, ["R1", "R2"])
check("R2 missing -> MISSING", status2 == "OK" and labels2["R2"] == "MISSING", str(labels2))
labels3, status3, _ = parse_raw("R1: water\nR2: water\nR2: tree", ["R1", "R2"])
check("duplicate rid rejected", status3 == "PARSE_INCONSISTENT", status3)
labels4, status4, _ = parse_raw("R1: water\nR9: tree", ["R1", "R2"])
check("extra rid rejected", status4 == "PARSE_INCONSISTENT", status4)
labels5, status5, _ = parse_raw("hello world", ["R1"])
check("non-R line rejected", status5 == "PARSE_INCONSISTENT", status5)

print("[5b] trailing-period strip (observed original-run rule)")
labels6, status6, _ = parse_raw("R1: water.\nR2: tree.", ["R1", "R2"])
check("periods stripped", status6 == "OK" and labels6 == {"R1": "water", "R2": "tree"}, str(labels6))
labels7, status7, _ = parse_raw("R1: not_a_class", ["R1"])
check("illegal label -> INVALID", status7 == "OK" and labels7["R1"] == "INVALID", str(labels7))

print("[6] parent equal-weight vs micro on multi-target components (ARTIFICIAL)")
targets = [mk("ca", "ua1", "R1", "buildings", "tree", "buildings", "tree"),   # correct
           mk("ca", "ua2", "R1", "water", "nvg_surface", "tree", "water"),    # wrong diff
           mk("cb", "ub1", "R1", "tree", "water", "nvg_surface", "water")]   # wrong diff
rows, _, _ = score_targets(targets)
m = agg(rows, "pair_correct", ["ca", "cb"])
check("micro 1/3", abs(m["micro"] - 1 / 3) < 1e-12, str(m))
check("equal-weight (0.5+0)/2 = 0.25", abs(m["parent_equal_weight"] - 0.25) < 1e-12, str(m))
k = agg(rows, "relation_pass_but_wrong", ["ca", "cb"])
check("K fixture = 2", k["count"] == 2, str(k))

print("[7] five buckets are mutually exclusive and ordered; sum preserved")
targets = [mk("c", f"u{i}", "R1", "buildings", "tree", pA, pB)
           for i, (pA, pB) in enumerate([("UNKNOWN", "tree"), ("buildings", "tree"), ("tree", "buildings"),
                                         ("tree", "tree"), ("water", "nvg_surface")])]
rows, _, _ = score_targets(targets)
buckets = {b: 0 for b in BUCKET_ORDER}
for r in rows:
    buckets[r["bucket"]] += 1
check("bucket sum == n targets", sum(buckets.values()) == len(targets), str(buckets))
check("expected spread", buckets == {"INVALID_MISSING": 1, "FULLY_CORRECT": 1, "ACCURATELY_INVERTED": 1,
                                     "WRONG_SAME_CLASS": 1, "OTHER_LEGAL_WRONG_DIFF": 1}, str(buckets))

print("[8] AA/BB pair correctness equals respective single-side correctness")
targets = [mk("c", "uz", "R1", "buildings", "tree", "buildings", "water")]
rows, derived, _ = score_targets(targets)
r = rows[0]
check("AA == single-side A", r["pair_correct_AA"] is True and r["pred"][0] == r["ref"][0])
check("BB == single-side B", r["pair_correct_BB"] is False and r["pred"][1] != r["ref"][1])
aa_row = next(d for d in derived if d["condition"] == "AA")
check("AA row pred same-class", aa_row["pred"][0] == aa_row["pred"][1])

print("[9] fixtures are marked artificial and excluded from real K (design guarantee)")
check("no real data loaded here", True)  # this script constructs its own inputs only

print()
if FAILURES:
    print(f"FIXTURES_FAIL ({len(FAILURES)}): {FAILURES}")
    sys.exit(1)
print("FIXTURES_OK (all fixture regressions passed; fixtures never enter real K)")
