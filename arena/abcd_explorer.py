"""Read-only browsing of the local, frozen ABCD assessment; no model calls."""
import json
from functools import lru_cache
from pathlib import Path
from arena.config import DATA

ABCD_DIR = DATA / "abcd-v1"
MODELS = ("jev", "winnow", "decider", "nimble", "qwen")


@lru_cache(maxsize=1)
def _snapshot(root: str, signature: tuple):
    folder = Path(root)
    cases = {c["id"]: c for c in (
        json.loads(line) for line in (folder / "test-cases.jsonl").read_text(encoding="utf-8").splitlines()
    )}
    predictions = {}
    for model in MODELS:
        path = folder / "runs/abcd-test-v1/workers" / model / "predictions.jsonl"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            p = json.loads(line)["prediction"]
            # Raw transport payloads/errors are unnecessary for browsing.
            safe = {k: p.get(k) for k in (
                "case_id", "model_id", "status", "selected", "probabilities",
                "input_tokens", "request_ms", "probability_source",
            )}
            predictions.setdefault(p["case_id"], []).append(safe)
    return cases, predictions


def snapshot():
    paths = [ABCD_DIR / "test-cases.jsonl"] + [
        ABCD_DIR / "runs/abcd-test-v1/workers" / m / "predictions.jsonl" for m in MODELS
    ]
    if not paths[0].is_file():
        raise FileNotFoundError("ABCD case data is not installed locally. Raw dataset text is not bundled with the public repository or portable report.")
    signature = tuple((p.stat().st_mtime_ns, p.stat().st_size) if p.is_file() else None for p in paths)
    return _snapshot(str(ABCD_DIR), signature)


def case_index(condition="", task="", conversation=None, offset=0, limit=50):
    cases, _ = snapshot()
    rows = []
    for c in cases.values():
        meta = c["provenance"]
        if condition and meta.get("condition") != condition:
            continue
        if task and c["family"] != task:
            continue
        if conversation is not None and meta.get("conversation_id") != conversation:
            continue
        rows.append({"id": c["id"], "family": c["family"], "condition": meta.get("condition"),
                     "conversation_id": meta.get("conversation_id"), "checkpoint": meta.get("checkpoint_index"),
                     "gold": c["gold"]})
    return {"total": len(rows), "cases": rows[offset:offset + limit], "experiment": "abcd-test-v1"}


def case_detail(case_id):
    cases, predictions = snapshot()
    if case_id not in cases:
        raise KeyError(case_id)
    c = cases[case_id]
    # Reference/provenance are explicitly separate from the candidate input.
    return {"case": c, "predictions": predictions.get(case_id, [])}
