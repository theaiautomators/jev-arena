from __future__ import annotations
import argparse
import json
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download
from arena.config import MODELS, DATA, digest, write_json
from arena.registry import REGISTRY

MANAGED={"laya","jevk5","decider","nli","qwen","semif","nimble","clm","winnow"}

def model_info(model_id):
    path=MODELS/model_id/"arena-manifest.json"
    if not path.exists():return None
    return json.loads(path.read_text(encoding="utf-8"))

def prepare_model(model_id,progress=print):
    entrant=REGISTRY[model_id]
    if not entrant.repo:return {"ready":True,"revision":entrant.revision}
    info=model_info(model_id)
    if info and info.get("complete") and info.get("prepare_version")==3 and info.get('resolved_revision')==entrant.revision:return info
    if model_id=="semif":
        base=prepare_model("qwen",progress)
        info={**base,"id":"semif","runtime":"semif","weights_model":"qwen"}
        write_json(MODELS/model_id/"arena-manifest.json",info)
        return info
    api=HfApi()
    remote=api.model_info(entrant.repo,revision=entrant.revision,files_metadata=True)
    folder=MODELS/model_id/"weights"
    files=[f.rfilename for f in remote.siblings]
    if entrant.runtime=="laya":
        prefix=entrant.subfolder+"/" if entrant.subfolder else ""
        allow=[f for f in files if f.startswith(prefix) and (f[len(prefix):] in ("model.safetensors","rl_agent_config.json") or f[len(prefix):].startswith(("encoder/","tokenizer/")))]
    elif entrant.runtime=="winnow":allow=["gguf/Winnow-12B-Q8_0.gguf","README.md"]
    else:allow=[f for f in files if f.endswith((".json",".safetensors",".txt",".model",".tiktoken",".jinja")) and not any(s in f for s in ("onnx/","gguf/"))]
    size=sum(f.size or 0 for f in remote.siblings if f.rfilename in allow)
    import shutil
    if shutil.disk_usage(MODELS).free<size*1.2+5*2**30:raise RuntimeError("Insufficient disk space for safe model preparation")
    progress(f"Downloading {entrant.name}: {size/2**30:.2f} GiB, revision {remote.sha}")
    snapshot_download(entrant.repo,revision=remote.sha,local_dir=folder,allow_patterns=allow,max_workers=4)
    inventory=[]
    for file in allow:
        p=folder/file
        if not p.exists():raise RuntimeError(f"Missing weight artifact {file}")
        # Streaming hashes avoid reading multi-GB weights into RAM.
        import hashlib
        h=hashlib.sha256()
        with p.open("rb") as handle:
            for block in iter(lambda:handle.read(8*1024*1024),b""):h.update(block)
        inventory.append({"file":file,"bytes":p.stat().st_size,"sha256":h.hexdigest()})
    dependencies=[]
    if entrant.runtime=="nimble":
        contract=json.loads((folder/"schema_config.json").read_text(encoding="utf-8"))
        dep_remote=api.model_info(contract["model"],revision=contract["revision"])
        snapshot_download(contract["model"],revision=dep_remote.sha,local_dir=folder/"base",allow_patterns=["*.json","*.safetensors","*.txt","*.model","*.jinja"],max_workers=4)
        dependencies.append({"role":"base","repo":contract["model"],"revision":dep_remote.sha})
    if entrant.runtime=="clm":
        dep_remote=api.model_info("Contrastive-LM/CLM-v0.1-8B",revision='e939398d4556fcd9400c76fa8c5a513202f42b0a')
        snapshot_download("Contrastive-LM/CLM-v0.1-8B",revision=dep_remote.sha,local_dir=folder/"head",allow_patterns=["CLM_v0.1-8B.pt"],max_workers=2)
        dependencies.append({"role":"head","repo":"Contrastive-LM/CLM-v0.1-8B","revision":dep_remote.sha})
    for dep in dependencies:
        dep['files']=[]
        for p in sorted((folder/dep['role']).rglob('*')):
            if not p.is_file() or '.cache' in p.parts:continue
            import hashlib
            h=hashlib.sha256()
            with p.open('rb') as handle:
                for block in iter(lambda:handle.read(8*1024*1024),b''):h.update(block)
            dep['files'].append({'file':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
    info={"prepare_version":3,"id":model_id,"repo":entrant.repo,"requested_revision":entrant.revision,"resolved_revision":remote.sha,"files":inventory,"dependencies":dependencies,"complete":True,"license":entrant.license,"runtime":entrant.runtime}
    write_json(MODELS/model_id/"arena-manifest.json",info)
    progress(f"{entrant.name} prepared and hashed")
    return info

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("models",nargs="+",choices=list(REGISTRY));args=parser.parse_args()
    for mid in args.models:prepare_model(mid)
