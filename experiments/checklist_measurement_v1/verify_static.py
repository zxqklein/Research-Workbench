#!/usr/bin/env python3
"""Independent verification for RW-W2-CHECKLIST-MEASUREMENT-v1.

Checks only behaviors that can change the scientific reading (PREREG s8):
  1. hand-written truth table (independent transcription of PREREG s4, NOT
     produced by run.py's truth function) vs the run's rows;
  2. hand-written order-mark mapping vs the run's rows;
  3. input key uniqueness and 128/16 structure;
  4. behavioral field-permission invariance for all six strategies;
  5. joint AB/BA correctness recomputed from rows vs summary;
  6. UNKNOWN / illegal / missing never shrink denominators (stub-strategy
     test driving run.py's own scorer on synthetic answer patterns);
  7. real run rows contain zero UNKNOWN/missing/illegal (total functions);
  8. summary main_reading equals the recomputed R0-pass & R1-fail set.

Exit code 0 = all checks pass; 1 = any failure.
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Hand-derived from PREREG section 4 (four target-state patterns). This table
# is the independent standard; run.py's truth function must match it, never
# the other way around.
HAND_TRUTH = {
    (0, 0): {"AB": "NO_EXISTENCE_CHANGE", "BA": "NO_EXISTENCE_CHANGE",
             "AA": "NO_EXISTENCE_CHANGE", "BB": "NO_EXISTENCE_CHANGE"},
    (0, 1): {"AB": "APPEAR", "BA": "DISAPPEAR",
             "AA": "NO_EXISTENCE_CHANGE", "BB": "NO_EXISTENCE_CHANGE"},
    (1, 0): {"AB": "DISAPPEAR", "BA": "APPEAR",
             "AA": "NO_EXISTENCE_CHANGE", "BB": "NO_EXISTENCE_CHANGE"},
    (1, 1): {"AB": "NO_EXISTENCE_CHANGE", "BA": "NO_EXISTENCE_CHANGE",
             "AA": "NO_EXISTENCE_CHANGE", "BB": "NO_EXISTENCE_CHANGE"},
}

# Hand-derived from PREREG section 3.
HAND_MARKS = {
    0: {"AB": "ORIGINAL", "BA": "REVERSED", "AA": "ORIGINAL", "BB": "ORIGINAL"},
    1: {"AB": "REVERSED", "BA": "ORIGINAL", "AA": "REVERSED", "BB": "REVERSED"},
}

VALID = ("APPEAR", "DISAPPEAR", "NO_EXISTENCE_CHANGE")


def load_run_module():
    spec = importlib.util.spec_from_file_location(
        "rw_w2_run", os.path.join(HERE, "run.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hand_target_first_second(row):
    """Independent recomputation of actual-order target existence bits."""
    t_a, t_b = row["states"]["t_A"], row["states"]["t_B"]
    first, second = {
        "AB": (t_a, t_b), "BA": (t_b, t_a),
        "AA": (t_a, t_a), "BB": (t_b, t_b),
    }[row["condition"]]
    return first, second


def hand_distractor_first_second(row):
    d_a, d_b = row["states"]["d_A"], row["states"]["d_B"]
    first, second = {
        "AB": (d_a, d_b), "BA": (d_b, d_a),
        "AA": (d_a, d_a), "BB": (d_b, d_b),
    }[row["condition"]]
    return first, second


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--results", required=True,
                        help="results directory produced by run.py")
    args = parser.parse_args(argv)

    with open(args.contract, "r", encoding="utf-8") as fh:
        contract = json.load(fh)
    with open(os.path.join(args.results, "rows.jsonl"), "r",
              encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    with open(os.path.join(args.results, "summary.json"), "r",
              encoding="utf-8") as fh:
        summary = json.load(fh)

    failures = []

    def check(name, ok, detail=""):
        status = "PASS" if ok else "FAIL"
        print("[%s] %s%s" % (status, name, (" -- " + detail) if detail else ""))
        if not ok:
            failures.append(name)

    # 1. hand truth table vs rows
    bad = []
    for row in rows:
        pattern = (row["states"]["t_A"], row["states"]["t_B"])
        expected = HAND_TRUTH[pattern][row["condition"]]
        if row["truth"] != expected:
            bad.append("%s: truth %s != hand %s"
                       % (row["key"], row["truth"], expected))
    check("truth table matches hand-written PREREG s4 table (128 rows)",
          not bad, "; ".join(bad[:5]))

    # 2. hand order-mark mapping vs rows
    bad = []
    for row in rows:
        expected = HAND_MARKS[row["version"]][row["condition"]]
        if row["order_mark"] != expected:
            bad.append("%s: mark %s != hand %s"
                       % (row["key"], row["order_mark"], expected))
    check("order marks match hand-written v0/v1 mapping (128 rows)",
          not bad, "; ".join(bad[:5]))

    # 3. structure and key uniqueness
    keys = [r["key"] for r in rows]
    check("128 rows with 128 unique keys",
          len(rows) == 128 and len(set(keys)) == 128,
          "%d rows, %d unique keys" % (len(rows), len(set(keys))))
    groups = sorted({r["group_id"] for r in rows})
    check("16 groups, each with 4 conditions x 2 versions",
          groups == list(range(16))
          and all(len({r["condition"] for r in rows
                       if r["group_id"] == g}) == 4
                  and len({r["version"] for r in rows
                           if r["group_id"] == g}) == 2
                  for g in groups))

    # 4. behavioral permission invariance
    def constant_under(rows, sid, key_fn):
        buckets = {}
        for row in rows:
            buckets.setdefault(key_fn(row), set()).add(row["outputs"][sid])
        bad = {k: sorted(v) for k, v in buckets.items() if len(v) > 1}
        return not bad, "%d buckets, offending: %s" % (
            len(buckets), json.dumps(bad, sort_keys=True)[:200]) if bad \
            else "%d buckets all constant" % len(buckets)

    ok, detail = constant_under(
        rows, "SLOT_ID",
        lambda r: (r["condition"], r["order_mark"]))
    check("SLOT_ID output constant given (condition, order_mark) "
          "-> cannot be reading states", ok, detail)
    ok, detail = constant_under(rows, "CONST_NULL", lambda r: True)
    check("CONST_NULL constant everywhere", ok, detail)
    ok, detail = constant_under(rows, "CONST_APPEAR", lambda r: True)
    check("CONST_APPEAR constant everywhere", ok, detail)
    for sid, key_fn, what in [
        ("ORACLE", hand_target_first_second,
         "(target_exist_first, target_exist_second)"),
        ("INVERT_TARGET", hand_target_first_second,
         "(target_exist_first, target_exist_second)"),
        ("DISTRACTOR", hand_distractor_first_second,
         "(distractor_exist_first, distractor_exist_second)"),
    ]:
        ok, detail = constant_under(rows, sid, key_fn)
        check("%s output constant given %s" % (sid, what), ok, detail)

    # 5. joint AB/BA correctness recomputed from rows vs summary
    mod = load_run_module()
    bad = []
    for spec in contract["strategies"]:
        sid = spec["id"]
        recomputed = 0
        for g in range(16):
            for v in (0, 1):
                ab = next(r for r in rows if r["key"] == "g%02d|AB|v%d" % (g, v))
                ba = next(r for r in rows if r["key"] == "g%02d|BA|v%d" % (g, v))
                ab_ok = ab["outputs"][sid] == ab["truth"]
                ba_ok = ba["outputs"][sid] == ba["truth"]
                recomputed += int(ab_ok and ba_ok)
                if ab["outputs"][sid] not in VALID or \
                        ba["outputs"][sid] not in VALID:
                    bad.append("%s v%d non-valid answer in joint check" % (sid, g))
        reported = summary["strategies"][sid]["r1"]["joint_ab_ba"]["pass"]
        if recomputed != reported:
            bad.append("%s: recomputed joint %d != summary %d"
                       % (sid, recomputed, reported))
    check("joint AB/BA correctness recomputed from rows matches summary "
          "(six strategies)", not bad, "; ".join(bad[:5]))

    # 6. stub-strategy test: UNKNOWN/illegal/missing never shrink denominators
    fake_rows = mod.build_rows(contract)
    pattern = {}
    n_unknown = n_missing = n_illegal = n_wrong = 0
    for i, row in enumerate(fake_rows):
        if i % 13 == 0:
            ans, n_unknown = "UNKNOWN", n_unknown + 1
        elif i % 17 == 0:
            ans, n_missing = None, n_missing + 1
        elif i % 19 == 0:
            ans, n_illegal = "MAYBE_APPEAR", n_illegal + 1
        elif i % 5 == 0:
            ans = "APPEAR" if row["truth"] == "DISAPPEAR" else "DISAPPEAR"
            n_wrong += 1
        else:
            ans = row["truth"]
        pattern[row["key"]] = ans
    for row in fake_rows:
        row["outputs"] = {"STUB": pattern[row["key"]]}
    r0 = mod.score_r0(fake_rows, "STUB", contract)
    r1 = mod.score_r1(fake_rows, "STUB", contract)
    acc = r1["accounting"]
    check("stub: MFT denominator stays 128 with UNKNOWN/missing/illegal present",
          acc["rows"] == 128 and r1["mft"]["total"] == 128,
          "rows=%d mft_total=%d" % (acc["rows"], r1["mft"]["total"]))
    check("stub: buckets counted, none folded into correct",
          acc["unknown"] == n_unknown and acc["missing"] == n_missing
          and acc["illegal"] == n_illegal and acc["wrong"] == n_wrong
          and acc["correct"] + acc["wrong"] + acc["unknown"]
          + acc["missing"] + acc["illegal"] == 128,
          "correct=%d wrong=%d unknown=%d missing=%d illegal=%d"
          % (acc["correct"], acc["wrong"], acc["unknown"],
             acc["missing"], acc["illegal"]))
    check("stub: R0/R1/INV/AA-BB denominators fixed at 16/64/64/64",
          r0["relation"]["total"] == 16 and r0["aa_bb_nochange"]["total"] == 64
          and r1["inv"]["total"] == 64 and r1["joint_ab_ba"]["total"] == 32
          and r1["dir"]["change_rows_total"] == 32)
    all_unknown = [dict(r, outputs={"STUB": "UNKNOWN"}) for r in fake_rows]
    r1u = mod.score_r1(all_unknown, "STUB", contract)
    check("stub: all-UNKNOWN strategy keeps every denominator and fails R1",
          r1u["accounting"]["unknown"] == 128
          and r1u["mft"]["total"] == 128
          and r1u["mft"]["correct"] == 0
          and r1u["inv"]["total"] == 64 and not r1u["inv"]["pass"]
          and not r1u["pass"])

    # 7. real run rows are total functions (zero non-valid outputs)
    bad = []
    for row in rows:
        for sid, out in row["outputs"].items():
            if out not in VALID:
                bad.append("%s/%s: %r" % (row["key"], sid, out))
    check("real run: all six strategies returned valid answers on all 128 rows",
          not bad, "; ".join(bad[:5]))

    # 8. main reading recomputed from summary flags
    recomputed_main = sorted(
        sid for sid, s in summary["strategies"].items()
        if sid != "ORACLE" and s["r0"]["pass"] and not s["r1"]["pass"])
    reported_main = sorted(summary["main_reading"]["pass_r0_fail_r1"])
    check("main reading (pass R0, fail R1) recomputed from summary matches",
          recomputed_main == reported_main,
          "recomputed=%s reported=%s" % (recomputed_main, reported_main))
    oracle = summary["strategies"]["ORACLE"]
    check("ORACLE passes R0 and R1 (implementation self-check)",
          oracle["r0"]["pass"] and oracle["r1"]["pass"])

    print()
    if failures:
        print("VERIFICATION FAILED: %d check(s): %s"
              % (len(failures), ", ".join(failures)))
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
