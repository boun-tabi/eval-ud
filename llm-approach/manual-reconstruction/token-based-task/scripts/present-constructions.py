import argparse, json, json, csv
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
    versions = ['v1', 'v2']
    annotators = ['Akif', 'Tarık', 'GPT-4']

    markdown_str = '# Reconstructions\n\n'
    csv_file = dir / 'reconstructions.csv'
    with csv_file.open('w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Sent ID', 'Token ID', 'Version', 'Annotator', 'Form', 'Lemma', 'UPOS', 'Feats', 'Head', 'Deprel'])
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
                            head, deprel = '', ''
                        feats_md = feats.replace('|', '\\|')
                        if version == 'v1':
                            version_t = 'v2.8'
                        elif version == 'v2':
                            version_t = 'v2.11'
                        markdown_str += f'| {sent_id} | {token_id} | {version_t} | Original | {lower(original_form)} | {lemma} | {upos} | {feats_md} | {head} | {deprel} |\n'
                        writer.writerow([sent_id, token_id, version_t, 'Original', lower(original_form), lemma, upos, feats, head, deprel])
                        for annotator in annotators:
                            if annotator in constructions[difficulty][sent_id][version][token_id]['annotators']:
                                form = constructions[difficulty][sent_id][version][token_id]['annotators'][annotator]
                                markdown_str += f'| {sent_id} | {token_id} | {version_t} | {annotator} | {form} | {lemma} | {upos} | {feats_md} | {head} | {deprel} |\n'
                                writer.writerow([sent_id, token_id, version_t, annotator, form, lemma, upos, feats, head, deprel])
                        markdown_str += '| | | | | | | | | | |\n'
                markdown_str += '| | | | | | | | | | |\n'
            markdown_str += '\n'

    markdown_path = dir / 'reconstructions.md'
    with markdown_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()