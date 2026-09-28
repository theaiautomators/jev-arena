"""Reproducible, outcome-independent sampling plus a separately labelled audit."""
from collections import defaultdict
from arena.config import digest


def stratified_ids(cases, count, seed=5090):
    buckets = defaultdict(list)
    for case in cases:
        buckets[(case.pack, case.family, case.question.kind, case.language)].append(case.id)
    for values in buckets.values():
        values.sort(key=lambda cid: digest([seed, cid]))
    # First balance within each pack, then across packs. A dataset with many
    # named families must not crowd classification or retrieval out of the audit.
    packs = defaultdict(list)
    for pack in sorted({key[0] for key in buckets}):
        keys = sorted(key for key in buckets if key[0] == pack)
        while any(buckets[key] for key in keys):
            for key in keys:
                if buckets[key]:
                    packs[pack].append(buckets[key].pop(0))
    chosen = []
    while len(chosen) < min(count, len(cases)):
        for pack in sorted(packs):
            if packs[pack] and len(chosen) < min(count, len(cases)):
                chosen.append(packs[pack].pop(0))
    return chosen


def disagreement_ids(cases, predictions, excluded, count, seed=5090):
    """Sample disagreements without looking at gold or preferring an entrant."""
    allowed = {c.id: set(c.question.labels) for c in cases}
    answers = defaultdict(set)
    for pred in predictions:
        if (pred['model_id'] != 'uniform' and pred['status'] in ('ok', 'invalid')
                and pred['selected'] in allowed.get(pred['case_id'], set())):
            answers[pred['case_id']].add(pred['selected'])
    candidates = [cid for cid, values in answers.items() if len(values) > 1 and cid not in excluded]
    return sorted(candidates, key=lambda cid: digest([seed, 'disagreement', cid]))[:count]
