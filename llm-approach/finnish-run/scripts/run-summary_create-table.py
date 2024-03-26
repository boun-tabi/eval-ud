from pathlib import Path
import os, json

def main():
    run_dirs = {
        'llm-approach/experiment_outputs/extra_experiment/poe_GPT-4-20231017004030': {
            'versions': ['v2.13'],
            'treebank': 'UD_English-EWT',
            'model': 'GPT-4',
            'dependency_included': False
        },
        'llm-approach/experiment_outputs/eventual_experiment/poe_Claude-2-100k-20231016083251': {
            'versions': ['v2.8', 'v2.11'],
            'treebank': 'UD_Turkish-BOUN',
            'model': 'Claude-2-100k',
            'dependency_included': False
        },
        'llm-approach/experiment_outputs/eventual_experiment/poe_Claude-instant-100k-20231016001050': {
            'versions': ['v2.8', 'v2.11'],
            'treebank': 'UD_Turkish-BOUN',
            'model': 'Claude-instant-100k',
            'dependency_included': False
        },
        'llm-approach/experiment_outputs/eventual_experiment/poe_GPT-3.5-Turbo-20231015223903': {
            'versions': ['v2.8', 'v2.11'],
            'treebank': 'UD_Turkish-BOUN',
            'model': 'GPT-3.5-Turbo',
            'dependency_included': False
        },
        'llm-approach/experiment_outputs/eventual_experiment/poe_GPT-4-20231015231246': {
            'versions': ['v2.8', 'v2.11'],
            'treebank': 'UD_Turkish-BOUN',
            'model': 'GPT-4',
            'dependency_included': False
        },
        'llm-approach/experiment_outputs/eventual_experiment/poe_GPT-4-2023-12-19_16-59-29': {
            'versions': ['v2.8', 'v2.11'],
            'treebank': 'UD_Turkish-BOUN',
            'model': 'GPT-4',
            'dependency_included': True
        },
        'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-2024-03-12_14-39-51': {
            'versions': ['v2.13'],
            'treebank': 'UD_Finnish-TDT',
            'model': 'GPT-4',
            'dependency_included': True
        },
    }

    script_dir = Path('llm-approach/finnish-run/scripts')
    # steps:
    # 1: clean_output.py
    clean_script_path = script_dir / 'clean_output.py'
    # 2: summarize_experiment-sequence_matching.py
    sequence_matching_script_path = script_dir / 'summarize_experiment-sequence_matching.py'
    # 3: compare-tokens.py
    compare_tokens_script_path = script_dir / 'compare-tokens.py'
    table = []
    for run_dir, run_info in run_dirs.items():
        run_dir = Path(run_dir)
        treebank = run_info['treebank']
        model = run_info['model']
        dependency_included = run_info['dependency_included']
        output_files = [f for f in run_dir.iterdir() if f.is_file() and f.suffix == '.json' and f.stem.endswith('output')]
        for output_file in output_files:
            # 1: clean_output.py
            os.system(f'python {clean_script_path} -o {output_file}')
            cleaned_output_path = run_dir / (output_file.stem + '-cleaned.json')
            # 2: summarize_experiment-sequence_matching.py
            os.system(f'python {sequence_matching_script_path} -r {run_dir} -t {cleaned_output_path}')
            summary_path = run_dir / (cleaned_output_path.stem + '-summary.json')
            with summary_path.open('r', encoding='utf-8') as f:
                summary = json.load(f)
            # 3: compare-tokens.py
            os.system(f'python {compare_tokens_script_path} -s {summary_path}')
            comparison_path = run_dir / (summary_path.stem + '-comparison.json')
            with comparison_path.open('r', encoding='utf-8') as f:
                comparison = json.load(f)
            table.append({
                'run_dir': str(run_dir),
                'treebank': treebank,
                'output_file': str(output_file.stem),
                'model': model,
                'dependency_included': dependency_included,
                'character-based': summary['average ratio'],
                'token-based': comparison['summary']['llm accuracy']['f1']
            })

    summary_path = script_dir / 'summary-table.json'
    with summary_path.open('w', encoding='utf-8') as f:
        json.dump(table, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()