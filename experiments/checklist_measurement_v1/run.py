#!/usr/bin/env python3
"""Deterministic enumeration and scoring for RW-W2-CHECKLIST-MEASUREMENT-v1.

Python standard library only, no randomness, no third-party packages.
Generates all 128 controlled inputs from the frozen contract, runs the six
fixed strategies on permission-filtered views, scores both contracts
(R0 relation threshold, R1 full contract) with fixed denominators, and
writes rows.jsonl, summary.json, manifest.json and counterexample files.

Interface (frozen in PREREG section 8):
    python3 run.py --contract contract.json --prereg-commit <sha> --out <new dir>
Refuses to write into an existing non-empty results directory.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone

VALID_ANSWERS = ("APPEAR", "DISAPPEAR", "NO_EXISTENCE_CHANGE")
DIRECTIONAL = ("APPEAR", "DISAPPEAR")
ORACLE_ID = "ORACLE"


# ---------------------------------------------------------------- enumeration

def direction(a, b):
    """PREREG section 4 direction rule on two existence bits."""
    if a == 0 and b == 1:
        return "APPEAR"
    if a == 1 and b == 0:
        return "DISAPPEAR"
    return "NO_EXISTENCE_CHANGE"


def truth_for_condition(states, condition):
    t_a, t_b = states["t_A"], states["t_B"]
    if condition == "AB":
        return direction(t_a, t_b)
    if condition == "BA":
        return direction(t_b, t_a)
    if condition in ("AA", "BB"):
        return "NO_EXISTENCE_CHANGE"
    raise ValueError("unknown condition: %r" % (condition,))


def build_rows(contract):
    """Deterministically expand the 16 groups to 128 controlled input rows."""
    enum = contract["enumeration"]
    rows = []
    for g in range(enum["group_count"]):
        states = {
            "t_A": (g >> 3) & 1,
            "t_B": (g >> 2) & 1,
            "d_A": (g >> 1) & 1,
            "d_B": g & 1,
        }
        for cond in enum["conditions"]:
            frames = []
            for fid in enum["condition_frame_order"][cond]:
                frames.append({
                    "frame_id": fid,
                    "background_id": enum["backgrounds"][fid],
                    "target_exists": states["t_A"] if fid == "A" else states["t_B"],
                    "distractor_exists": states["d_A"] if fid == "A" else states["d_B"],
                })
            for v in enum["versions"]:
                rows.append({
                    "key": "g%02d|%s|v%d" % (g, cond, v),
                    "group_id": g,
                    "states": dict(states),
                    "condition": cond,
                    "version": v,
                    "order_mark": enum["order_marks"][str(v)][cond],
                    "frames": [dict(f) for f in frames],
                    "truth": truth_for_condition(states, cond),
                })
    return rows


# --------------------------------------------- strategies (permission views)

def strat_oracle(view):
    return direction(view["target_exist_first"], view["target_exist_second"])


def strat_const_null(view):
    return "NO_EXISTENCE_CHANGE"


def strat_const_appear(view):
    return "APPEAR"


def strat_slot_id(view):
    if view["frame_id_first"] == view["frame_id_second"]:
        return "NO_EXISTENCE_CHANGE"
    return "APPEAR" if view["order_mark"] == "ORIGINAL" else "DISAPPEAR"


def strat_invert_target(view):
    ans = direction(view["target_exist_first"], view["target_exist_second"])
    if ans == "APPEAR":
        return "DISAPPEAR"
    if ans == "DISAPPEAR":
        return "APPEAR"
    return ans


def strat_distractor(view):
    return direction(view["distractor_exist_first"], view["distractor_exist_second"])


STRATEGY_FUNCS = {
    "ORACLE": strat_oracle,
    "CONST_NULL": strat_const_null,
    "CONST_APPEAR": strat_const_appear,
    "SLOT_ID": strat_slot_id,
    "INVERT_TARGET": strat_invert_target,
    "DISTRACTOR": strat_distractor,
}


def view_fields(row):
    """Every field a strategy could request; permission filter picks from this."""
    return {
        "frame_id_first": row["frames"][0]["frame_id"],
        "frame_id_second": row["frames"][1]["frame_id"],
        "target_exist_first": row["frames"][0]["target_exists"],
        "target_exist_second": row["frames"][1]["target_exists"],
        "distractor_exist_first": row["frames"][0]["distractor_exists"],
        "distractor_exist_second": row["frames"][1]["distractor_exists"],
        "order_mark": row["order_mark"],
    }


def run_strategies(rows, contract):
    """Attach each strategy's answer, reading only its contract-declared fields."""
    for spec in contract["strategies"]:
        if spec["id"] not in STRATEGY_FUNCS:
            raise SystemExit("contract names unknown strategy: %s" % spec["id"])
    for row in rows:
        fields = view_fields(row)
        outs = {}
        for spec in contract["strategies"]:
            # KeyError here would mean contract/implementation field mismatch.
            view = {k: fields[k] for k in spec["reads"]}
            outs[spec["id"]] = STRATEGY_FUNCS[spec["id"]](view)
        row["outputs"] = outs
    return rows


