from pathlib import Path
import os, json

run_dirs = [
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-2024-04-10_15-46-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Basque-BDT-2.11-2024-04-10_17-48-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_English-EWT-2.12-2024-04-10_18-10-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_English-EWT-2.13-2024-04-10_18-11-38',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Turkish-BOUN-2.8-2024-04-10_18-44-56',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Turkish-BOUN-2.11-2024-04-10_18-47-10',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Irish-IDT-2.7-2024-04-10_19-04-12',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Irish-IDT-2.8-2024-04-10_19-05-36',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Highland_Puebla_Nahuatl-ITML-2.13-2024-04-10_21-02-09',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Hindi-HDTB-2.9-2024-04-10_21-06-07',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Hindi-HDTB-2.10-2024-04-10_21-14-11'
]

pass_l = [
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-2024-04-10_15-46-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Basque-BDT-2.11-2024-04-10_17-48-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_English-EWT-2.12-2024-04-10_18-10-28',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_English-EWT-2.13-2024-04-10_18-11-38',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Turkish-BOUN-2.8-2024-04-10_18-44-56',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Turkish-BOUN-2.11-2024-04-10_18-47-10',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Irish-IDT-2.7-2024-04-10_19-04-12',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Irish-IDT-2.8-2024-04-10_19-05-36',
    'llm-approach/finnish-run/scripts/outputs/poe_GPT-4-UD_Highland_Puebla_Nahuatl-ITML-2.13-2024-04-10_21-02-09',
]

def main():
    script_dir = Path(__file__).parent
    summary_table_path = script_dir / 'summary-table.json'
    # steps:
    # 1: clean_output.py
    clean_script_path = script_dir / 'clean_output.py'
    # 2: summarize_experiment-sequence_matching.py
    sequence_matching_script_path = script_dir / 'summarize_experiment-sequence_matching.py'
    # 3: compare-tokens.py
    compare_tokens_script_path = script_dir / 'compare-tokens.py'
    table = []
    for run_dir_str in run_dirs:
        run_dir = Path(run_dir_str)
        md_file = run_dir / 'md.json'
        with md_file.open('r', encoding='utf-8') as f:
            run_info = json.load(f)
        treebank = run_info['treebank']
        model = run_info['model'].replace('poe_', '')
        version = run_info['version']
        dependency_included = run_info['dependency_included']
        output_file = [f for f in run_dir.iterdir() if f.is_file() and f.suffix == '.json' and f.stem.endswith('output')][0]
        # 1: clean_output.py
        if run_dir_str not in pass_l:
            os.system(f'python {clean_script_path} -o {output_file}')
        cleaned_output_path = run_dir / (output_file.stem + '-cleaned.json')
        # 2: summarize_experiment-sequence_matching.py
        if run_dir_str not in pass_l:
            os.system(f'python {sequence_matching_script_path} -r {run_dir} -t {cleaned_output_path}')
        summary_path = run_dir / (cleaned_output_path.stem + '-summary.json')
        with summary_path.open('r', encoding='utf-8') as f:
            summary = json.load(f)
        sentence_count = summary['sentence_count']
        # 3: compare-tokens.py
        if run_dir_str not in pass_l:
            os.system(f'python {compare_tokens_script_path} -s {summary_path}')
        comparison_path = run_dir / (summary_path.stem + '-comparison.json')
        with comparison_path.open('r', encoding='utf-8') as f:
            comparison = json.load(f)
        table.append({
            'run_dir': str(run_dir),
            'treebank': treebank,
            'output_file': str(output_file.stem),
            'version': version,
            'model': model,
            'dependency_included': dependency_included,
            'character-based': summary['average ratio'],
            'token-based': comparison['summary']['llm accuracy']['f1'],
            'sentence_count': sentence_count
        })
        print(f'{treebank} {model} {dependency_included} {output_file.stem} done')

        with summary_table_path.open('w', encoding='utf-8') as f:
            json.dump(table, f, indent=4, ensure_ascii=False)
    else:
        with summary_table_path.open('r', encoding='utf-8') as f:
            table = json.load(f)

    markdown_summary_path = script_dir / 'summary-table.md'
    table.sort(key=lambda x: (x['treebank'], x['model'], x['dependency_included'], x['output_file']))
    markdown_str = '| Treebank | Version | Model | Character-based | Token-based | Dependency-included | Sentence count |\n'
    markdown_str += '| --- | --- | --- | --- | --- | --- | --- |\n'
    for row in table:
        character_accuracy, token_accuracy = '%.1f' % (row['character-based'] * 100) + '%', '%.1f' % (row['token-based'] * 100) + '%'
        dep_included = 'Yes' if row['dependency_included'] else 'No'
        output_file = row['output_file']
        version = row['version']
        markdown_str += f"| {row['treebank']} | {version} | {row['model']} | {character_accuracy} | {token_accuracy} | {dep_included} | {row['sentence_count']} |\n"
    with markdown_summary_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()