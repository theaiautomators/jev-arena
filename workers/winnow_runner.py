"""Stdio bridge to Winnow's native server inside the same networkless container."""
import json
import subprocess
import sys
import time
import urllib.request
import traceback
wire=sys.stdout
from runner import native_question,normalize
def send(value):wire.write(json.dumps(value)+"\n");wire.flush()

def main():
    start=time.perf_counter()
    proc=subprocess.Popen(['python3','/app/scripts/serve.py','--text-only','--model','/weights/model/gguf/Winnow-12B-Q8_0.gguf','--context','8192','--decision-parallel','4','--host','127.0.0.1','--port','8091'],stdout=sys.stderr,stderr=sys.stderr)
    try:
        for _ in range(600):
            if proc.poll() is not None:raise RuntimeError('Winnow server exited')
            try:
                with urllib.request.urlopen('http://127.0.0.1:8091/health',timeout=2) as r:
                    if r.status==200:break
            except Exception:time.sleep(1)
        else:raise TimeoutError('Winnow readiness deadline exceeded')
        send({'ready':True,'runtime':'winnow','load_ms':(time.perf_counter()-start)*1000,'device':'cuda','precision':'Q8_0','context':8192,'server':'native Winnow llama.cpp'})
        for line in sys.stdin:
            try:
                x=json.loads(line)
                if x.get('command')=='stop':break
                q=x['question'];body={'state':x['state'],'questions':{'decision':native_question(q)}}
                req=urllib.request.Request('http://127.0.0.1:8091/v1/systemone',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=120) as r:raw=json.load(r)
                send({'status':'ok','probability_source':'native',**normalize(raw['answers']['decision'],q),'input_tokens':raw.get('usage',{}).get('input_tokens')})
            except Exception as e:send({'status':'transport_error','error':str(e)})
    finally:
        proc.terminate()
        try:proc.wait(10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
if __name__=='__main__':
    try:main()
    except Exception as e:traceback.print_exc();send({'ready':False,'error':str(e)});sys.exit(1)
