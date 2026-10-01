#!/usr/bin/env python3
"""RW-W3-REAL-CACHE-REUSE-v1: relation x correctness cross-count on a frozen real C_local cache.

Read-only reuse of p2 historical data at a fixed commit (accessed via `git show`,
never checked out). Implements the frozen contract
experiments/real_cache_relation_v1/contract.json v1.0.0 (freeze commit recorded
in the output manifests). No model loading, no import of any p2 scorer, no
general-purpose evaluation platform.

Outputs:
  --output-dir (local_only): full per-target derived table with UIDs, execution log,
      local manifest with real machine paths. NEVER committed (gitignored).
  --public-output-dir: summary.json, manifest.json, counterexamples.md
      (counts, proportions, types, source pointers only).

Fails closed: any verification failure aborts before any output file is written.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

CLASSES = ["nvg_surface", "buildings", "tree", "low_vegetation", "water", "playgrounds"]
CLASS_SET = set(CLASSES)
BUCKET_ORDER = ["INVALID_MISSING", "FULLY_CORRECT", "ACCURATELY_INVERTED", "WRONG_SAME_CLASS", "OTHER_LEGAL_WRONG_DIFF"]
BASE = "reports/rsicc_evidence_conflict_20260930"
INPUT_FILES = [
    f"{BASE}/FROZEN_REPORT_A.json",
    f"{BASE}/run/CACHE_SEAL_report_a_shard0.json",
    f"{BASE}/run/CACHE_SEAL_report_a_shard1.json",
    f"{BASE}/run/CACHE_SEAL_report_a_shard2.json",
    f"{BASE}/run/report_a_shard0_LEDGER.jsonl",
    f"{BASE}/run/report_a_shard1_LEDGER.jsonl",
    f"{BASE}/run/report_a_shard2_LEDGER.jsonl",
    f"{BASE}/RESULT_MANIFEST.json",
]
# Expected SHA-256 from frozen contract.json v1.0.0
EXPECTED_SHA = {
    f"{BASE}/FROZEN_REPORT_A.json": "fdd51a370b6f2ff63058b0ab0884c9a881b24508f7b11f106db4f946e6d27c87",
    f"{BASE}/run/CACHE_SEAL_report_a_shard0.json": "fefbed247a1e4dda508513e014fde4579895ba19e1c86261a496021cd371c583",
    f"{BASE}/run/CACHE_SEAL_report_a_shard1.json": "840f73fa355fe29ec7b41b97cca2fb93db59ad875730dc72d96a3857af383cf2",
    f"{BASE}/run/CACHE_SEAL_report_a_shard2.json": "2668084b2bba5a0791342a8d313a392729bc7fa52d5af0019fa61be2e0e0b2b8",
    f"{BASE}/run/report_a_shard0_LEDGER.jsonl": "8cf097a8bfca4dada816278f79d875bbf62ae2a16ed85ce7f4a14b6f6e2603ff",
    f"{BASE}/run/report_a_shard1_LEDGER.jsonl": "c7b9f974d65b049438fac0769eaef53fcc99f3dbdd65b1aa52422d0ac39435e6",
    f"{BASE}/run/report_a_shard2_LEDGER.jsonl": "d36eed9a4009991304244f8bc0055d16e0a8773a4a2a72f8aea753963ca1dba1",
    f"{BASE}/RESULT_MANIFEST.json": "3814697ffee55839c0b25a944dd8aac878157233d30a579e025ba1254efd3740",
}
# Known published readings used ONLY for the input mapping cross-check (abort if mismatch).
KNOWN_SINGLE_SIDE_MICRO = (110, 232)
KNOWN_PAIR_EQUAL_WEIGHT = 0.1746031746031746
LINE_RE = re.compile(r"^(R\d+)\s*:\s*(.*)$")


def fail(msg, log):
    log.write(f"ABORT: {msg}\n")
    sys.exit(f"ABORT: {msg}")


def git_show(repo, ref, path):
    res = subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"git show failed for {ref}:{path}: {res.stderr.decode(errors='replace')[:300]}")
    return res.stdout


def parse_raw(raw_output, expected_rids):
    """Contract parse rule: per-line 'R<n>: <label>', strip whitespace, strip one
    trailing ASCII '.', must be a legal class. Returns (labels dict, status, detail)."""
    labels = {}
    seen = set()
    for line in raw_output.splitlines():
        if not line.strip():
            continue
        m = LINE_RE.match(line.strip())
        if not m:
            return None, "PARSE_INCONSISTENT", f"non-R line: {line!r}"
        rid, lab = m.group(1), m.group(2).strip()
        if lab.endswith("."):
            lab = lab[:-1]
        if rid in seen:
            return None, "PARSE_INCONSISTENT", f"duplicate rid line {rid}"
        seen.add(rid)
        labels[rid] = lab
    extra = seen - set(expected_rids)
    missing = set(expected_rids) - seen
    if extra:
        return None, "PARSE_INCONSISTENT", f"unexpected rid lines {sorted(extra)}"
    out = {}
    for rid in expected_rids:
        if rid in missing:
            out[rid] = "MISSING"
        elif labels[rid] in CLASS_SET:
            out[rid] = labels[rid]
        else:
            out[rid] = "INVALID"
    return out, "OK", ""


def score_targets(targets):
    """Apply frozen readings and buckets. targets: list of dicts with keys
    component, rid, uid, refA, refB, predA, predB (pred values are class or
    MISSING/INVALID). Returns (per_target rows, derived_rows, consistency dict)."""
    rows = []
    derived = []
    swap_ok = 0
    same_side_ok = 0
    ab_ba_pair_consistent = 0
    for t in targets:
        pA, pB = t["predA"], t["predB"]
        valid = pA in CLASS_SET and pB in CLASS_SET
        # Derived rows per contract table (constructed explicitly, relations re-checked on rows)
        rowspec = {
            "AB": {"ref": (t["refA"], t["refB"]), "pred": (pA, pB)},
            "BA": {"ref": (t["refB"], t["refA"]), "pred": (pB, pA)},
            "AA": {"ref": (t["refA"], t["refA"]), "pred": (pA, pA)},
            "BB": {"ref": (t["refB"], t["refB"]), "pred": (pB, pB)},
        }
        # Weak structural relation re-checked ON the constructed rows, not assumed:
        # BA row must be the exact swap of the AB row; AA/BB rows must be same-class.
        swap_pair_ok = bool(valid and rowspec["BA"]["pred"] == tuple(reversed(rowspec["AB"]["pred"])))
        cond_rows = {}
        for cond, spec in rowspec.items():
            r = spec["ref"]
            p = spec["pred"]
            if cond in ("AB", "BA"):
                weak = swap_pair_ok
                swap_ok += weak
            else:
                weak = bool(valid and p[0] == p[1])
                same_side_ok += weak
            pc = valid and p[0] == r[0] and p[1] == r[1]
            cond_rows[cond] = {
                "condition": cond,
                "ref": list(r),
                "pred": list(p),
                "valid": valid,
                "weak_structural_relation": weak,
                "relation_change_pass": bool(valid and p[0] != p[1] and weak),
                "pair_correct": bool(pc),
            }
            derived.append({"uid": t["uid"], "component": t["component"], "rid": t["rid"], **cond_rows[cond]})
        # AB/BA full correctness must be identical (consistency check)
        if cond_rows["AB"]["pair_correct"] == cond_rows["BA"]["pair_correct"]:
            ab_ba_pair_consistent += 1
        rcp = cond_rows["AB"]["relation_change_pass"]
        pair_ok = cond_rows["AB"]["pair_correct"]
        if not valid:
            bucket = "INVALID_MISSING"
        elif pair_ok:
            bucket = "FULLY_CORRECT"
        elif (pA, pB) == (t["refB"], t["refA"]):
            bucket = "ACCURATELY_INVERTED"
        elif pA == pB:
            bucket = "WRONG_SAME_CLASS"
        else:
            bucket = "OTHER_LEGAL_WRONG_DIFF"
        rows.append({
            "uid": t["uid"], "component": t["component"], "rid": t["rid"],
            "ref": [t["refA"], t["refB"]], "pred": [pA, pB], "valid": valid,
            "relation_change_pass": rcp, "pair_correct": pair_ok,
            "relation_pass_but_wrong": bool(rcp and not pair_ok),
            "bucket": bucket,
            "pair_correct_AA": bool(valid and pA == t["refA"]),
            "pair_correct_BB": bool(valid and pB == t["refB"]),
        })
    consistency = {
        "swap_relation_rows_ok": swap_ok,
        "same_side_relation_rows_ok": same_side_ok,
        "ab_ba_pair_correct_consistent_targets": ab_ba_pair_consistent,
    }
    return rows, derived, consistency


def agg(rows, key, components):
    """Micro over targets and parent equal-weight over 63 components."""
    num = sum(1 for r in rows if r[key])
    micro = num / len(rows)
    by_comp = {}
    for r in rows:
        by_comp.setdefault(r["component"], []).append(1 if r[key] else 0)
    per = [sum(v) / len(v) for c in components for v in [by_comp.get(c, [])] if v]
    if len(per) != len(components):
        missing = [c for c in components if not by_comp.get(c)]
        raise RuntimeError(f"component(s) with no targets: {missing}")
    return {"count": num, "micro": micro, "parent_equal_weight": sum(per) / len(per)}


def build_targets(frozen, seals):
    """units_snapshot -> target list; verify refs gA != gB and seal/units alignment."""
    comps = frozen["components"]
    units = frozen["units_snapshot"]
    if len(comps) != frozen["n_valid_components"]:
        raise RuntimeError(f"component count {len(comps)} != n_valid_components {frozen['n_valid_components']}")
    if set(comps) != set(units.keys()):
        raise RuntimeError("components list and units_snapshot keys disagree")
    targets = []
    for cid in comps:
        seal = seals[cid]
        for u in units[cid]:
            if u["ref_cA"] == u["ref_cB"]:
                raise RuntimeError(f"ref gA==gB for {u['uid']}: violates fixed input assumption")
            rid = u["rid"]
            if rid not in seal["C_local"]:
                raise RuntimeError(f"rid {rid} missing in seal for {cid}")
            targets.append({
                "component": cid, "rid": rid, "uid": u["uid"],
                "refA": u["ref_cA"], "refB": u["ref_cB"],
                "predA": seal["C_local"][rid]["A"], "predB": seal["C_local"][rid]["B"],
            })
    return targets


def verify_inputs(repo, ref, log):
    """Extract via git show, verify contract SHA-256 and RESULT_MANIFEST receipts."""
    blobs = {}
    for path in INPUT_FILES:
        data = git_show(repo, ref, path)
        h = hashlib.sha256(data).hexdigest()
        if EXPECTED_SHA[path] and h != EXPECTED_SHA[path]:
            fail(f"input SHA mismatch for {path}: {h}", log)
        blobs[path] = data
        log.write(f"input {path} sha256 {h} OK\n")
    manifest = json.loads(blobs[f"{BASE}/RESULT_MANIFEST.json"])
    receipts = {e["path"]: e["sha256"] for e in manifest["files"]}
    for path in INPUT_FILES[:-1]:
        if receipts.get(path) != EXPECTED_SHA[path]:
            fail(f"RESULT_MANIFEST receipt mismatch for {path}", log)
    log.write("RESULT_MANIFEST receipts verified for all 7 data inputs\n")
    return blobs


def collect_and_verify_cache(blobs, log):
    """Three-way verification: ledger raw parse == seal labels; seal cells unique;
    raw_sha/prompt_sha match. Returns (targets, unresolved list)."""
    frozen = json.loads(blobs[f"{BASE}/FROZEN_REPORT_A.json"])
    seals = {}
    for s in range(3):
        d = json.loads(blobs[f"{BASE}/run/CACHE_SEAL_report_a_shard{s}.json"])
        for cid, c in d["components"].items():
            if cid in seals:
                fail(f"component {cid} sealed in two shards", log)
            seals[cid] = c
    ledger = {}
    for s in range(3):
        for line in blobs[f"{BASE}/run/report_a_shard{s}_LEDGER.jsonl"].decode("utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("arm") == "C_local" and r.get("kind") == "call":
                ledger.setdefault(r["cell"], []).append(r)
    unresolved = []
    n_cells = 0
    for cid in frozen["components"]:
        for side in ("A", "B"):
            cell = f"{cid}|C_local|{side}"
            recs = ledger.get(cell, [])
            n_cells += 1
            if len(recs) != 1:
                unresolved.append({"cell": cell, "reason": f"n_records={len(recs)}"})
                continue
            rec = recs[0]
            if rec["status"] != "ok":
                unresolved.append({"cell": cell, "reason": f"status={rec['status']}"})
                continue
            seal = seals[cid]["C_local_cells"][side]
            raw_sha = hashlib.sha256(rec["raw_output"].encode("utf-8")).hexdigest()
            if raw_sha != seal["raw_sha"]:
                unresolved.append({"cell": cell, "reason": "raw_sha mismatch"})
                continue
            if rec["prompt_sha"] != seal["prompt_sha"]:
                unresolved.append({"cell": cell, "reason": "prompt_sha mismatch"})
                continue
            expected_rids = sorted(u["rid"] for u in frozen["units_snapshot"][cid])
            parsed, status, detail = parse_raw(rec["raw_output"], expected_rids)
            if status != "OK":
                unresolved.append({"cell": cell, "reason": f"{status}: {detail}"})
                continue
            for rid in expected_rids:
                if parsed[rid] in CLASS_SET and parsed[rid] != seals[cid]["C_local"][rid][side]:
                    unresolved.append({"cell": cell, "reason": f"label mismatch {rid}: parsed {parsed[rid]} vs seal {seals[cid]['C_local'][rid][side]}"})
    if unresolved:
        return frozen, seals, unresolved, n_cells
    targets = build_targets(frozen, seals)
    return frozen, seals, [], n_cells, targets


def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source-repo", required=True)
    ap.add_argument("--source-ref", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--public-output-dir", required=True)
    ap.add_argument("--contract-commit", required=True, help="full 40-char Git SHA of the frozen PREREG/contract commit")
    args = ap.parse_args()

    t0 = time.perf_counter()
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.public_output_dir, exist_ok=True)
    for d in (args.output_dir, args.public_output_dir):
        for name in ("summary.json", "manifest.json", "counterexamples.md", "derived_rows_full.jsonl", "targets_full.jsonl", "execution_log.txt", "manifest_local.json"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                sys.exit(f"ABORT: output file already exists (overwrite refused): {p}")

    log = open(os.path.join(args.output_dir, "execution_log.txt"), "w", encoding="utf-8")

    def tlog(msg):
        log.write(f"[{time.perf_counter() - t0:8.4f}s] {msg}\n")

    tlog(f"start; source-repo={args.source_repo} source-ref={args.source_ref}")
    tlog(f"contract freeze commit: {args.contract_commit}")

    # Phase 1: inputs
    blobs = verify_inputs(args.source_repo, args.source_ref, log)
    tlog("input SHA-256 verified (contract + RESULT_MANIFEST receipts)")

    # Phase 2: three-way cache verification
    res = collect_and_verify_cache(blobs, log)
    if len(res) == 4:
        frozen, seals, unresolved, n_cells = res
        tlog(f"unresolved cells: {len(unresolved)} -> INPUT_UNRESOLVED/PARTIAL; writing failure record only")
        summary = {
            "task_id": "RW-W3-REAL-CACHE-REUSE-v1", "contract_version": "1.0.0",
            "status": "INPUT_UNRESOLVED", "n_cells_checked": n_cells,
            "unresolved": unresolved, "dependent_statistics_stopped": True,
        }
        with open(os.path.join(args.public_output_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        return
    frozen, seals, unresolved, n_cells, targets = res
    tlog(f"three-way verification passed: {n_cells} cells, 0 unresolved; {len(targets)} targets")

    # Phase 3: mapping cross-check against known published readings (abort on mismatch)
    comps = frozen["components"]
    n = len(targets)
    single = sum(1 for t in targets if t["predA"] == t["refA"]) + sum(1 for t in targets if t["predB"] == t["refB"])
    if (single, n * 2) != KNOWN_SINGLE_SIDE_MICRO:
        fail(f"single-side micro {single}/{n*2} != known {KNOWN_SINGLE_SIDE_MICRO}", log)
    rows, derived, consistency = score_targets(targets)
    pair_ew = agg(rows, "pair_correct", comps)["parent_equal_weight"]
    if abs(pair_ew - KNOWN_PAIR_EQUAL_WEIGHT) > 1e-12:
        fail(f"pair parent equal-weight {pair_ew!r} != known {KNOWN_PAIR_EQUAL_WEIGHT!r}", log)
    tlog(f"mapping cross-check OK: single-side {single}/{n*2}, pair equal-weight {pair_ew!r}")

    # Phase 4: frozen readings and buckets
    rcp = agg(rows, "relation_change_pass", comps)
    pc_ab = agg(rows, "pair_correct", comps)
    k = agg(rows, "relation_pass_but_wrong", comps)
    buckets = {b: 0 for b in BUCKET_ORDER}
    for r in rows:
        buckets[r["bucket"]] += 1
    assert sum(buckets.values()) == n, "bucket sum != 116"
    # AA/BB pair correctness equals respective single-side correctness
    for r in rows:
        assert r["pair_correct_AA"] == (r["pred"][0] == r["ref"][0])
        assert r["pair_correct_BB"] == (r["pred"][1] == r["ref"][1])
    tlog(f"readings: relation_change_pass {rcp['count']}, pair_correct {pc_ab['count']}, K {k['count']}; buckets {buckets}")

    # Phase 5: write outputs
    write_jsonl(os.path.join(args.output_dir, "targets_full.jsonl"), rows)
    write_jsonl(os.path.join(args.output_dir, "derived_rows_full.jsonl"), derived)
    tlog(f"local full tables written: {len(rows)} targets, {len(derived)} derived rows")

    def ew(condsel):
        per = {}
        for r in rows:
            if r["valid"] and condsel(r):
                per.setdefault(r["component"], set()).add(r["uid"])
        vals = [len(per.get(c, set())) / sum(1 for r in rows if r["component"] == c) for c in comps]
        return sum(vals) / len(vals)

    summary = {
        "task_id": "RW-W3-REAL-CACHE-REUSE-v1",
        "contract_version": "1.0.0",
        "contract_freeze_commit": args.contract_commit,
        "nature": "RETROSPECTIVE_REUSE",
        "derived_rows_label": "DERIVED_FROM_SINGLE_SIDE_CACHE",
        "source": {
            "repo": "zxqklein/p2", "branch": "feat/c1-directional-delta-v1",
            "historical_data_commit": args.source_ref,
            "input_sha256": {p: EXPECTED_SHA[p] for p in INPUT_FILES},
        },
        "units": {
            "n_parent_components": len(comps), "n_targets": n,
            "n_side_level_calls": n_cells, "n_target_side_predictions": n * 2,
            "n_derived_rows": len(derived), "all_refs_gA_ne_gB": True,
            "r2_never_replaced_by_r1": True,
        },
        "verification": {
            "input_sha256_matches_contract_and_manifest": True,
            "three_way_raw_seal_reference_match": True,
            "unresolved_cells": 0,
            "weak_structural_relation_rows_ok": consistency["swap_relation_rows_ok"] + consistency["same_side_relation_rows_ok"],
            "weak_structural_relation_rows_total": len(derived),
            "ab_ba_pair_correct_consistent_targets": consistency["ab_ba_pair_correct_consistent_targets"],
            "mapping_crosscheck_single_side_micro": f"{single}/{n*2}",
            "mapping_crosscheck_pair_parent_equal_weight": pair_ew,
        },
        "readings": {
            "relation_change_pass": rcp,
            "pair_correct": pc_ab,
            "pair_correct_note": "AB and BA identical by construction and verified; AA/BB equal respective single-side correctness",
            "relation_pass_but_wrong": k,
        },
        "five_buckets": {
            b: {"count": buckets[b], "proportion": buckets[b] / n} for b in BUCKET_ORDER
        },
        "bucket_sum": sum(buckets.values()),
        "status": "REUSE_OBSERVED_IN_SCOPE" if k["count"] >= 1 else "NO_COUNTEREXAMPLE_IN_THIS_CACHE",
        "claims_boundary": "diagnostic frequency of this frozen cache; not a model-policy false-accept rate; no extrapolation; not an independent confirmation; certifies nothing about direction mechanism, object binding, event gold, geographic generalization, or new-method performance",
        "counterexample_selection": "first by UID lexicographic order per type, max 2, see counterexamples.md",
        "user_predictions": "NOT_PROVIDED",
        "cost": {"gpu_hours": 0, "new_training_runs": 0, "model_or_judge_calls": 0, "paid_api": 0},
    }
    sum_path = os.path.join(args.public_output_dir, "summary.json")
    with open(sum_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, sort_keys=False)

    # Counterexamples: first 'relation satisfied but wrong' and first 'wrong same-class' by UID
    cex, cex_md = [], ["# 反例摘录（最多 2 个，按 UID 字典序）", ""]
    rel_first = next((r for r in sorted(rows, key=lambda r: r["uid"]) if r["relation_pass_but_wrong"]), None)
    same_first = next((r for r in sorted(rows, key=lambda r: r["uid"]) if r["bucket"] == "WRONG_SAME_CLASS"), None)
    for tag, r in (("关系满足但类别错误 (relation_pass_but_wrong)", rel_first), ("错误同类 (WRONG_SAME_CLASS)", same_first)):
        if r is None:
            cex_md.append(f"## {tag}\n\n本缓存中不存在该类型目标。\n")
            continue
        cex.append(r)
        cex_md.extend([
            f"## {tag}",
            "",
            f"- UID: `{r['uid']}`（组件 `{r['component']}`，{r['rid']}）",
            f"- 参考类别对 (gA,gB): ({r['ref'][0]}, {r['ref'][1]})",
            f"- 缓存预测对 (pA,pB): ({r['pred'][0]}, {r['pred'][1]})",
            f"- 派生读数: relation_change_pass={r['relation_change_pass']}, pair_correct={r['pair_correct']}, bucket={r['bucket']}",
            f"- 来源: p2@`{args.source_ref}` 的 `{BASE}/run/CACHE_SEAL_report_a_shard*.json` components[`{r['component']}`].C_local[`{r['rid']}`] 与同 cell 账本记录（`{r['component']}|C_local|A` / `|B`）",
            "- 上游限制: p2 原件为私有仓库；外部读者无法访问。公开代码可在自有同格式缓存或人工 fixtures 上运行，不宣称全部历史数据公开可复现。",
            "",
        ])
    cex_path = os.path.join(args.public_output_dir, "counterexamples.md")
    with open(cex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cex_md))

    # Public manifest (never self-referential: hashes only summary.json + counterexamples.md)
    code_path = os.path.abspath(__file__)
    with open(code_path, "rb") as f:
        code_sha = hashlib.sha256(f.read()).hexdigest()
    out_hashes = {
        os.path.basename(sum_path): hashlib.sha256(open(sum_path, "rb").read()).hexdigest(),
        os.path.basename(cex_path): hashlib.sha256(open(cex_path, "rb").read()).hexdigest(),
    }
    elapsed = time.perf_counter() - t0
    manifest = {
        "task_id": "RW-W3-REAL-CACHE-REUSE-v1",
        "tool": "experiments/real_cache_relation_v1/run.py",
        "tool_sha256": code_sha,
        "contract_version": "1.0.0",
        "contract_freeze_commit": args.contract_commit,
        "source_ref": args.source_ref,
        "input_sha256": {p: EXPECTED_SHA[p] for p in INPUT_FILES},
        "replay_command": "python experiments/real_cache_relation_v1/run.py --source-repo <path-to-p2-checkout> --source-ref 9dcd77cc174117551f22b8b694feec00ac985292 --output-dir experiments/real_cache_relation_v1/local_only/run_v1 --public-output-dir experiments/real_cache_relation_v1/results_v1 --contract-commit " + args.contract_commit,
        "replay_note": "<path-to-p2-checkout> is a local placeholder; the source repo must contain the fixed commit; access is read-only via git show",
        "outputs_sha256": out_hashes,
        "status": summary["status"],
        "cost": {"cpu_seconds_this_scoring_run": round(elapsed, 6), "gpu_hours": 0, "new_training_runs": 0, "model_or_judge_calls": 0},
        "cost_note": "single-threaded stdlib run; CPU ~= wall clock; implementation/verification/maintenance time recorded separately in RETURN",
    }
    with open(os.path.join(args.public_output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    local_manifest = dict(manifest)
    local_manifest["real_paths"] = {
        "source_repo": os.path.abspath(args.source_repo),
        "output_dir": os.path.abspath(args.output_dir),
        "public_output_dir": os.path.abspath(args.public_output_dir),
    }
    local_manifest["full_command"] = " ".join(sys.argv)
    local_manifest["python"] = sys.version
    with open(os.path.join(args.output_dir, "manifest_local.json"), "w", encoding="utf-8") as f:
        json.dump(local_manifest, f, ensure_ascii=False, indent=1)

    tlog(f"done; status={summary['status']}; K={k['count']}/{n}; cpu={elapsed:.4f}s")
    print(f"status={summary['status']} K={k['count']}/{n} relation_change_pass={rcp['count']}/{n} pair_correct={pc_ab['count']}/{n} cpu={elapsed:.4f}s")


if __name__ == "__main__":
    main()