# ------------------------------------------------------------------- scoring

def classify_answer(ans):
    if ans is None:
        return "missing"
    if ans == "UNKNOWN":
        return "unknown"
    if ans in VALID_ANSWERS:
        return "valid"
    return "illegal"


def is_correct(row, ans):
    return classify_answer(ans) == "valid" and ans == row["truth"]


def _index(rows):
    return {r["key"]: r for r in rows}


def _relation_cells(rows, sid, enum):
    """Change-group AB/BA order-swap relation: 8 groups x 2 versions = 16 cells."""
    per_version = {v: {"pass": 0, "total": 0} for v in enum["versions"]}
    failures = []
    total = passed = 0
    idx = _index(rows)
    for g in enum["change_groups"]:
        for v in enum["versions"]:
            ab = idx["g%02d|AB|v%d" % (g, v)]["outputs"][sid]
            ba = idx["g%02d|BA|v%d" % (g, v)]["outputs"][sid]
            ok = (
                classify_answer(ab) == "valid" and ab in DIRECTIONAL
                and classify_answer(ba) == "valid" and ba in DIRECTIONAL
                and {ab, ba} == set(DIRECTIONAL)
            )
            total += 1
            passed += int(ok)
            per_version[v]["total"] += 1
            per_version[v]["pass"] += int(ok)
            if not ok:
                failures.append("g%02d|AB/BA|v%d" % (g, v))
    return {"pass": passed, "total": total, "per_version": per_version,
            "failed_cells": failures}


def _aa_bb_cells(rows, sid, enum):
    """AA/BB empty judgment over all 16 groups x 2 conditions x 2 versions = 64."""
    per_version = {v: {"pass": 0, "total": 0} for v in enum["versions"]}
    failures = []
    total = passed = 0
    for row in rows:
        if row["condition"] not in ("AA", "BB"):
            continue
        ans = row["outputs"][sid]
        ok = classify_answer(ans) == "valid" and ans == "NO_EXISTENCE_CHANGE"
        total += 1
        passed += int(ok)
        per_version[row["version"]]["total"] += 1
        per_version[row["version"]]["pass"] += int(ok)
        if not ok:
            failures.append(row["key"])
    return {"pass": passed, "total": total, "per_version": per_version,
            "failed_rows": failures}


def score_r0(rows, sid, contract):
    enum = contract["enumeration"]
    relation = _relation_cells(rows, sid, enum)
    aa_bb = _aa_bb_cells(rows, sid, enum)
    r0spec = contract["contracts"]["R0"]
    if relation["total"] != r0spec["change_relation_pairs"]["denominator"]:
        raise SystemExit("R0 relation denominator mismatch: %d != contract"
                         % relation["total"])
    if aa_bb["total"] != r0spec["aa_bb_nochange_rows"]["denominator"]:
        raise SystemExit("R0 AA/BB denominator mismatch: %d != contract"
                         % aa_bb["total"])
    return {
        "relation": relation,
        "aa_bb_nochange": aa_bb,
        "pass": relation["pass"] == relation["total"]
        and aa_bb["pass"] == aa_bb["total"],
    }


