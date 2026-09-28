from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class Question(BaseModel):
    id: str
    text: str
    kind: Literal["choice", "noul", "score"]
    labels: list[str] = Field(min_length=2)
    rubric: str = ""
    criteria: dict[str,str] | list[str] | None = None

class Case(BaseModel):
    id: str
    cluster: str
    pack: str
    family: str
    state: str
    question: Question
    gold: str
    acceptable: list[str] = Field(default_factory=list)
    reference_probs: dict[str, float] | None = None
    provenance: dict = Field(default_factory=dict)
    language: str = "en"
    split: str = "test"
    label_status: Literal["formal", "public", "teacher", "provisional", "audited"] = "formal"
    evidence: str = ""
    variant: str | None = None

    @model_validator(mode="after")
    def labels_valid(self):
        if len(set(self.question.labels)) != len(self.question.labels):
            raise ValueError("duplicate labels")
        if self.gold not in self.question.labels:
            raise ValueError("reference label outside options")
        return self

    def candidate(self) -> dict:
        # Explicit allow-list. Never serialize the Case into the worker request.
        return {"case_id": self.id, "state": self.state, "question": self.question.model_dump()}

class Prediction(BaseModel):
    case_id: str
    model_id: str
    status: Literal["ok", "invalid", "timeout", "transport_error", "unsupported", "cancelled"]
    selected: str | None = None
    probabilities: dict[str, float] | None = None
    probability_source: str = "unavailable"
    expected_score: float | None = None
    request_ms: float = 0
    queue_ms: float = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    attempt: int = 1
    error: str | None = None
    raw: dict = Field(default_factory=dict)
    input_hash: str = ""
    raw_valid: bool = True
    normalized_rounding: bool = False

class RunRequest(BaseModel):
    preset: Literal["smoke", "demo", "full"] = "full"
    model_ids: list[str] = Field(min_length=1, max_length=16)
    judge: bool = True
    judge_audit_cases: int = Field(default=60, ge=0, le=1000)
    judge_disagreement_cases: int = Field(default=0, ge=0, le=250)
    paid_cap_usd: float = Field(default=5, ge=0, le=100)
    seed: int = 5090
    idempotency_key: str = Field(min_length=8, max_length=128)

class EndpointConfig(BaseModel):
    # Local external servers are explicit alternatives to managed native workers.
    model_id: str
    url: str
    revision: str = Field(min_length=1)
    precision: str = "unknown"
