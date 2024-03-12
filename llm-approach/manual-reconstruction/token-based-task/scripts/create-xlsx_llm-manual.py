import argparse, json
from pathlib import Path
import xlsxwriter

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run-dir', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()

    run_dir = Path(args.run_dir)
    outputs_path = run_dir / 'outputs.json'

    with open(outputs_path, 'r') as f:
        outputs = json.load(f)

    md_path = run_dir / 'md.json'

    with open(md_path, 'r') as f:
        md = json.load(f)

    version1 = args.version1
    version2 = args.version2
    person1 = args.person1
    person2 = args.person2

    filepath = run_dir / 'llm-manual.xlsx'

    workbook = xlsxwriter.Workbook(filepath)
    bold = workbook.add_format({'bold': True})

    token_ids = list(outputs.keys())
    for token_id in token_ids:
        original_form = outputs[token_id]['original_form']
        p1_v1_forms = outputs[token_id][version1][person1]
        p1_v2_forms = outputs[token_id][version2][person1]
        p2_v1_forms = outputs[token_id][version1][person2]
        p2_v2_forms = outputs[token_id][version2][person2]
        llm_v1_form = outputs[token_id][version1]['llm']
        llm_v2_form = outputs[token_id][version2]['llm']

        worksheet = workbook.add_worksheet(token_id)
        worksheet.write(0, 0, 'Type', bold)
        worksheet.write(0, 1, 'Form', bold)

        max_i = max(len(p1_v1_forms), len(p1_v2_forms), len(p2_v1_forms), len(p2_v2_forms))
        worksheet.write(1, 0, 'Original')
        worksheet.write(1, 1, original_form)
        worksheet.write(2, 0, 'Annotator 1 - {}'.format(version1))
        for i, form in enumerate(p1_v1_forms):
            worksheet.write(2, 1+i, form)
        worksheet.write(3, 0, 'Annotator 2 - {}'.format(version1))
        for i, form in enumerate(p2_v1_forms):
            worksheet.write(3, 1+i, form)
        worksheet.write(4, 0, 'LLM - {}'.format(version1))
        worksheet.write(4, 1, llm_v1_form)
        worksheet.write(5, 0, 'Annotator 1 - {}'.format(version2))
        for i, form in enumerate(p1_v2_forms):
            worksheet.write(5, 1+i, form)
        worksheet.write(6, 0, 'Annotator 2 - {}'.format(version2))
        for i, form in enumerate(p2_v2_forms):
            worksheet.write(6, 1+i, form)
        worksheet.write(7, 0, 'LLM - {}'.format(version2))
        worksheet.write(7, 1, llm_v2_form)

        worksheet.write(0, max_i+1, 'Comments', bold)

        # add annotations
        v1_table = md['tokens1'][token_id]['md_line']

        v1_lines = v1_table.split('\n')
        keys, values = v1_lines[0].replace('| ', '$').replace(' |', '$'), v1_lines[2].replace('| ', '$').replace(' |', '$')
        v1_d = {k.strip(): v.strip().replace('\\|', '|') for k, v in zip(keys.split('$')[1:], values.split('$')[1:]) if k.strip() and v.strip()}

        v2_table = md['tokens2'][token_id]['md_line']

        v2_lines = v2_table.split('\n')
        keys, values = v2_lines[0].replace('| ', '$').replace(' |', '$'), v2_lines[2].replace('| ', '$').replace(' |', '$')
        v2_d = {k.strip(): v.strip().replace('\\|', '|') for k, v in zip(keys.split('$')[1:], values.split('$')[1:]) if k.strip() and v.strip()}

        worksheet.merge_range(0, max_i+3, 0, max_i+3+len(v1_d), 'Annotations - {}'.format(version1), bold)
        for i, (k, v) in enumerate(v1_d.items()):
            worksheet.write(1, max_i+3+i, k, bold)
            worksheet.write(2, max_i+3+i, v)

        worksheet.merge_range(4, max_i+3, 4, max_i+3+len(v2_d), 'Annotations - {}'.format(version2), bold)
        for i, (k, v) in enumerate(v2_d.items()):
            worksheet.write(5, max_i+3+i, k, bold)
            worksheet.write(6, max_i+3+i, v)

        worksheet.autofit()

    workbook.close()

if __name__ == '__main__':
    main()