def score_r1(rows, sid, contract):
    enum = contract["enumeration"]
    r1spec = contract["contracts"]["R1"]

    # MFT over all rows, decomposed by true class x condition x version.
    mft_correct = 0
    wrong = unknown = missing = illegal = 0
    wrong_rows = []
    cells = {}
    cond_version = {}
    for row in rows:
        ans = row["outputs"][sid]
        cls = classify_answer(ans)
        correct = cls == "valid" and ans == row["truth"]
        mft_correct += int(correct)
        if cls == "valid" and not correct:
            wrong += 1
            wrong_rows.append(row["key"])
        elif cls == "unknown":
            unknown += 1
        elif cls == "missing":
            missing += 1
        elif cls == "illegal":
            illegal += 1
        cell = cells.setdefault((row["truth"], row["condition"], row["version"]),
                                {"correct": 0, "total": 0})
        cell["total"] += 1
        cell["correct"] += int(correct)
        cv = cond_version.setdefault((row["condition"], row["version"]),
                                     {"correct": 0, "total": 0})
        cv["total"] += 1
        cv["correct"] += int(correct)
    mft_decomp = {
        "%s|%s|v%d" % k: cells[k] for k in sorted(cells)
    }
    mft_cond_version = {
        "%s|v%d" % k: cond_version[k] for k in sorted(cond_version)
    }

    # Joint AB/BA correctness: group x version pairs, both rows correct.
    joint_pass = joint_total = 0
    joint_per_version = {v: {"pass": 0, "total": 0} for v in enum["versions"]}
    joint_failures = []
    idx = _index(rows)
    for g in range(enum["group_count"]):
        for v in enum["versions"]:
            ab_row = idx["g%02d|AB|v%d" % (g, v)]
            ba_row = idx["g%02d|BA|v%d" % (g, v)]
            ok = (is_correct(ab_row, ab_row["outputs"][sid])
                  and is_correct(ba_row, ba_row["outputs"][sid]))
            joint_total += 1
            joint_pass += int(ok)
            joint_per_version[v]["total"] += 1
            joint_per_version[v]["pass"] += int(ok)
            if not ok:
                joint_failures.append("g%02d|AB+BA|v%d" % (g, v))

    # DIR: relation and answer correctness reported separately.
    relation = _relation_cells(rows, sid, enum)
    change_groups = set(enum["change_groups"])
    change_correct = change_total = 0
    change_wrong_rows = []
    change_pairs_pass = change_pairs_total = 0
    for row in rows:
        if row["group_id"] in change_groups and row["condition"] in ("AB", "BA"):
            change_total += 1
            ok = is_correct(row, row["outputs"][sid])
            change_correct += int(ok)
            if not ok:
                change_wrong_rows.append(row["key"])
    for g in enum["change_groups"]:
        for v in enum["versions"]:
            ab_row = idx["g%02d|AB|v%d" % (g, v)]
            ba_row = idx["g%02d|BA|v%d" % (g, v)]
            change_pairs_total += 1
            change_pairs_pass += int(
                is_correct(ab_row, ab_row["outputs"][sid])
                and is_correct(ba_row, ba_row["outputs"][sid]))

    # INV: both versions valid answers AND equal; non-answers never count.
    inv_pass = inv_total = 0
    inv_per_condition = {c: {"pass": 0, "total": 0} for c in enum["conditions"]}
    inv_failures = []
    for g in range(enum["group_count"]):
        for cond in enum["conditions"]:
            a0 = idx["g%02d|%s|v0" % (g, cond)]["outputs"][sid]
            a1 = idx["g%02d|%s|v1" % (g, cond)]["outputs"][sid]
            ok = (classify_answer(a0) == "valid"
                  and classify_answer(a1) == "valid" and a0 == a1)
            inv_total += 1
            inv_pass += int(ok)
            inv_per_condition[cond]["total"] += 1
            inv_per_condition[cond]["pass"] += int(ok)
            if not ok:
                inv_failures.append("g%02d|%s" % (g, cond))

    aa_bb = _aa_bb_cells(rows, sid, enum)

    # Denominator checks against the frozen contract.
    if len(rows) != r1spec["mft_rows"]["denominator"]:
        raise SystemExit("R1 MFT denominator mismatch: %d" % len(rows))
    if joint_total != r1spec["joint_ab_ba_pairs"]["denominator"]:
        raise SystemExit("R1 joint denominator mismatch: %d" % joint_total)
    if relation["total"] != r1spec["dir_relation_pairs"]["denominator"]:
        raise SystemExit("R1 DIR relation denominator mismatch: %d"
                         % relation["total"])
    if change_total != r1spec["dir_change_rows"]["denominator"]:
        raise SystemExit("R1 DIR change-rows denominator mismatch: %d"
                         % change_total)
    if inv_total != r1spec["inv_pairs"]["denominator"]:
        raise SystemExit("R1 INV denominator mismatch: %d" % inv_total)
    if aa_bb["total"] != r1spec["aa_bb_nochange_rows"]["denominator"]:
        raise SystemExit("R1 AA/BB denominator mismatch: %d" % aa_bb["total"])

    accounting = {
        "rows": len(rows),
        "correct": mft_correct,
        "wrong": wrong,
        "wrong_rows": wrong_rows,
        "unknown": unknown,
        "missing": missing,
        "illegal": illegal,
    }
    components = {
        "mft_all_correct": mft_correct == r1spec["mft_rows"]["denominator"],
        "joint_all_correct": joint_pass == r1spec["joint_ab_ba_pairs"]["denominator"],
        "dir_relation_all": relation["pass"] == r1spec["dir_relation_pairs"]["denominator"],
        "dir_change_rows_all_correct": change_correct == r1spec["dir_change_rows"]["denominator"],
        "inv_all_pairs": inv_pass == r1spec["inv_pairs"]["denominator"],
        "aa_bb_all": aa_bb["pass"] == r1spec["aa_bb_nochange_rows"]["denominator"],
        "no_unknown_missing_illegal": unknown == 0 and missing == 0 and illegal == 0,
    }
    return {
        "mft": {
            "correct": mft_correct,
            "total": len(rows),
            "by_class_condition_version": mft_decomp,
            "by_condition_version": mft_cond_version,
        },
        "joint_ab_ba": {
            "pass": joint_pass, "total": joint_total,
            "per_version": joint_per_version, "failed_pairs": joint_failures,
        },
        "dir": {
            "relation": relation,
            "change_rows_correct": change_correct,
            "change_rows_total": change_total,
            "change_wrong_rows": change_wrong_rows,
            "change_pairs_both_correct": change_pairs_pass,
            "change_pairs_total": change_pairs_total,
        },
        "inv": {
            "pass": inv_pass, "total": inv_total,
            "per_condition": inv_per_condition, "failed_pairs": inv_failures,
        },
        "aa_bb_nochange": aa_bb,
        "accounting": accounting,
        "components": components,
        "failed_components": [k for k, ok in components.items() if not ok],
        "pass": all(components.values()),
    }


