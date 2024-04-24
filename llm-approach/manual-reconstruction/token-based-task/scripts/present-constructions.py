import argparse, json, json, xlsxwriter
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-tb1', '--treebank1', type=str, required=True)
    parser.add_argument('-tb2', '--treebank2', type=str, required=True)
    return parser.parse_args()

def get_form(sent_id, token_id, version, tbs, has_dep=False):
    if version == 'v1':
        table = tbs['v1'][sent_id]['table']
    elif version == 'v2':
        table = tbs['v2'][sent_id]['table']
    if has_dep:
        head_d = {}
    for line in table.split('\n'):
        fields = line.split('\t')
        id_t = fields[0]
        if has_dep:
            form_t = fields[1]
            head_d[id_t] = form_t
        if id_t == str(token_id):
            form, lemma, upos, feats = fields[1], fields[2], fields[3], fields[5]
            if has_dep:
                head, deprel = fields[6], fields[7]
    if has_dep:
        if head == '0':
            head = '-'
        else:
            head = head_d[head]
        return form, lemma, upos, feats, head, deprel
    else:
        return form, lemma, upos, feats

lower_d = {
    'I': 'ı',
    'İ': 'i',
    'Ğ': 'ğ',
    'Ü': 'ü',
    'Ş': 'ş',
    'Ö': 'ö',
    'Ç': 'ç'
}

def lower(s):
    for k, v in lower_d.items():
        s = s.replace(k, v)
    return s.lower()

