"""Explicit preparation; no downloads or package installs happen during measured runs."""
import argparse
import json
import os
import shutil
import subprocess
from arena.config import ROOT,DATA,SOURCES,write_json,digest
from arena.registry import REGISTRY
from arena.prepare import prepare_model

def execute(args,progress):
    progress(' '.join(str(a) for a in args))
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    with (DATA/'setup.log').open('a',encoding='utf-8') as log:
        p=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
    if p.returncode:raise RuntimeError(f'{args[0]} failed ({p.returncode}); inspect .arena/setup.log')

def prepare(ids,progress=print,models=True,datasets=True,workers=True):
    from arena.source_fetch import fetch,REPOS
    from arena.importers import prepare_all
    unknown=set(ids)-set(REGISTRY)
    if unknown:raise ValueError('Unknown models: '+', '.join(unknown))
    if datasets or workers:
        for item in REPOS.items():progress(fetch(item))
    if datasets:
        progress('Preparing and freezing evaluation datasets…');prepare_all()
    if workers and any(not REGISTRY[m].hosted and m!='uniform' for m in ids):
        if not shutil.which('docker'):raise RuntimeError('Docker is required. Start Docker Desktop with NVIDIA GPU support.')
        context=ROOT
        if SOURCES!=ROOT/'.arena'/'sources':
            context=DATA/'build-context';context.mkdir(exist_ok=True)
            shutil.copytree(ROOT/'workers',context/'workers',dirs_exist_ok=True)
            shutil.copytree(SOURCES,context/'.arena'/'sources',dirs_exist_ok=True)
            shutil.copy2(ROOT/'.dockerignore',context/'.dockerignore')
        runtimes={REGISTRY[m].runtime for m in ids}
        if runtimes-{'winnow','clm','typesafe','uniform'}:execute(['docker','build','-f',str(context/'workers'/'Dockerfile'),'-t','jev-arena-worker:0.1',str(context)],progress)
        if 'clm' in runtimes:execute(['docker','build','-f',str(context/'workers'/'Dockerfile.clm'),'-t','jev-arena-clm:0.1',str(context)],progress)
        if 'winnow' in runtimes:
            # "native" compiles for the available GPU; override for cross compilation.
            arch=os.environ.get('ARENA_CUDA_ARCH','120')
            execute(['docker','build','--build-arg','CUDA_ARCH='+arch,'--build-arg','BUILD_JOBS=8','-t','jev-arena-winnow:0.1',str(SOURCES/'winnow')],progress)
            execute(['docker','build','-f',str(context/'workers'/'Dockerfile.winnow-bridge'),'-t','jev-arena-winnow-bridge:0.1',str(context)],progress)
    if models:
        for mid in ids:prepare_model(mid,progress)
    progress('Preparation complete. Run Smoke before the full comparison.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--models',nargs='+',default=['laya','plumb','decider']);p.add_argument('--skip-datasets',action='store_true');p.add_argument('--skip-workers',action='store_true');a=p.parse_args()
    prepare(a.models,datasets=not a.skip_datasets,workers=not a.skip_workers)
