from pathlib import Path
import os, json, argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--calculate', action='store_true', help='Calculate the character-based and token-based accuracies')
    return parser.parse_args()

run_dirs = {
    'llm-approach/manual-reconstruction/token-based-task/scripts/outputs/poe_GPT-4-2024-02-25_22-36-32': {
        'versions': ['v2.8', 'v2.11'],
        'model': 'GPT-4',
        'dependency_included': True
    },
    'llm-approach/manual-reconstruction/token-based-task/scripts/outputs/poe_GPT-4-2024-02-25_22-41-49': {
        'versions': ['v2.8', 'v2.11'],
        'model': 'GPT-4',
        'dependency_included': False
    }
}

def main():
    args = get_args()
    script_dir = Path(__file__).parent
    finnish_script_dir = Path('llm-approach/finnish-run/scripts')
    summary_path = script_dir / 'summary-table.json'
    if args.calculate:
        # steps:
        # 1: clean_output.py
        clean_script_path = finnish_script_dir / 'clean_output.py'
        # 2: compare-tokens.py
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
                # 2: compare-tokens.py
                os.system(f'python {compare_tokens_script_path} -o {cleaned_output_path}')
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