def main():
    args = get_args()
    constructions_path = Path(args.constructions)
    with constructions_path.open('r', encoding='utf-8') as f:
        constructions = json.load(f)
    dir = constructions_path.parent
    
    tb1_path = Path(args.treebank1)
    with tb1_path.open('r', encoding='utf-8') as f:
        tb1_data = json.load(f)
    tb2_path = Path(args.treebank2)
    with tb2_path.open('r', encoding='utf-8') as f:
        tb2_data = json.load(f)
    tbs = {'v1': tb1_data, 'v2': tb2_data}
    difficulties = ['easy', 'medium', 'difficult', 'random']
    types = ['dep', 'normal']
    versions = ['v1', 'v2']
    annotators = ['Akif', 'Tarık', 'GPT-4']

    # workbook = xlsxwriter.Workbook(filepath)
    # bold = workbook.add_format({'bold': True})

    # sent_ids = list(constructions[person1][version1].keys())
    # for sent_id in sent_ids:
    #     original_text = v1_data[sent_id]['original_text']
    #     p1_v1_text = constructions[person1][version1][sent_id]
    #     p1_v2_text = constructions[person1][version2][sent_id]
    #     p2_v1_text = constructions[person2][version1][sent_id]
    #     p2_v2_text = constructions[person2][version2][sent_id]
    #     llm_v1_text = v1_data[sent_id]['output_text']
    #     llm_v2_text = v2_data[sent_id]['output_text']

    #     worksheet = workbook.add_worksheet(sent_id)
    #     worksheet.write(0, 0, 'Type', bold)
    #     worksheet.write(0, 1, 'Text', bold)
    #     worksheet.write(0, 2, 'Comments', bold)

    #     worksheet.write(1, 0, 'Original')
    #     worksheet.write(1, 1, original_text)
    #     worksheet.write(2, 0, 'Annotator 1 - {}'.format(version1))
    #     worksheet.write(2, 1, p1_v1_text)
    #     worksheet.write(3, 0, 'Annotator 2 - {}'.format(version1))
    #     worksheet.write(3, 1, p2_v1_text)
    #     worksheet.write(4, 0, 'LLM - {}'.format(version1))
    #     worksheet.write(4, 1, llm_v1_text)
    #     worksheet.write(5, 0, 'Annotator 1 - {}'.format(version2))
    #     worksheet.write(5, 1, p1_v2_text)
    #     worksheet.write(6, 0, 'Annotator 2 - {}'.format(version2))
    #     worksheet.write(6, 1, p2_v2_text)
    #     worksheet.write(7, 0, 'LLM - {}'.format(version2))
    #     worksheet.write(7, 1, llm_v2_text)

    #     # add annotations
    #     v1_table = v1_tb[sent_id]['table']
    #     v2_table = v2_tb[sent_id]['table']

    #     worksheet.merge_range(0, 3, 0, 9, 'Annotations - {}'.format(version1), bold)
    #     worksheet.write(1, 3, 'ID', bold)
    #     worksheet.write(1, 4, 'Form', bold)
    #     worksheet.write(1, 5, 'Lemma', bold)
    #     worksheet.write(1, 6, 'UPOS', bold)
    #     worksheet.write(1, 7, 'Feats', bold)
    #     worksheet.write(1, 8, 'Head', bold)
    #     worksheet.write(1, 9, 'Deprel', bold)

    #     for i, row in enumerate(v1_table.split('\n')):
    #         fields = row.split('\t')
    #         id_t, form_t, lemma_t, upos_t, feats_t, head_t, deprel_t = fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], fields[7]
    #         worksheet.write(2+i, 3, id_t)
    #         worksheet.write(2+i, 4, form_t)
    #         worksheet.write(2+i, 5, lemma_t)
    #         worksheet.write(2+i, 6, upos_t)
    #         worksheet.write(2+i, 7, feats_t)
    #         worksheet.write(2+i, 8, head_t)
    #         worksheet.write(2+i, 9, deprel_t)
    #     cont_idx = 3+i

    #     worksheet.merge_range(cont_idx+1, 3, cont_idx+1, 9, 'Annotations - {}'.format(version2), bold)
    #     worksheet.write(cont_idx+2, 3, 'ID', bold)
    #     worksheet.write(cont_idx+2, 4, 'Form', bold)
    #     worksheet.write(cont_idx+2, 5, 'Lemma', bold)
    #     worksheet.write(cont_idx+2, 6, 'UPOS', bold)
    #     worksheet.write(cont_idx+2, 7, 'Feats', bold)
    #     worksheet.write(cont_idx+2, 8, 'Head', bold)
    #     worksheet.write(cont_idx+2, 9, 'Deprel', bold)

    #     for i, row in enumerate(v2_table.split('\n')):
    #         fields = row.split('\t')
    #         id_t, form_t, lemma_t, upos_t, feats_t, head_t, deprel_t = fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], fields[7]
    #         worksheet.write(cont_idx+3+i, 3, id_t)
    #         worksheet.write(cont_idx+3+i, 4, form_t)
    #         worksheet.write(cont_idx+3+i, 5, lemma_t)
    #         worksheet.write(cont_idx+3+i, 6, upos_t)
    #         worksheet.write(cont_idx+3+i, 7, feats_t)
    #         worksheet.write(cont_idx+3+i, 8, head_t)
    #         worksheet.write(cont_idx+3+i, 9, deprel_t)

    #     worksheet.autofit()

    # workbook.close()

    markdown_str = '# Reconstructions\n\n'
    for difficulty in difficulties:
        markdown_str += f'## {difficulty.capitalize()}\n\n'
        markdown_str += '| Sent ID | Token ID | Version | Annotator | Form | Lemma | UPOS | Feats | Head | Deprel |\n'
        markdown_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
        for sent_id in constructions[difficulty]:
            for version in versions:
                for token_id in constructions[difficulty][sent_id][version]:
                    type_t = constructions[difficulty][sent_id][version][token_id]['type']
                    has_dep = True if type_t == 'dep' else False
                    if has_dep:
                        original_form, lemma, upos, feats, head, deprel = get_form(sent_id, token_id, version, tbs, has_dep)
                    else:
                        original_form, lemma, upos, feats = get_form(sent_id, token_id, version, tbs)
                        head, deprel = None, None
                    feats = feats.replace('|', '\\|')
                    if version == 'v1':
                        version_t = 'v2.8'
                    elif version == 'v2':
                        version_t = 'v2.11'
                    markdown_str += f'| {sent_id} | {token_id} | {version_t} | Original | {lower(original_form)} | {lemma} | {upos} | {feats} | {head} | {deprel} |\n'
                    for annotator in annotators:
                        if annotator in constructions[difficulty][sent_id][version][token_id]['annotators']:
                            form = constructions[difficulty][sent_id][version][token_id]['annotators'][annotator]
                            markdown_str += f'| {sent_id} | {token_id} | {version_t} | {annotator} | {form} | {lemma} | {upos} | {feats} | {head} | {deprel} |\n'
                    markdown_str += '| | | | | | | | | | |\n'
            markdown_str += '| | | | | | | | | | |\n'
        markdown_str += '\n'

    markdown_path = dir / 'reconstructions.md'
    with markdown_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()