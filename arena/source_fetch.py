"""Download reference source for inspection and pin its commit. Does not execute it."""
import concurrent.futures
import io
import json
import tarfile
import urllib.request
from pathlib import Path

from arena.config import SOURCES,ROOT as PROJECT
ROOT = SOURCES
REPOS = {
    "laya": "NandhaKishorM/laya", "jevk5": "allebee/jevk5", "decider": "Mapika/decider",
    "semif": "TheoLeeCJ/SemIf-OpenJev", "nimble": "bespokelabsai/nimble",
    "clm": "Contrastive-LM/CLM", "winnow": "EldanRing/winnow-inference",
    "jevbench": "fstandhartinger/jevbench",
}

def fetch(item):
    key, repo = item
    try:
        lock=json.loads((PROJECT/'sources.lock.json').read_text(encoding="utf-8"))
        ref=sha=lock[key]['revision']
        existing=ROOT/key/'arena-source.json'
        if existing.exists() and json.loads(existing.read_text(encoding="utf-8")).get('revision')==ref:return f'{key}: pinned source already present'
        raw = urllib.request.urlopen(f"https://codeload.github.com/{repo}/tar.gz/{ref}").read()
        target = ROOT / key
        target.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            for entry in tf.getmembers():
                parts = Path(entry.name).parts[1:]
                if not parts or not entry.isfile(): continue
                out = target.joinpath(*parts).resolve()
                if not out.is_relative_to(target.resolve()): raise ValueError("unsafe archive path")
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(tf.extractfile(entry).read())
        (target / "arena-source.json").write_text(json.dumps({"repo":repo,"revision":ref,"retrieved_sha":sha}, indent=2), encoding="utf-8")
        return f"{key}: {ref}"
    except Exception as e:
        raise RuntimeError(f'{key}: source preparation failed: {e}') from e

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch, REPOS.items()): print(result, flush=True)
