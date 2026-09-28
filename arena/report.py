"""Allow-listed, portable report exports. No prompts, secrets or user paths."""
import json
import re
import base64
from arena.config import ROOT

def license_notices():
    return '\n\n'.join((ROOT/name).read_text(encoding='utf-8') for name in ('LICENSE','THIRD-PARTY-LICENSES.txt') if (ROOT/name).is_file())

def public_report(result, run, readiness=None):
    """Use recorded provenance, never the machine or login present at export time."""
    safe = {key: result[key] for key in (
        'run_id', 'status', 'kind', 'preset', 'case_count', 'matched_count',
        'entrants', 'comparisons', 'limitations', 'publication_ready',
        'performance', 'episodes',
    )}
    safe['status'] = run['status']
    safe['judge_jobs'] = []
    judge_metadata = []
    for job in result['judge_jobs']:
        data = job.get('data', {})
        grade = data.get('grade')
        if job['status'] != 'complete' or not grade:
            continue
        judge_metadata.append(data.get('metadata', {}))
        # Free-text evidence can quote third-party datasets; export grades only.
        safe['judge_jobs'].append({
            'job_id': job['job_id'], 'status': 'complete',
            'data': {
                'models': data.get('models', []),
                'item': {'case_id': data.get('item', {}).get('case_id', '')},
                'grade': {
                    **{key: grade[key] for key in ('verdict', 'needs_human_review') if key in grade},
                    'rationale': 'Full judge evidence remains in the original local run.',
                    'evidence': '',
                },
            },
        })
    manifest = run['manifest']
    recorded = manifest.get('hardware', {})
    gpu = recorded.get('gpu')
    hardware = {key: recorded[key] for key in ('platform', 'python', 'disk_free_gb') if key in recorded}
    hardware['gpu'] = {key: gpu[key] for key in (
        'name', 'memory_total_mb', 'memory_used_mb', 'temperature_c', 'power_w', 'driver',
    ) if key in gpu} if isinstance(gpu, dict) else None
    safe['manifest'] = {key: manifest[key] for key in (
        'version', 'created', 'case_sha256', 'case_count', 'order', 'fresh_labels',
        'protocol_sha256', 'implemented_profile_sha256', 'runtime_fingerprint',
        'judge', 'declared_option_cohort',
    ) if key in manifest}
    safe['manifest']['hardware'] = hardware
    safe['manifest']['entrants'] = manifest['entrants']
    requested = manifest.get('judge', {}).get('requested_model')
    versions = sorted({meta['cli'] for meta in judge_metadata if meta.get('cli')})
    observed = sorted({meta['observed_model'] for meta in judge_metadata if meta.get('observed_model')})
    safe['judge_summary'] = {
        'completed': sum(job['status'] == 'complete' for job in result['judge_jobs']),
        'requested_model': requested, 'observed_model': observed[0] if len(observed) == 1 else None,
        'observed_models': observed, 'cli_versions': versions, 'transport': 'Codex CLI',
    }
    public_run = {
        'id': run['id'], 'created': run['created'], 'status': run['status'], 'error': None,
        'request': {key: run['request'][key] for key in ('preset', 'model_ids', 'judge')},
        'manifest': safe['manifest'],
    }
    ready = {
        'models': manifest['entrants'], 'hardware': hardware, 'setup': {},
        'active_run': None, 'docker_ready': False,
        'judge': {
            'ready': False, 'requested_model': requested,
            'observed_model': safe['judge_summary']['observed_model'],
            'version': ', '.join(versions) if versions else None,
            'controls': manifest.get('judge', {}).get('controls'),
        },
        'suites': {
            'expected': result['case_count'], 'available': 0, 'packs': [],
            'fresh_status': 'Saved report: metrics and case identifiers are included; original input text remains in the source run.',
            'presets': [{'id': result['preset'], 'count': result['case_count'], 'ready': False}],
        },
    }
    return {'format': 'jev-arena-report-v1', 'run': public_run, 'result': safe, 'readiness': ready}

def standalone(payload):
    assets=ROOT/'dist'/'assets'
    js=list(assets.glob('index-*.js'));css=list(assets.glob('index-*.css'))
    if len(js)!=1 or len(css)!=1:raise ValueError('Build the frontend before exporting an HTML report')
    styles=css[0].read_text(encoding='utf-8')
    def font(match):
        name=match.group(1).split('/')[-1].strip('"\'')
        p=assets/name
        if not p.is_file() or p.suffix not in ('.woff', '.woff2'):return match.group(0)
        return 'url(data:font/'+p.suffix[1:]+';base64,'+base64.b64encode(p.read_bytes()).decode()+')'
    styles=re.sub(r'url\(([^)]+\.woff2?)\)',font,styles)
    data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    code=js[0].read_text(encoding='utf-8').replace('</script','<\\/script')
    notices=json.dumps(license_notices(),ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101010"><title>Jev Arena · The AI Automators · Saved report</title><style>'+styles+'</style><div id="root"></div><script type="application/json" id="arena-license-notices">'+notices+'</script><script>window.__ARENA_REPORT__='+data+';</script><script type="module">'+code+'</script></html>'
