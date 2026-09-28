"""Container-side comparison using the upstream HTTP Embedder and Engine."""
import json
import subprocess
import time
from pathlib import Path

import requests
from clm import Engine
from clm.embedder import Embedder
from wire import native_question, normalize_answer


def main():
    path = '/weights/model'
    command = ['vllm','serve',path,'--served-model-name','qwen3-8b','--runner','pooling',
               '--dtype','bfloat16','--max-model-len','2048','--gpu-memory-utilization','0.72',
               '--enforce-eager','--no-enable-prefix-caching',
               '--max-num-batched-tokens','8192',
               '--host','127.0.0.1','--port','8090']
    Path('/out/server-command.json').write_text(json.dumps(command))
    with open('/out/native-server.log','w') as log:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(240):
                if server.poll() is not None:
                    raise RuntimeError('Native CLM encoder server exited; inspect native-server.log')
                try:
                    if requests.get('http://127.0.0.1:8090/health',timeout=2).status_code == 200:
                        break
                except requests.RequestException:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError('Native encoder health deadline')
            engine = Engine(embedder=Embedder(url='http://127.0.0.1:8090/v1/embeddings',model='qwen3-8b',max_tokens=None,cache_size=0),
                            checkpoint=path+'/head/CLM_v0.1-8B.pt',device='cuda',action_cache=0)
            outputs=[]
            for case in json.loads(Path('/inputs/cases.json').read_text()):
                answer=engine.answer(case['state'],{'decision':native_question(case['question'])})
                outputs.append({'case_id':case['case_id'],**normalize_answer(answer['answers']['decision'],case['question'])})
            Path('/out/native-predictions.json').write_text(json.dumps(outputs))
            print(json.dumps({'native_predictions':len(outputs)}),flush=True)
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill();server.wait()


if __name__ == '__main__':
    main()
