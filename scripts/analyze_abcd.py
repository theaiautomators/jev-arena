"""Independent ABCD verification and metrics; never modifies candidate evidence."""
from __future__ import annotations
import itertools
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from arena.config import DATA, ROOT, digest, write_json
from arena.contracts import Case

FOLDER = DATA / "abcd-v1"
RUN = FOLDER / "runs/abcd-test-v1"
CONDITIONS = ("full_handbook", "retrieved_policy")


def distribution(values):
    x = [float(v) for v in values if v is not None]
    return {"n": len(x), "min": min(x) if x else None,
            "p50": float(np.median(x)) if x else None,
            "p95": float(np.quantile(x, .95)) if x else None,
            "max": max(x) if x else None}


def interval(values, clusters, repeats=10000):
    """Resample whole conversations/bases; related variants stay together."""
    grouped = defaultdict(list)
    for value, cluster in zip(values, clusters): grouped[cluster].append(value)
    if not grouped: return None
    sums = np.array([sum(v) for _, v in sorted(grouped.items())])
    counts = np.array([len(v) for _, v in sorted(grouped.items())])
    rng = np.random.default_rng(15090)
    means = []
    for i in range(0, repeats, 100):
        idx = rng.integers(0, len(sums), size=(min(100, repeats-i), len(sums)))
        means.extend((sums[idx].sum(1) / counts[idx].sum(1)).tolist())
    return np.quantile(means, [.025, .975]).tolist()


def observation(case, row):
    p = row["prediction"]
    supported = p["status"] != "unsupported"
    return {"case_id": case.id, "cluster": case.cluster,
            "supported": supported, "strict": p["status"] == "ok" and p["selected"] == case.gold,
            "label": p.get("selected") == case.gold, "status": p["status"]}


def rates(obs):
    supported = [o for o in obs if o["supported"]]
    result = {"planned": len(obs), "supported": len(supported),
              "unsupported": len(obs)-len(supported),
              "status_counts": dict(Counter(o["status"] for o in obs))}
    for metric in ("strict", "label"):
        values = [int(o[metric]) for o in supported]
        result[metric+"_correct"] = sum(values)
        result[metric+"_accuracy_supported"] = sum(values)/len(values) if values else None
        result[metric+"_correct_yield_planned"] = sum(int(o[metric]) for o in obs)/len(obs) if obs else None
        result[metric+"_ci_supported"] = interval(values, [o["cluster"] for o in supported])
    return result