# ------------------------------------------------------- main reading + dumps

def build_summary(rows, contract, per_strategy):
    enum = contract["enumeration"]
    strategies_out = {}
    main_list = []
    r1_misses = []
    for spec in contract["strategies"]:
        sid = spec["id"]
        r0 = per_strategy[sid]["r0"]
        r1 = per_strategy[sid]["r1"]
        strategies_out[sid] = {
            "reads": spec["reads"],
            "rule": spec["rule"],
            "r0": r0,
            "r1": r1,
            "r0_pass_r1_fail": bool(r0["pass"] and not r1["pass"]),
        }
        if sid != ORACLE_ID:
            if r0["pass"] and not r1["pass"]:
                main_list.append(sid)
            if not r1["pass"]:
                r1_misses.append({"strategy": sid,
                                  "failed_components": r1["failed_components"]})
    summary = {
        "task_id": contract["task_id"],
        "contract_version": contract["contract_version"],
        "enumeration": {
            "groups": enum["group_count"],
            "rows": len(rows),
            "conditions": enum["conditions"],
            "versions": enum["versions"],
            "change_groups": enum["change_groups"],
            "unit_note": "16 controlled groups expanded to 128 controlled inputs; "
                         "not 128 independent samples",
        },
        "strategies": strategies_out,
        "main_reading": {
            "definition": contract["main_reading"]["definition"],
            "non_oracle_strategies": 5,
            "pass_r0_fail_r1": main_list,
            "count": len(main_list),
            "counterexample_files": ["counterexamples/%s.json" % s
                                     for s in main_list],
        },
        "auxiliary": {
            "r1_misses": r1_misses,
            "r0_pass": [sid for sid, s in strategies_out.items() if s["r0"]["pass"]],
            "r1_pass": [sid for sid, s in strategies_out.items() if s["r1"]["pass"]],
        },
    }
    return summary


