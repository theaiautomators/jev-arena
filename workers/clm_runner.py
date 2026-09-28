"""Native CLM head with vLLM LAST pooling, networkless in-process worker."""
import contextlib
import json
import os
import sys
import time
import traceback

wire=sys.stdout;sys.stdout=sys.stderr
def send(value):wire.write(json.dumps(value)+"\n");wire.flush()

def main():
    import torch
    import numpy as np
    from vllm import LLM,PoolingParams
    from transformers import AutoTokenizer
    from clm import Engine
    from runner import native_question,normalize
    path='/weights/model';limit=int(os.environ.get('ARENA_CONTEXT','2048'))
    tok=AutoTokenizer.from_pretrained(path)
    start=time.perf_counter()
    encoder=LLM(model=path,runner='pooling',dtype='bfloat16',max_model_len=limit,gpu_memory_utilization=.72,enforce_eager=True,enable_prefix_caching=False,trust_remote_code=False)
    class Embedder:
        def embed(self,texts):
            ids=[tok.encode(t) for t in texts]
            if any(len(x)>limit for x in ids):raise ValueError('Context limit exceeded; truncation disabled')
            out=encoder.encode(texts,pooling_task='embed',pooling_params=PoolingParams(),use_tqdm=False)
            vectors=np.array([o.outputs.data.float().cpu().numpy() if hasattr(o.outputs.data,'cpu') else o.outputs.data for o in out],dtype=np.float32)
            vectors=vectors/(np.linalg.norm(vectors,axis=-1,keepdims=True)+1e-12)
            return vectors,sum(map(len,ids))
    engine=Engine(embedder=Embedder(),checkpoint=path+'/head/CLM_v0.1-8B.pt',device='cuda',action_cache=0)
    send({'ready':True,'runtime':'clm','load_ms':(time.perf_counter()-start)*1000,'device':'cuda','gpu':torch.cuda.get_device_name(),'cache_mode':'disabled','encoder':'vLLM pooling / LAST','parameter_dtype':'bfloat16'})
    for line in sys.stdin:
        try:
            x=json.loads(line)
            if x.get('command')=='stop':break
            start=time.perf_counter();q=x['question']
            raw=engine.answer(x['state'],{'decision':native_question(q)})
            result=normalize(raw['answers']['decision'],q)
            send({'status':'ok','probability_source':'native',**result,'input_tokens':raw['usage']['input_tokens'],'model_ms':(time.perf_counter()-start)*1000})
        except ValueError as e:send({'status':'unsupported' if 'limit exceeded' in str(e) else 'invalid','error':str(e)})
        except Exception as e:traceback.print_exc();send({'status':'transport_error','error':str(e)})
if __name__=='__main__':
    try:main()
    except Exception as e:traceback.print_exc();send({'ready':False,'error':str(e)});sys.exit(1)
