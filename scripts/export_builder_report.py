"""Export the public Full v2 report; preserve original exports and measurements."""
import io
import json
import re
import zipfile
from pathlib import Path
from dotenv import dotenv_values
from arena.config import ROOT, RUNS, digest, write_json
from arena.report import public_report, standalone, license_notices
from scripts.report_contents import FULL_DOCS, public_documents, check_archive

RID = "20260927-205440-6350b9"
folder = RUNS / RID
out = ROOT / ".arena/public-reports"
out.mkdir(exist_ok=True)
read = lambda path: json.loads(path.read_text(encoding="utf-8"))
run, result = read(folder/"run.json"), read(folder/"results.json")
assert run["status"] == result["status"] == "complete"
payload = public_report(result, run)
payload["result"]["matched_basis"] = result.get("matched_basis")
payload["result"]["limitations"] = list(payload["result"]["limitations"]) + [
    "Report-time correction: Winnow's native limit is 64 choices. The frozen 255-choice declaration caused 500 BANKING77 HTTP 400s; these are not reasoning errors. Shared 4,635-reference scores are unaffected.",
    "Paired dashboard intervals use strict correctness and pair-specific supported cohorts, not all-entrant shared selected-label accuracy.",
    "879 answer reviews cover 250 pack-balanced and 50 outcome-selected questions; audit fractions do not estimate population error rates. Automated review is not human annotation.",
    "Jev main inputs: median 423 tokens, p95 1,756, maximum 4,297. No near-limit context-quality claim is supported.",
    "Follow-ups and report-time review are in the accompanying ZIP evidence. Frozen raw records are unchanged."
]
html = standalone(payload)
assert len(payload["result"]["entrants"]) == 13
assert payload["result"]["judge_summary"]["completed"] == 879
assert payload["result"]["judge_summary"]["cli_versions"] == ["codex-cli 0.157.1"]
assert payload["readiness"]["hardware"]["gpu"]["name"] == "NVIDIA GeForce RTX 5090"
for before, after in zip(result["entrants"], payload["result"]["entrants"]):
    assert before == after
files = public_documents(ROOT, FULL_DOCS)
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("results.json", json.dumps(payload, ensure_ascii=False))
    z.writestr("report.html", html)
    z.writestr("LICENSES.txt", license_notices())
    z.writestr("METHOD-NOTES.md", "Full v2 public report: shared selected-answer accuracy leads the dashboard; frozen strict scores and measurements are unchanged. ABCD is a separate panel, not part of the v2 total. Original source-snapshot.zip remains unchanged.\n\n" + (ROOT/"docs/RESULTS.md").read_text(encoding="utf-8"))
    for name, data in files.items():z.writestr(name, data)
    z.write(folder/"source-snapshot.zip", "source-snapshot.zip")
    # Prediction fields contain identifiers/numbers and allowed option labels; free-text raw/errors are private.
    rows = [json.loads(line) for line in (folder/"predictions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 99723 and len({(x["model_id"],x["case_id"]) for x in rows}) == 99723
    z.writestr("predictions.jsonl", "\n".join(json.dumps({k:v for k,v in x.items() if k not in ("raw","error")}, ensure_ascii=False) for x in rows))
    z.writestr("README.txt", "Open report.html for the offline dashboard. Start with docs/BUILDER-TAKEAWAYS.md. Read docs/RESULTS.md for full methods. ABCD has a separate report linked from the repository. The Astra review covers the underlying assessment; the report presentation is a later revision. Follow-up aggregate evidence is in docs/evidence/full-v2-supplement.json. Original dataset text, credentials and private logs are excluded. The source snapshot preserves the historical implementation, including the capability bug corrected after the run. Source repository: https://github.com/theaiautomators/jev-arena.")

secrets = [str(v).encode() for k,v in dotenv_values(ROOT/".env").items() if v and ("KEY" in k.upper() or "TOKEN" in k.upper())]
scanned = []
def inspect(data, name):
    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for member in z.namelist():
                if not member.endswith("/"):inspect(z.read(member),name+"/"+member)
        return
    scanned.append(name)
    assert not any(value in data for value in secrets), "Credential in " + name
    assert not re.search(rb"apikey_[A-Za-z0-9_]{30,}", data), "Credential pattern in " + name
    assert not re.search(rb"[Cc]:[\\/]+[Uu]sers[\\/]+[Oo]wner|[Cc]:\\\\[Uu]sers\\\\[Oo]wner",data), "Private path in " + name
check_archive(buffer.getvalue())
inspect(buffer.getvalue(),"arena-full-v2.zip")
(out/"arena-full-v2.html").write_bytes(html.encode())
(out/"arena-full-v2.zip").write_bytes(buffer.getvalue())
write_json(ROOT/".arena/verification/public-full-v2-export.json", {"run_id":RID,"files_scanned":len(scanned),"credential_and_private_path_scan_passed":True,"zip_sha256":digest(buffer.getvalue()),"html_sha256":digest(html.encode()),"frozen_metrics_unchanged":True,"review_note_included":True})
print(json.dumps({"exported":True,"files_scanned":len(scanned),"zip_bytes":len(buffer.getvalue()),"html_bytes":len(html.encode())}))
