from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Entrant:
    id: str
    name: str
    family: str
    repo: str | None
    revision: str
    runtime: str
    size: str
    license: str
    hosted: bool = False
    diagnostic: bool = False
    max_options: int = 255
    context: int = 8192
    precision: str = "BF16"
    probability_source: str = "native"
    subfolder: str = ""

ENTRANTS = [
    Entrant("jev", "Jev 1.13", "TypeSafe", None, "jev-1.13.0", "typesafe", "Hosted", "Proprietary service", True, context=32000, precision="Service managed"),
    Entrant("plumb", "Plumb 4B", "JevK5", "crh225/plumb-4b", "55de037801a8a9b9de3db5c0e16cef86210c2186", "jevk5", "4B", "Apache-2.0", max_options=16),
    Entrant("decider", "Decider 4B · v2", "Mapika", "Mapika/decider-4b", "49564ddcfccafb6db563eb757c1d41e6c78dcb56", "decider", "4B", "See model card"),
    Entrant("winnow", "Winnow 12B", "EldanRing", "EldanRing/Winnow-12B", "b6ac22b0d51b69b18200acacb3fbdd98073fffe8", "winnow", "12B", "Gemma terms", precision="Q8_0", max_options=64),
    Entrant("semif", "SemIf 4B", "OpenJev", "Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a", "semif", "4B", "Apache-2.0 / MIT", max_options=16),
    Entrant("clm", "CLM 8B", "Contrastive LM", "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218", "clm", "8B", "Apache-2.0", context=2048),
    Entrant("nimble", "Nimble 9B", "Bespoke Labs", "bespokelabs/Bespoke-Nimble-9B", "bd792f44ec8e265be861bfcdf4e05967ffe0e858", "nimble", "9B", "Apache-2.0"),
    Entrant("laya", "Laya", "Convai Innovations", "convaiinnovations/laya", "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851", "laya", "421M", "Apache-2.0", precision="FP32 + BF16 autocast", context=8192),
    Entrant("laya-typed", "Laya · typed", "Convai Innovations", "convaiinnovations/laya", "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851", "laya", "421M", "Apache-2.0", diagnostic=True, precision="FP32 + BF16 autocast", subfolder="typed-decisions"),
    Entrant("laya-multi", "Laya · multilingual", "Convai Innovations", "convaiinnovations/laya", "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851", "laya", "322M", "Apache-2.0", diagnostic=True, precision="FP32 + BF16 autocast", subfolder="multilingual"),
    Entrant("qwen", "Qwen 3.5 · JSON", "Generative control", "Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a", "qwen", "4B", "Apache-2.0", diagnostic=True, probability_source="unavailable"),
    Entrant("nli", "ModernBERT · NLI", "Zero-shot control", "MoritzLaurer/ModernBERT-large-zeroshot-v2.0", "a51e07b524299e309dd2b88d48b0cfa2bd9ec598", "nli", "395M", "Apache-2.0", diagnostic=True, probability_source="transformed_nli", precision="FP32", context=8192),
    Entrant("uniform", "Uniform baseline", "Statistical control", None, "arena-v1", "uniform", "No weights", "MIT", diagnostic=True, precision="FP64"),
]
REGISTRY = {e.id: e for e in ENTRANTS}

def public_registry():
    return [asdict(e) for e in ENTRANTS]
