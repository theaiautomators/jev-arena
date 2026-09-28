"""Export ABCD-only evidence. Raw conversations, prompts, responses and private paths are excluded."""
import base64
import io
import json
import re
import zipfile
from pathlib import Path
from dotenv import dotenv_values
from arena.config import ROOT, digest, write_json
from scripts.analyze_abcd import FOLDER, RUN

def read(p): return json.loads(p.read_text(encoding="utf-8"))

def sanitize(value):
    if isinstance(value, dict):
        return {k:sanitize(v) for k,v in value.items() if k not in ("error_counts",)}
    if isinstance(value, list): return [sanitize(v) for v in value]
    return value

def main():
    summary = sanitize(read(ROOT/"docs/evidence/abcd-v1-summary.json"))
    summary["retrieval_diagnostic_status"] = "Legacy scenario-string diagnostic retained for provenance; superseded by retrieval_correction in this payload and docs/evidence/abcd-retrieval-correction.json. Do not use the legacy counts."
    supplement = read(ROOT/"docs/evidence/abcd-v1-supplement.json")
    assert summary["candidate_records"] == 12720
    assert supplement["frozen_source_and_journal_hashes_unchanged"]
    audit = None
    if (RUN/"audit/report.json").exists():
        a = read(RUN/"audit/report.json"); u = a["usage"]
        audit = {k:a[k] for k in ("selected_questions","judged_questions","answer_reviews","verdicts")}
        audit.update({"tokens":u["tokens"],"observed_models":u["observed_models"],
                      "successful_calls":sum(x["exit_code"] == 0 for x in u["attempts"]),
                      "failed_calls":sum(x["exit_code"] != 0 for x in u["attempts"]),
                      "flag_count":len(a["flags"]), "gold_changed":False, "human_audit":False})
    inspection = read(RUN/"audit/inspection.json") if (RUN/"audit/inspection.json").exists() else None
    closing = read(FOLDER/"closing-review.json") if (FOLDER/"closing-review.json").exists() else None
    ready = bool(inspection and closing and closing.get("resolved"))
    data = {"id":"abcd-test-v1","summary":summary,"supplement":supplement,"audit":audit,"retrieval_correction":sanitize(read(ROOT/"docs/evidence/abcd-retrieval-correction.json")),
            "review_status":"Measurements verified; automated audit and adversarial review complete. Human semantic audit not performed." if ready else "Measurements verified. Final automated audit and adversarial review still pending.",
            "inspection_status":inspection["summary"] if inspection else "Flagged cases still require inspection; primary reference labels remain unchanged."}
    template = (ROOT/"scripts/abcd_report_template.html").read_text(encoding="utf-8-sig")
    logo = base64.b64encode((ROOT/"apps/web/src/assets/taia-logo.webp").read_bytes()).decode()
    html = template.replace("__LOGO__","data:image/webp;base64,"+logo).replace("__DATA__",json.dumps(data,ensure_ascii=False).replace("<","\\u003c"))
    assert "__DATA__" not in html and "__LOGO__" not in html
    files = {"report.html":html.encode(),"report-data.json":json.dumps(data,ensure_ascii=False,indent=2).encode(),
             "README.txt":b"Open report.html for the offline ABCD dashboard. Read docs/ABCD-RESULTS.md and the review evidence before using claims. Source conversations, prompts, credentials and private logs are excluded. This is not published AST or live customer-resolution success. V2 evidence remains separate. Source repository: https://github.com/theaiautomators/jev-arena."}
    for name in ("ABCD-RESULTS.md","ABCD-PROTOCOL.md","VIDEO-SCRIPT.txt","VIDEO-SPINE.md",
                 "evidence/ABCD-AUDIT-REVIEW.md","evidence/ASTRA-ABCD-REVIEW.md","evidence/abcd-retrieval-correction.json"):
        path = ROOT/"docs"/name
        if path.exists(): files["docs/"+name] = path.read_bytes()
    files["docs/evidence/abcd-v1-summary.json"] = json.dumps(summary,indent=2).encode()
    files["docs/evidence/abcd-v1-supplement.json"] = json.dumps(supplement,indent=2).encode()
    files["docs/archive/full-v2-final/RESULTS.md"] = (ROOT/"docs/archive/full-v2-final/RESULTS.md").read_bytes()
    for notice in ("LICENSE","THIRD-PARTY-LICENSES.txt"):
        files[notice] = (ROOT/notice).read_bytes()
    files["ABCD-LICENSE.txt"] = (ROOT/"docs/licenses/ABCD-LICENSE.txt").read_bytes()
    frozen = read(FOLDER/"test-freeze.json")
    files["frozen-fingerprint.json"] = json.dumps(frozen["fingerprint"],indent=2).encode()
    # Only identifiers, reference/selected labels, status, timings, usage and hashes.
    cases = {json.loads(x)["id"]:json.loads(x) for x in (FOLDER/"test-cases.jsonl").read_text(encoding="utf-8").splitlines()}
    output = []
    for mid in frozen["order"]:
        path = RUN/"workers"/mid/"predictions.jsonl"
        assert digest(path.read_bytes()) == summary["verification"]["journal_sha256"][mid]
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line); p = r["prediction"]; c = cases[p["case_id"]]
            out = {k:p[k] for k in ("case_id","model_id","selected","status","input_tokens","request_ms","input_hash","raw_valid","normalized_rounding")}
            out.update({"reference":c["gold"],"cluster":c["cluster"],"pack":c["pack"],"task":c["family"],
                        "condition":c["provenance"]["condition"],"retrieval_ms":r["retrieval_ms"],"pipeline_ms":r["pipeline_ms"]})
            output.append(out)
    assert len(output) == len({(p["model_id"],p["case_id"]) for p in output}) == 12720
    files["predictions.jsonl"] = ("\n".join(json.dumps(r,ensure_ascii=False) for r in output)+"\n").encode()
    # Compare credential values in memory without printing any of them.
    secrets = [str(v).encode() for k,v in dotenv_values(ROOT/".env").items() if v and ("KEY" in k.upper() or "TOKEN" in k.upper())]
    for name, value in files.items():
        assert not any(s in value for s in secrets), "Credential in "+name
        assert not re.search(rb"apikey_[A-Za-z0-9_]{30,}",value), "Credential pattern in "+name
        assert not re.search(rb"[Cc]:[\\/]+[Uu]sers[\\/]+[Oo]wner",value), "Private path in "+name
    target = ROOT/".arena/reports"; target.mkdir(exist_ok=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as z:
        for name, value in files.items(): z.writestr(name,value)
    (target/"abcd-v1-report.html").write_bytes(html.encode())
    (target/"abcd-v1-report.zip").write_bytes(buffer.getvalue())
    verification = {"id":"abcd-test-v1","files_scanned":len(files),"credential_private_path_scan_passed":True,
                    "prediction_rows":len(output),"no_dialogue_or_policy_text":True,
                    "html_sha256":digest(html.encode()),"zip_sha256":digest(buffer.getvalue()),"final_review_complete":ready}
    write_json(ROOT/".arena/verification/abcd-export.json",verification)
    print(json.dumps(verification))

if __name__ == "__main__": main()
