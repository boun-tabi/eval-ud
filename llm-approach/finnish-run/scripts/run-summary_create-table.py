from pathlib import Path
import os, json, argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--calculate', action='store_true')
    parser.add_argument('-cd', '--calculate-dir', type=str)
    parser.add_argument('-o', '--output-dir', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    output_dir = Path(args.output_dir)
    run_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
    # if args.calculate_dir:
    #     run_dirs = [d for d in run_dirs if str(d).endswith(args.calculate_dir)]
    script_dir = Path(__file__).parent
    summary_table_path = output_dir / 'summary-table.json'
    if args.calculate:
        # steps:
        # 1: clean_output.py
        clean_script_path = script_dir / 'clean_output.py'
        # 2: summarize_experiment-sequence_matching.py
        sequence_matching_script_path = script_dir / 'summarize_experiment-sequence_matching.py'
        # 3: compare-tokens.py
        compare_tokens_script_path = script_dir / 'compare-tokens.py'
        table = []
        for run_dir in run_dirs:
            md_file = run_dir / 'md.json'
            with md_file.open('r', encoding='utf-8') as f:
                run_info = json.load(f)
            date = run_info['now'].split('_')[0]
            treebank = run_info['treebank']
            model = run_info['model']
            for model_name_t in ['poe', 'trendyol']:
                model = model.replace(f'{model_name_t}_', '')
            version = run_info['version']
            dependency_included = run_info['dependency_included']
            if 'special_tr' in run_info:
                special_tr = run_info['special_tr']
            else:
                special_tr = False
            output_file = [f for f in run_dir.iterdir() if f.is_file() and f.suffix == '.json' and f.stem.endswith('output')][0]
            # 1: clean_output.py
            os.system(f'python {clean_script_path} -o {output_file}')
            cleaned_output_path = run_dir / (output_file.stem + '-cleaned.json')
            # 2: summarize_experiment-sequence_matching.py
            os.system(f'python {sequence_matching_script_path} -r {run_dir} -t {cleaned_output_path}')
            summary_path = run_dir / (cleaned_output_path.stem + '-summary.json')
            with summary_path.open('r', encoding='utf-8') as f:
                summary = json.load(f)
            sentence_count = summary['sentence_count']
            # 3: compare-tokens.py
            os.system(f'python {compare_tokens_script_path} -s {summary_path}')
            comparison_path = run_dir / (summary_path.stem + '-comparison.json')
            with comparison_path.open('r', encoding='utf-8') as f:
                comparison = json.load(f)
            table.append({
                'run_dir': str(run_dir),
                'treebank': treebank,
                'version': version,
                'model': model,
                'dependency_included': dependency_included,
                'character-based': summary['average ratio'],
                'token-based': comparison['summary']['llm accuracy'],
                'sentence_count': sentence_count,
                'date': date,
                'special_tr': special_tr
            })
            print(f'{treebank} {model} {dependency_included} done')
            print(f'character-based: {summary["average ratio"]}, token-based: {comparison["summary"]["llm accuracy"]}')
            print('-----------------------------------')

            with summary_table_path.open('w', encoding='utf-8') as f:
                json.dump(table, f, indent=4, ensure_ascii=False)
    else:
        with summary_table_path.open('r', encoding='utf-8') as f:
            table = json.load(f)
    
    run_d = {}
    for row in table:
        treebank, version, character_accuracy, token_accuracy = row['treebank'], row['version'], row['character-based'], row['token-based']
        if treebank not in run_d:
            run_d[treebank] = {}
        if version not in run_d[treebank]:
            run_d[treebank][version] = {
                'character-based': character_accuracy,
                'token-based': token_accuracy,
            }

    for treebank in run_d:
        versions = run_d[treebank]
        if len(versions) < 2:
            continue
        max_character_accuracy, max_character_version, max_token_accuracy, max_token_version = None, None, None, None
        for version in versions:
            character_accuracy = run_d[treebank][version]['character-based']
            if max_character_accuracy is None or character_accuracy > max_character_accuracy:
                max_character_accuracy = character_accuracy
                max_character_version = version
            token_accuracy = run_d[treebank][version]['token-based']
            if max_token_accuracy is None or token_accuracy > max_token_accuracy:
                max_token_accuracy = token_accuracy
                max_token_version = version
        run_d[treebank][max_character_version]['max_character'] = True
        run_d[treebank][max_token_version]['max_token'] = True

    markdown_summary_path = output_dir / 'summary-table.md'
    table.sort(key=lambda x: (x['treebank'], x['model'], x['special_tr'], int(x['version'].split('.')[0]), int(x['version'].split('.')[1]), x['dependency_included']))
    markdown_str = '| Treebank | Version | Model | Character-based | Token-based | Dependency-included | Sentence count | Date | Special TR |\n'
    markdown_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for row in table:
        character_accuracy, token_accuracy = '%.1f' % (row['character-based'] * 100) + '%', '%.1f' % (row['token-based'] * 100) + '%'
        dep_included = 'Yes' if row['dependency_included'] else 'No'
        date = row['date']
        treebank, version, model, sentence_count = row['treebank'], row['version'], row['model'], row['sentence_count']
        if 'max_character' in run_d[treebank][version]:
            character_accuracy = f'**{character_accuracy}**'
        if 'max_token' in run_d[treebank][version]:
            token_accuracy = f'**{token_accuracy}**'
        special_tr = row['special_tr']
        markdown_str += f'| {treebank} | {version} | {model} | {character_accuracy} | {token_accuracy} | {dep_included} | {sentence_count} | {date} | {special_tr} |\n'
    with markdown_summary_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()