def write_counterexamples(rows, contract, summary, out_dir):
    """One full group (all 4 conditions x 2 versions) per counterexample
    strategy: enough to show R0 passing and R1 failing on the same group."""
    out_files = []
    enum = contract["enumeration"]
    first_change = enum["change_groups"][0]
    idx = _index(rows)
    for sid in summary["main_reading"]["pass_r0_fail_r1"]:
        group_rows = [idx["g%02d|%s|v%d" % (first_change, c, v)]
                      for c in enum["conditions"] for v in enum["versions"]]
        evidence = {
            "strategy": sid,
            "reads": summary["strategies"][sid]["reads"],
            "rule": summary["strategies"][sid]["rule"],
            "r0_verdict": "PASS",
            "r1_failed_components": summary["strategies"][sid]["r1"]["failed_components"],
            "evidence_group": first_change,
            "scope_note": "one full group; the same behavior holds on every "
                          "change group (see rows.jsonl); R0 passes here while "
                          "R1 fails here",
            "rows": group_rows,
        }
        path = os.path.join(out_dir, "counterexamples", "%s.json" % sid)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(evidence, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        out_files.append(path)
    return out_files


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_contract(contract):
    enum = contract["enumeration"]
    problems = []
    if enum["group_count"] != 16:
        problems.append("group_count != 16")
    if enum["row_count"] != (enum["group_count"] * len(enum["conditions"])
                             * len(enum["versions"])):
        problems.append("row_count != groups x conditions x versions")
    if len(enum["change_groups"]) != 8:
        problems.append("change_groups != 8 groups")
    for v in enum["versions"]:
        if str(v) not in enum["order_marks"]:
            problems.append("order_marks missing version %r" % v)
    if len(contract["strategies"]) != 6:
        problems.append("strategy count != 6")
    r0 = contract["contracts"]["R0"]
    r1 = contract["contracts"]["R1"]
    for spec, expected in [
        (r0["change_relation_pairs"], 16),
        (r0["aa_bb_nochange_rows"], 64),
        (r1["mft_rows"], 128),
        (r1["joint_ab_ba_pairs"], 32),
        (r1["dir_relation_pairs"], 16),
        (r1["dir_change_rows"], 32),
        (r1["inv_pairs"], 64),
        (r1["aa_bb_nochange_rows"], 64),
    ]:
        if spec["denominator"] != expected:
            problems.append("denominator %r != %d" % (spec, expected))
    if problems:
        raise SystemExit("contract freeze inconsistencies:\n  - "
                         + "\n  - ".join(problems))


# ----------------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--prereg-commit", required=True,
                        help="full SHA of the commit that froze PREREG+contract")
    args = parser.parse_args(argv)

    if os.path.exists(args.out) and os.listdir(args.out):
        sys.stderr.write("refusing to overwrite non-empty results dir: %s\n"
                         % args.out)
        return 2

    wall_start = time.perf_counter()
    cpu_start = time.process_time()

    with open(args.contract, "r", encoding="utf-8") as fh:
        contract = json.load(fh)
    validate_contract(contract)

    rows = build_rows(contract)
    if len(rows) != contract["enumeration"]["row_count"]:
        raise SystemExit("enumeration produced %d rows, contract says %d"
                         % (len(rows), contract["enumeration"]["row_count"]))
    keys = [r["key"] for r in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("duplicate input keys in enumeration")

    run_strategies(rows, contract)

    per_strategy = {}
    for spec in contract["strategies"]:
        sid = spec["id"]
        per_strategy[sid] = {
            "r0": score_r0(rows, sid, contract),
            "r1": score_r1(rows, sid, contract),
        }
    oracle = per_strategy[ORACLE_ID]
    if not oracle["r1"]["pass"] or not oracle["r0"]["pass"]:
        sys.stderr.write("ORACLE failed its own contract: r0=%s r1 failed=%s\n"
                         % (oracle["r0"]["pass"], oracle["r1"]["failed_components"]))
        sys.stderr.write("this is an implementation bug, not a finding; "
                         "no results written\n")
        return 3

    summary = build_summary(rows, contract, per_strategy)

    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "counterexamples"), exist_ok=True)

    rows_path = os.path.join(args.out, "rows.jsonl")
    with open(rows_path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    summary_path = os.path.join(args.out, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    ce_files = write_counterexamples(rows, contract, summary, args.out)

    wall_end = time.perf_counter()
    cpu_end = time.process_time()

    verify_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "verify_static.py")
    manifest = {
        "task_id": contract["task_id"],
        "contract_version": contract["contract_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "prereg_commit": args.prereg_commit,
        "command": list(sys.argv),
        "inputs": {
            "contract": {"path": args.contract, "sha256": sha256_file(args.contract)},
            "run_py": {"path": os.path.abspath(__file__),
                       "sha256": sha256_file(os.path.abspath(__file__))},
            "verify_static_py": {"path": verify_path,
                                 "sha256": sha256_file(verify_path)
                                 if os.path.exists(verify_path) else None},
        },
        "environment": {
            "python": sys.version.replace("\n", " "),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "gpu": "none used; pure stdlib CPU run",
        },
        "counts": {
            "groups": contract["enumeration"]["group_count"],
            "rows": len(rows),
            "strategies": len(contract["strategies"]),
            "counterexample_files": ce_files,
        },
        "validation": {
            "keys_unique": True,
            "contract_row_count_match": True,
            "oracle_r0_pass": oracle["r0"]["pass"],
            "oracle_r1_pass": oracle["r1"]["pass"],
            "overwrite_refusal_active": True,
        },
        "main_reading": summary["main_reading"],
        "resources": {
            "wall_seconds": round(wall_end - wall_start, 6),
            "cpu_process_seconds": round(cpu_end - cpu_start, 6),
            "cpu_core_hours": round((cpu_end - cpu_start) / 3600.0, 9),
            "measurement_source": "time.perf_counter / time.process_time inside run.py",
            "new_training": 0,
            "gpu_hours": 0,
            "model_vlm_judge_api_calls": 0,
            "paid_services": 0,
            "downloads": 0,
            "assistant_token_cost": "UNKNOWN (not observable to the run)",
        },
        "outputs": {
            "rows_jsonl_sha256": sha256_file(rows_path),
            "summary_json_sha256": sha256_file(summary_path),
        },
    }
    manifest_path = os.path.join(args.out, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    print("wrote %d rows, %d strategy results to %s"
          % (len(rows), len(contract["strategies"]), args.out))
    print("main reading: %d/5 non-ORACLE strategies pass R0 but fail R1: %s"
          % (summary["main_reading"]["count"],
             ", ".join(summary["main_reading"]["pass_r0_fail_r1"]) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