def classification(cases, rows):
    """All declared labels are in macro F1; unavailable capacity is separate."""
    labels = cases[0].question.labels if cases else []
    assert all(c.question.labels == labels for c in cases)
    supported = [c for c in cases if rows[c.id]["prediction"]["status"] != "unsupported"]
    out = {"labels": labels, "planned_support": dict(Counter(c.gold for c in cases)),
           "supported_support": dict(Counter(c.gold for c in supported))}
    for metric in ("strict", "label"):
        confusion = Counter()
        for c in supported:
            p = rows[c.id]["prediction"]
            predicted = p.get("selected")
            if predicted not in labels or (metric == "strict" and p["status"] != "ok"): predicted = "[invalid_or_failed]"
            confusion[c.gold, predicted] += 1
        per_label = []
        for label in labels:
            tp = confusion[label, label]
            fp = sum(n for (gold, pred), n in confusion.items() if pred == label and gold != label)
            fn = sum(n for (gold, pred), n in confusion.items() if gold == label and pred != label)
            per_label.append({"label": label, "support": tp+fn, "correct": tp,
                              "recall": tp/(tp+fn) if tp+fn else None,
                              "precision": tp/(tp+fp) if tp+fp else None,
                              "f1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.})
        out[metric] = {"macro_f1": float(np.mean([x["f1"] for x in per_label])) if supported else None,
                       "per_label": per_label,
                       "confusion": [{"gold": a, "predicted": b, "n": n} for (a,b),n in sorted(confusion.items())]}
    return out


def summarize(cases, rows, include_classes=True):
    result = rates([observation(c, rows[c.id]) for c in cases])
    predictions = [rows[c.id]["prediction"] for c in cases]
    attempted = [p for p in predictions if p["status"] != "unsupported"]
    result.update({"valid": sum(p["status"] == "ok" for p in predictions),
                   "usable_labels": sum(p.get("selected") in c.question.labels for c,p in zip(cases,predictions)),
                   "input_tokens_all": distribution(p.get("input_tokens") for p in predictions),
                   "input_tokens_unreported_status_counts": dict(Counter(p["status"] for p in predictions if p.get("input_tokens") is None)),
                   "input_tokens_supported": distribution(p.get("input_tokens") for p in attempted),
                   "request_ms_supported_including_invalid": distribution(p["request_ms"] for p in attempted),
                   "pipeline_ms_supported": distribution(rows[c.id]["pipeline_ms"] for c in cases if rows[c.id]["prediction"]["status"] != "unsupported"),
                   "retrieval_ms": distribution(rows[c.id]["retrieval_ms"] for c in cases),
                   "normalization_count": sum(p.get("normalized_rounding", False) for p in predictions),
                   "error_counts": dict(Counter(p.get("error") for p in predictions if p.get("error")))})
    if include_classes: result["classification"] = classification(cases, rows)
    return result


def combined(cases, rows, condition):
    subset = [c for c in cases if c.pack == "ABCD next action" and c.provenance["condition"] == condition]
    actions = {(c.cluster, c.provenance["checkpoint_index"]): c for c in subset if c.family == "action"}
    out = []
    for c in subset:
        if c.family != "route": continue
        o = observation(c, rows[c.id])
        if c.gold == "take_action":
            action = actions[c.cluster, c.provenance["checkpoint_index"]]
            a = observation(action, rows[action.id])
            o["supported"] = o["supported"] and a["supported"]
            o["strict"] = o["strict"] and a["strict"]
            o["label"] = o["label"] and a["label"]
            o["status"] = "unsupported" if not o["supported"] else ("ok" if o["status"] == a["status"] == "ok" else "invalid_or_failed")
        out.append(o)
    return out


def paired(a, b):
    assert len(a) == len(b)
    shared = [(x,y) for x,y in zip(a,b) if x["supported"] and y["supported"]]
    assert all(x["cluster"] == y["cluster"] for x,y in shared)
    out = {"shared_supported": len(shared), "direction": "b minus a"}
    for metric in ("strict", "label"):
        deltas = [int(y[metric])-int(x[metric]) for x,y in shared]
        out[metric] = {"a_correct": sum(x[metric] for x,y in shared),
                       "b_correct": sum(y[metric] for x,y in shared),
                       "difference": float(np.mean(deltas)) if deltas else None,
                       "ci": interval(deltas, [x["cluster"] for x,y in shared])}
    return out


def verify_inputs(frozen, cases):
    fp = frozen["fingerprint"]
    for key,name in (("test_cases","test-cases.jsonl"),("dev_cases","dev-cases.jsonl"),("policy_sections","policy-sections.json"),("source_manifest","source-manifest.json")):
        assert digest((FOLDER/name).read_bytes()) == fp[key], name
    for name, expected in fp["files"].items():
        assert digest((RUN/"source"/name).read_bytes()) == expected, name
    source = DATA/"research/abcd"
    manifest = json.loads((FOLDER/"source-manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items(): assert digest((source/name).read_bytes()) == expected, name
    from arena.abcd import read_sources, policy_sections, natural_cases
    data,guidelines,ontology = read_sources(source)
    sections = policy_sections(guidelines, ontology, json.loads((source/"kb.json").read_text(encoding="utf-8")))
    rebuilt,_ = natural_cases(data, sections, ontology)
    original = {c.id:c for c in cases if c.pack == "ABCD next action"}
    assert len(original) == len(rebuilt) == 2400
    assert all(c.model_dump() == original[c.id].model_dump() for c in rebuilt), "Rebuilt source alignment differs"
    assert len({c.cluster for c in rebuilt}) == 300
    assert all(c.split == "test" and not c.acceptable for c in cases)
    return {"source_files": len(manifest["files"]), "rebuilt_natural_cases": len(rebuilt), "conversations": 300}


def verify_token_accounting(prediction):
    tokens = prediction.get("input_tokens")
    if tokens is None:
        # A provider/network failure may return no usage. Preserve the failure,
        # report its unknown tokens and reservation; never invent a token count.
        assert prediction["status"] in ("transport_error", "timeout", "cancelled")
        assert prediction.get("selected") is None
        return False
    assert isinstance(tokens, int) and tokens > 0
    return True


def verify_rows(cases, rows, mid):
    lookup = {c.id:c for c in cases}
    assert len(rows) == len(lookup) == 2544
    ids = [r["prediction"]["case_id"] for r in rows]
    assert len(set(ids)) == len(ids) and set(ids) == set(lookup)
    for row in rows:
        p = row["prediction"]; c = lookup[p["case_id"]]
        assert p["model_id"] == mid and p["input_hash"] == digest(c.candidate())
        verify_token_accounting(p)
        assert row["retrieval_ms"] >= 0 and row["pipeline_ms"] >= 0
        if p["status"] == "ok":
            assert p["selected"] in c.question.labels and p["raw_valid"]
            probs = p.get("probabilities")
            if probs is not None:
                assert set(probs) == set(c.question.labels)
                assert all(math.isfinite(v) and 0 <= v <= 1 for v in probs.values())
                assert math.isclose(math.fsum(probs.values()),1,rel_tol=0,abs_tol=1e-4+1e-12)
        if p["status"] == "unsupported": assert p["selected"] is None
    return dict(zip(ids, rows))


def main():
    assert (RUN/"candidate-complete.json").exists(), "Candidate work is incomplete; no final analysis"
    frozen = json.loads((FOLDER/"test-freeze.json").read_text(encoding="utf-8"))
    cases = [Case.model_validate_json(x) for x in (FOLDER/"test-cases.jsonl").read_text(encoding="utf-8").splitlines()]
    verification = verify_inputs(frozen, cases)
    mids = frozen["order"]
    rows = {}; models = {}; timestamps = []; journal_hashes = {}
    groups = {(condition,task):[c for c in cases if c.pack == "ABCD next action" and c.family == task and c.provenance["condition"] == condition] for condition in CONDITIONS for task in ("route","action")}
    for (condition,task), group in groups.items(): assert len(group) == (900 if task == "route" else 300)
    for mid in mids:
        work = RUN/"workers"/mid
        raw = (work/"predictions.jsonl").read_bytes(); journal_hashes[mid] = digest(raw)
        parsed = [json.loads(x) for x in raw.decode("utf-8").splitlines()]
        rows[mid] = verify_rows(cases, parsed, mid)
        timestamps.extend(r["recorded"] for r in parsed)
        cleanup = json.loads((work/"cleanup.json").read_text(encoding="utf-8"))
        if mid != "jev": assert cleanup["container_stopped"] and cleanup["memory_within_baseline"]
        assert json.loads((work/"completed.json").read_text(encoding="utf-8"))["records"] == 2544
        result = {"natural": {}, "stress": {}, "cleanup": cleanup}
        for (condition,task),group in groups.items():
            entry = summarize(group, rows[mid])
            if condition == "retrieved_policy":
                hit = [c for c in group if c.provenance["source_intent_for_analysis_only"] in c.provenance["retrieved_sections"]]
                miss = [c for c in group if c not in hit]
                entry["retrieval_diagnostic"] = {"hit": summarize(hit,rows[mid]), "miss": summarize(miss,rows[mid])}
            result["natural"][condition+"/"+task] = entry
        result["combined"] = {condition:rates(combined(cases,rows[mid],condition)) for condition in CONDITIONS}
        for length in (4096,8192,16384,28672):
            for position in ("early","middle","late"):
                group = [c for c in cases if c.pack == "Controlled context stress" and c.provenance["target_state_tokens_qwen"] == length and c.provenance["evidence_position"] == position]
                assert len(group) == 12
                result["stress"][str(length)+"/"+position] = summarize(group,rows[mid])
        models[mid] = result
    comparisons = {}; common = {}; condition_effects = {}
    for (condition,task),group in groups.items():
        key = condition+"/"+task
        shared = [c for c in group if all(rows[m][c.id]["prediction"]["status"] != "unsupported" for m in mids)]
        common[key] = {"n":len(shared), "models":{m:summarize(shared,rows[m]) for m in mids}}
        comparisons[key] = {}
        for a,b in itertools.combinations(mids,2):
            comparisons[key][a+" -> "+b] = paired([observation(c,rows[a][c.id]) for c in group],[observation(c,rows[b][c.id]) for c in group])
    for mid in mids:
        condition_effects[mid] = {}
        for task in ("route","action"):
            key = lambda c:(c.cluster,c.provenance["checkpoint_index"])
            a = sorted(groups["full_handbook",task],key=key); b = sorted(groups["retrieved_policy",task],key=key)
            assert [key(c) for c in a] == [key(c) for c in b]
            condition_effects[mid][task] = paired([observation(c,rows[mid][c.id]) for c in a],[observation(c,rows[mid][c.id]) for c in b])
        condition_effects[mid]["combined"] = paired(combined(cases,rows[mid],"full_handbook"),combined(cases,rows[mid],"retrieved_policy"))
    from scripts.abcd_preflight import budget
    ledgers = {str(p.relative_to(FOLDER)):json.loads(p.read_text(encoding="utf-8")) for p in FOLDER.rglob("cost-ledger.json")}
    end = json.loads((RUN/"candidate-complete.json").read_text(encoding="utf-8"))
    summary = {"id":"abcd-test-v1", "analysis_at":time.time(), "candidate_records":len(mids)*len(cases),
               "verification":{**verification,"journal_sha256":journal_hashes}, "models":models,
               "all_profile_common_support":common, "pairwise":comparisons,
               "retrieved_minus_full":condition_effects,
               "runtime":{"freeze_to_candidate_complete_minutes":(end["at"]-frozen["created"])/60,
                          "first_prediction_to_candidate_complete_minutes":(end["at"]-min(timestamps))/60,
                          "scope":"Candidate window includes loading, warmups and any pauses; excludes development preflight, subsequent audit/review and earlier GPU wait."},
               "cost":{"abcd_actual_usd":sum(x["actual_usd"] for x in ledgers.values()),
                       "abcd_reserved_usd":sum(x["reserved_usd"] for x in ledgers.values()),
                       "combined":budget(), "ledgers":ledgers},
               "limitations":["Balanced observed-next-step adaptation, not published AST or natural route prevalence.","No human semantic audit or live support outcomes.","Native caches and different precision/runtime profiles affect serial latency.","Synthetic track has 12 bases and four answer templates; never pool it with natural accuracy.","Descriptive cluster-bootstrap intervals are not adjusted for multiple comparisons."]}
    write_json(RUN/"independent-analysis.json",summary)
    write_json(ROOT/"docs/evidence/abcd-v1-summary.json",summary)
    print(json.dumps({"verified":summary["candidate_records"],"models":mids,"cost":summary["cost"]["abcd_actual_usd"]}))


if __name__ == "__main__": main()
