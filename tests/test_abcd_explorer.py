import json

import pytest
from fastapi.testclient import TestClient

from arena import abcd_explorer as explorer
from arena.api import app


@pytest.fixture
def local_cases(tmp_path, monkeypatch):
    monkeypatch.setattr(explorer, "ABCD_DIR", tmp_path)
    explorer._snapshot.cache_clear()
    cases = [
        {"id": "full-route", "family": "route", "gold": "take_action",
         "state": "POLICY\nOBSERVED CONVERSATION SO FAR\ncustomer: Please help",
         "provenance": {"condition": "full_handbook", "conversation_id": 42, "checkpoint_index": 3}},
        {"id": "retrieved-action", "family": "action", "gold": "verify_identity",
         "state": "Saved shorter input", "provenance": {"condition": "retrieved_policy", "conversation_id": 42}},
        {"id": "synthetic", "family": "synthetic_action", "gold": "A",
         "state": "Controlled input", "provenance": {"condition": "controlled_stress"}},
    ]
    (tmp_path / "test-cases.jsonl").write_text("\n".join(json.dumps(c) for c in cases), encoding="utf-8")
    for model in explorer.MODELS:
        path = tmp_path / "runs/abcd-test-v1/workers" / model / "predictions.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"prediction": {"case_id": "full-route", "model_id": model,
            "status": "ok", "selected": "take_action", "input_tokens": 28, "request_ms": 15,
            "raw": {"private_transport": "DO_NOT_EXPOSE"}, "error": "PRIVATE_ERROR"}}), encoding="utf-8")
    yield cases
    explorer._snapshot.cache_clear()


def test_filtered_pagination_and_stress(local_cases):
    client = TestClient(app)
    assert client.get("/api/abcd/cases?conversation=42").json()["total"] == 2
    r = client.get("/api/abcd/cases?condition=retrieved_policy&task=action").json()
    assert [c["id"] for c in r["cases"]] == ["retrieved-action"]
    assert client.get("/api/abcd/cases?offset=1&limit=1").json()["cases"][0]["id"] == "retrieved-action"
    assert client.get("/api/abcd/cases?condition=controlled_stress").json()["total"] == 1
    assert "state" not in client.get("/api/abcd/cases").json()["cases"][0]


def test_exact_input_and_saved_answers_without_transport_payloads(local_cases):
    response = TestClient(app).get("/api/abcd/cases/full-route")
    d = response.json()
    assert d["case"] == local_cases[0]
    assert {p["model_id"] for p in d["predictions"]} == set(explorer.MODELS)
    assert all(p["selected"] == "take_action" for p in d["predictions"])
    assert "DO_NOT_EXPOSE" not in response.text and "PRIVATE_ERROR" not in response.text
    assert TestClient(app).get("/api/abcd/cases/missing").status_code == 404


@pytest.mark.parametrize("query", ["limit=1000", "offset=-1", "conversation=-1", "condition=bad", "task=bad"])
def test_query_boundaries(local_cases, query):
    assert TestClient(app).get("/api/abcd/cases?" + query).status_code == 422


def test_missing_local_data_is_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(explorer, "ABCD_DIR", tmp_path)
    response = TestClient(app).get("/api/abcd/cases")
    assert response.status_code == 404
    assert "not installed locally" in response.json()["detail"]
    assert str(tmp_path) not in response.text
