from pathlib import Path
import os, json, argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--calculate', action='store_true', help='Calculate the character-based and token-based accuracies')
    return parser.parse_args()

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
    'llm-approach/llama/scripts/outputs/poe_Claude-3-Opus-200k-2024-03-05_23-13-44': {
        'versions': ['v2.8', 'v2.11'],
        'treebank': 'UD_Turkish-BOUN',
        'model': 'Claude-3-Opus-200k',
        'dependency_included': False
    },
    'llm-approach/llama/scripts/outputs/poe_Mistral-Large-2024-02-27_10-13-02': {
        'versions': ['v2.8', 'v2.11'],
        'treebank': 'UD_Turkish-BOUN',
        'model': 'Misral-Large',
        'dependency_included': False
    },
    'llm-approach/llama/scripts/outputs/poe_Mixtral-8x7B-Chat-2024-01-27_23-54-52': {
        'versions': ['v2.8', 'v2.11'],
        'treebank': 'UD_Turkish-BOUN',
        'model': 'Mixtral-8x7B-Chat',
        'dependency_included': False
    },
    'llm-approach/llama/scripts/outputs/poe_Llama-2-70b-2024-01-24_22-25-12': {
        'versions': ['v2.8', 'v2.11'],
        'treebank': 'UD_Turkish-BOUN',
        'model': 'Llama-2-70b',
        'dependency_included': False
    },
    'llm-approach/llama/scripts/outputs/poe_Mistral-Medium-2024-01-29_14-39-24': {
        'versions': ['v2.8', 'v2.11'],
        'treebank': 'UD_Turkish-BOUN',
        'model': 'Misral-Medium',
        'dependency_included': False
    }
}

def main():
    args = get_args()
    script_dir = Path(__file__).parent
    summary_path = script_dir / 'summary-table.json'
    if args.calculate:
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

        with summary_path.open('w', encoding='utf-8') as f:
            json.dump(table, f, indent=4, ensure_ascii=False)
    else:
        with summary_path.open('r', encoding='utf-8') as f:
            table = json.load(f)

    markdown_summary_path = script_dir / 'summary-table.md'
    table.sort(key=lambda x: (x['treebank'], x['model'], x['dependency_included'], x['output_file']))
    markdown_str = '| Treebank | Version | Model | Character-based | Token-based | Dependency-included |\n'
    markdown_str += '| --- | --- | --- | --- | --- | --- |\n'
    for row in table:
        character_accuracy, token_accuracy = '%.1f' % (row['character-based'] * 100) + '%', '%.1f' % (row['token-based'] * 100) + '%'
        dep_included = 'Yes' if row['dependency_included'] else 'No'
        output_file = row['output_file']
        version = 'v2.13' if 'tb_output' in output_file else 'v2.11' if 'v2.11' in output_file else 'v2.8'
        markdown_str += f"| {row['treebank']} | {version} | {row['model']} | {character_accuracy} | {token_accuracy} | {dep_included} |\n"
    with markdown_summary_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()