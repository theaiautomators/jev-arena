"""Publish compact measured summaries, without prompts, local paths or credentials."""
import argparse
from collections import Counter
from pathlib import Path

from arena.config import write_json
from arena.controller import Controller
from scripts.evidence_summary import summarize_run


def public_evidence(run_id):
    summary = summarize_run(run_id)
    controller = Controller()
    result = controller.results(run_id, True)
    summary['summary_scope'] = 'Measured configuration results; not a universal ranking or a human semantic audit.'
    summary['matched_case_count'] = result['matched_count']
    summary['matched_reference_count'] = result['entrants'][0]['matched']['verified_count']
    for model in summary['models']:
        # Aggregate task counts are enough for this small public evidence ledger.
        for scope in ('metrics', 'matched'):
            model[scope].pop('confusion', None)
        model['performance'] = [
            {key: value for key, value in block.items() if key not in ('telemetry', 'predictions')}
            for block in result['performance'].get(model['id'], {}).get('blocks', [])
        ]
        for group, values in model['episodes'].items():
            task, mode = group.split('/')
            episodes = [episode for episode in result['episodes']
                        if episode['model_id'] == model['id'] and episode['task'] == task and episode['mode'] == mode]
            traces = [step for episode in episodes for step in episode.get('trace', [])]
            values['steps'] = sum(episode['steps'] for episode in episodes)
            if task == 'tickets':
                values['correct_steps'] = sum(bool(step['correct']) for step in traces)
                values['unrestricted_steps'] = sum(not step['restricted'] for step in traces)
                values['unnecessary_review'] = sum(not step['restricted'] and step['answer'] == 'Review' for step in traces)
            values['selected_actions'] = dict(Counter(str(step.get('answer')) for step in traces))
    metadata = [job['data'].get('metadata', {}) for job in result['judge_jobs'] if job['status'] == 'complete']
    summary['judge'] = {
        'requested_model': result['manifest']['judge']['requested_model'],
        'observed_models': sorted({meta['observed_model'] for meta in metadata if meta.get('observed_model')}),
        'cli_versions': sorted({meta['cli'] for meta in metadata if meta.get('cli')}),
        'verdict_counts': dict(Counter(job['data']['grade']['verdict'] for job in result['judge_jobs'] if job['status'] == 'complete')),
    }
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    write_json(args.output, public_evidence(args.run_id))
    print(f'Public aggregate evidence saved: {args.output}')
