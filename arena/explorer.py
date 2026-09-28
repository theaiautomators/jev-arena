"""Read-only views over saved evidence. Never re-score or rewrite a run."""
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from statistics import median
import numpy as np


def signature(path):
    path = Path(path)
    stat = path.stat()
    return str(path), stat.st_mtime_ns, stat.st_size


@lru_cache(maxsize=8)
def _cases(path, _mtime, _size):
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def saved_cases(folder):
    path = Path(folder) / "cases.jsonl"
    return _cases(*signature(path)) if path.exists() else []


def matches(case, prediction):
    return prediction.get("selected") in [case["gold"], *case.get("acceptable", [])]


def case_page(folder, store, rid, *, model=None, pack=None, family=None, kind=None,
              search="", outcome="", offset=0, limit=30, index_only=False):
    all_cases = saved_cases(folder)
    counts = Counter((c["pack"], c["family"]) for c in all_cases)
    facets = [{"pack": p, "family": f, "count": n} for (p, f), n in counts.items()]
    values = [c for c in all_cases if (not pack or c["pack"] == pack)
              and (not family or c["family"] == family)
              and (not kind or c["question"]["kind"] == kind)]
    if search:
        needle = search.casefold()
        values = [c for c in values if needle in " ".join(
            [c["id"], c["state"], c["question"]["text"], c["family"]]).casefold()]
    if outcome:
        predictions = {p["case_id"]: p for p in store.prediction_summaries(rid, model)}
        def keep(c):
            p = predictions.get(c["id"])
            if not p:
                return False
            if outcome == "correct":
                return p["status"] != "unsupported" and matches(c, p)
            if outcome == "wrong":
                return p["status"] in ("ok", "invalid") and not matches(c, p)
            if outcome == "failed":
                return p["status"] not in ("ok", "unsupported")
            return p["status"] == "unsupported"
        values = [c for c in values if keep(c)]
    subset = values[offset:offset + limit]
    if index_only:
        subset = [{k: c[k] for k in ("id", "pack", "family", "question", "label_status")}
                  | {"preview": c["state"][:140]} for c in subset]
    return {"total": len(values), "cases": subset, "facets": facets,
            "predictions": [] if index_only else store.predictions_for_cases(rid, [c["id"] for c in subset], model)}


def summarize(cases, predictions, model_ids):
    """Counts include errors; missing/unsupported rows are never correct answers."""
    by_model = {m: {} for m in model_ids}
    for p in predictions:
        if p["model_id"] in by_model:
            by_model[p["model_id"]][p["case_id"]] = p
    reference = [c for c in cases if c["label_status"] not in ("teacher", "provisional")]
    shared = {c["id"] for c in reference if all(
        c["id"] in by_model[m] and by_model[m][c["id"]]["status"] != "unsupported" for m in model_ids)}

    def counts(cohort, rows):
        attempted = [(c, rows[c["id"]]) for c in cohort
                     if c["id"] in rows and rows[c["id"]]["status"] != "unsupported"]
        times = sorted(p.get("request_ms", 0) for _, p in attempted)
        n = len(attempted)
        labels = sum(matches(c, p) for c, p in attempted)
        strict = sum(p["status"] == "ok" and matches(c, p) for c, p in attempted)
        return {"n": n, "planned": len(cohort), "label_correct": labels, "strict_correct": strict,
                "label_accuracy": labels / n if n else None, "strict_accuracy": strict / n if n else None,
                "invalid": sum(p["status"] == "invalid" for _, p in attempted),
                "failed": sum(p["status"] != "ok" for _, p in attempted),
                "unsupported": sum(rows.get(c["id"], {}).get("status") == "unsupported" for c in cohort),
                "missing": sum(c["id"] not in rows for c in cohort),
                "p50_ms": median(times) if times else None,
                "p95_ms": float(np.quantile(times, .95)) if times else None}

    groups = [("", "", cases)]
    for pack in dict.fromkeys(c["pack"] for c in cases):
        packed = [c for c in cases if c["pack"] == pack]
        groups.append((pack, "", packed))
        families = list(dict.fromkeys(c["family"] for c in packed))
        if len(families) > 1 or families[0] != pack:
            groups.extend((pack, f, [c for c in packed if c["family"] == f]) for f in families)
    output = []
    for pack, family, members in groups:
        refs = [c for c in members if c["label_status"] not in ("teacher", "provisional")]
        common = [c for c in refs if c["id"] in shared]
        teachers = [c for c in members if c["label_status"] == "teacher"]
        output.append({"key": pack + "::" + family, "pack": pack, "family": family,
                       "cases": len(members), "reference_n": len(refs), "shared_n": len(common),
                       "teacher_n": len(teachers), "models": {
                           m: {"shared": counts(common, rows), "supported": counts(refs, rows),
                               "teacher": counts(teachers, rows)} for m, rows in by_model.items()}})
    return {"groups": output, "models": model_ids, "shared_reference_n": len(shared)}


@lru_cache(maxsize=4)
def _analysis(case_sig, prediction_sig, model_ids):
    # Retain only the fields used by analysis, not large native transport payloads.
    with open(prediction_sig[0], encoding="utf-8") as stream:
        rows = [{k: p.get(k) for k in ("case_id", "model_id", "status", "selected", "request_ms")}
                for line in stream if line.strip() for p in [json.loads(line)]]
    return summarize(_cases(*case_sig), rows, model_ids)


def analysis(folder, store, rid, model_ids, complete=False):
    folder = Path(folder)
    if complete and (folder / "predictions.jsonl").exists():
        result = _analysis(signature(folder / "cases.jsonl"), signature(folder / "predictions.jsonl"), tuple(model_ids))
    else:
        result = summarize(saved_cases(folder), store.prediction_summaries(rid), model_ids)
    return {"run_id": rid, **result}
