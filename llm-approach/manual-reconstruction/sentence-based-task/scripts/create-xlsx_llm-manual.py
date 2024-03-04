import argparse, json
from pathlib import Path
import xlsxwriter

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    parser.add_argument('-o', '--order', type=str)
    parser.add_argument('-tb', '--treebank-dir', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with open(args.constructions, 'r', encoding='utf-8') as f:
        constructions = json.load(f)
    llm_dir = Path(args.llm_dir)
    version1 = args.version1
    version2 = args.version2
    if '{}_output-cleaned.json'.format(version1) in [f.name for f in llm_dir.iterdir()]:
        v1_output = llm_dir / '{}_output-cleaned.json'.format(version1)
        v2_output = llm_dir / '{}_output-cleaned.json'.format(version2)
        with open(v1_output, 'r', encoding='utf-8') as f:
            v1_data = json.load(f)
        with open(v2_output, 'r', encoding='utf-8') as f:
            v2_data = json.load(f)
    else:
        v1_output = llm_dir / '{}_output.json'.format(version1)
        v2_output = llm_dir / '{}_output.json'.format(version2)
        with open(v1_output, 'r', encoding='utf-8') as f:
            v1_data = json.load(f)
        with open(v2_output, 'r', encoding='utf-8') as f:
            v2_data = json.load(f)

    person1 = args.person1
    person2 = args.person2

    if args.order:
        filepath = llm_dir / 'llm-manual-{}.xlsx'.format(args.order)
    else:
        filepath = llm_dir / 'llm-manual.xlsx'

    tb_dir = Path(args.treebank_dir)
    v1_path = tb_dir / version1 / 'treebank.json'
    v2_path = tb_dir / version2 / 'treebank.json'
    with open(v1_path, 'r', encoding='utf-8') as f:
        v1_tb = json.load(f)
    with open(v2_path, 'r', encoding='utf-8') as f:
        v2_tb = json.load(f)

    workbook = xlsxwriter.Workbook(filepath)
    bold = workbook.add_format({'bold': True})

    sent_ids = list(constructions[person1][version1].keys())
    for sent_id in sent_ids:
        original_text = v1_data[sent_id]['original_text']
        p1_v1_text = constructions[person1][version1][sent_id]
        p1_v2_text = constructions[person1][version2][sent_id]
        p2_v1_text = constructions[person2][version1][sent_id]
        p2_v2_text = constructions[person2][version2][sent_id]
        llm_v1_text = v1_data[sent_id]['output_text']
        llm_v2_text = v2_data[sent_id]['output_text']

        worksheet = workbook.add_worksheet(sent_id)
        worksheet.write(0, 0, 'Type', bold)
        worksheet.write(0, 1, 'Text', bold)
        worksheet.write(0, 2, 'Comments', bold)

        worksheet.write(1, 0, 'Original')
        worksheet.write(1, 1, original_text)
        worksheet.write(2, 0, 'Annotator 1 - {}'.format(version1))
        worksheet.write(2, 1, p1_v1_text)
        worksheet.write(3, 0, 'Annotator 2 - {}'.format(version1))
        worksheet.write(3, 1, p2_v1_text)
        worksheet.write(4, 0, 'LLM - {}'.format(version1))
        worksheet.write(4, 1, llm_v1_text)
        worksheet.write(5, 0, 'Annotator 1 - {}'.format(version2))
        worksheet.write(5, 1, p1_v2_text)
        worksheet.write(6, 0, 'Annotator 2 - {}'.format(version2))
        worksheet.write(6, 1, p2_v2_text)
        worksheet.write(7, 0, 'LLM - {}'.format(version2))
        worksheet.write(7, 1, llm_v2_text)

        # add annotations
        v1_table = v1_tb[sent_id]['table']
        v2_table = v2_tb[sent_id]['table']

        worksheet.merge_range(0, 3, 0, 9, 'Annotations - {}'.format(version1), bold)
        worksheet.write(1, 3, 'ID', bold)
        worksheet.write(1, 4, 'Form', bold)
        worksheet.write(1, 5, 'Lemma', bold)
        worksheet.write(1, 6, 'UPOS', bold)
        worksheet.write(1, 7, 'Feats', bold)
        worksheet.write(1, 8, 'Head', bold)
        worksheet.write(1, 9, 'Deprel', bold)

        for i, row in enumerate(v1_table.split('\n')):
            fields = row.split('\t')
            id_t, form_t, lemma_t, upos_t, feats_t, head_t, deprel_t = fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], fields[7]
            worksheet.write(2+i, 3, id_t)
            worksheet.write(2+i, 4, form_t)
            worksheet.write(2+i, 5, lemma_t)
            worksheet.write(2+i, 6, upos_t)
            worksheet.write(2+i, 7, feats_t)
            worksheet.write(2+i, 8, head_t)
            worksheet.write(2+i, 9, deprel_t)
        cont_idx = 4+i

        worksheet.merge_range(cont_idx+1, 3, cont_idx+1, 9, 'Annotations - {}'.format(version2), bold)
        worksheet.write(cont_idx+1, 3, 'ID', bold)
        worksheet.write(cont_idx+1, 4, 'Form', bold)
        worksheet.write(cont_idx+1, 5, 'Lemma', bold)
        worksheet.write(cont_idx+1, 6, 'UPOS', bold)
        worksheet.write(cont_idx+1, 7, 'Feats', bold)
        worksheet.write(cont_idx+1, 8, 'Head', bold)
        worksheet.write(cont_idx+1, 9, 'Deprel', bold)

        for i, row in enumerate(v2_table.split('\n')):
            fields = row.split('\t')
            id_t, form_t, lemma_t, upos_t, feats_t, head_t, deprel_t = fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], fields[7]
            worksheet.write(cont_idx+2+i, 3, id_t)
            worksheet.write(cont_idx+2+i, 4, form_t)
            worksheet.write(cont_idx+2+i, 5, lemma_t)
            worksheet.write(cont_idx+2+i, 6, upos_t)
            worksheet.write(cont_idx+2+i, 7, feats_t)
            worksheet.write(cont_idx+2+i, 8, head_t)
            worksheet.write(cont_idx+2+i, 9, deprel_t)
        
        worksheet.autofit()

    workbook.close()

if __name__ == '__main__':
    main()