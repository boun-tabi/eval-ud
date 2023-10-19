import os, argparse, json
from spacy.tokenizer import Tokenizer
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    tr_boun_dir = os.path.join(THIS_DIR, '..', 'tr_boun')

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    args = parser.parse_args()

    dir = args.directory
    summary_path = os.path.join(dir, 'summary.json')
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    md_path = os.path.join(dir, 'md.json')
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    model = md['model']

    tb8_path, tb11_path = os.path.join(tr_boun_dir, 'v2.8', 'treebank.json'), os.path.join(tr_boun_dir, 'v2.11', 'treebank.json')
    with open(tb8_path, 'r', encoding='utf-8') as f:
        tb8_temp = json.load(f)
    tb8 = {}
    for el in tb8_temp:
        sent_id = el['sent_id']
        del el['sent_id']
        tb8[sent_id] = el
    with open(tb11_path, 'r', encoding='utf-8') as f:
        tb11_temp = json.load(f)
    tb11 = {}
    for el in tb11_temp:
        sent_id = el['sent_id']
        del el['sent_id']
        tb11[sent_id] = el

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    analysis_d = {'sentences': {}}
    for sent_id, value in results.items():
        v2_8_table, v2_11_table = tb8[sent_id]['table'], tb11[sent_id]['table']
        original_text, text_v2_8, text_v2_11 = value['original text'], value['v2.8 text'], value['v2.11 text']
        if text_v2_8[0] == '"' and text_v2_8[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_8 = text_v2_8[1:-1]
        if text_v2_11[0] == '"' and text_v2_11[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_11 = text_v2_11[1:-1]

        v2_8_tokens = []
        for token in tokenizer(text_v2_8):
            v2_8_tokens.append(token.text)
        v2_11_tokens = []
        for token in tokenizer(text_v2_11):
            v2_11_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        comparison_d = {}
        idx_8, idx_11 = 0, 0
        for i, token in enumerate(original_tokens):
            while idx_8 < len(v2_8_tokens) - 1 and fuzz.ratio(token, v2_8_tokens[idx_8 + 1]) > fuzz.ratio(token, v2_11_tokens[idx_8]):
                idx_8 += 1
            while idx_11 < len(v2_11_tokens) - 1 and fuzz.ratio(token, v2_11_tokens[idx_11 + 1]) > fuzz.ratio(token, v2_11_tokens[idx_11]):
                idx_11 += 1
            if idx_8 < len(v2_8_tokens) and token != v2_8_tokens[idx_8] and idx_11 < len(v2_11_tokens) and token == v2_11_tokens[idx_11]:
                comparison_d[i] = {'v2.8': 0, 'v2.11': 1, 'idx_8': idx_8, 'idx_11': idx_11}
                print(token)
                print('v2.8: {} | v2.11: {}'.format(v2_8_tokens[idx_8], v2_11_tokens[idx_11]))
                input()
            elif idx_8 < len(v2_8_tokens) and token == v2_8_tokens[idx_8] and idx_11 < len(v2_11_tokens) and token != v2_11_tokens[idx_11]:
                comparison_d[i] = {'v2.8': 1, 'v2.11': 0, 'idx_8': idx_8, 'idx_11': idx_11}

        v2_8_annotation = {}
        token_idx = 0
        in_split = -1
        for i, line in enumerate(v2_8_table.split('\n')):
            fields = line.split('\t')
            id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
            if '-' in id_t:
                in_split = 0
                continue
            while 1:
                if token_idx < len(v2_8_tokens) - 1 and fuzz.ratio(form_t, v2_8_tokens[token_idx + 1]) > fuzz.ratio(form_t, v2_8_tokens[token_idx]):
                    token_idx += 1
                elif token_idx - 1 > -1 and token_idx < len(v2_8_tokens) and fuzz.ratio(form_t, v2_8_tokens[token_idx - 1]) > fuzz.ratio(form_t, v2_8_tokens[token_idx]):
                    token_idx -= 1
                else:
                    break
            v2_8_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_8_annotation[id_t]['space_after'] = False
            if token_idx in comparison_d:
                if 'v2.8 feats' not in comparison_d[token_idx]:
                    comparison_d[token_idx]['v2.8 feats'] = ''
                if comparison_d[token_idx]['v2.8 feats'] != '' and feats_t != '_':
                    comparison_d[token_idx]['v2.8 feats'] += '|'
                    comparison_d[token_idx]['v2.8 feats'] += feats_t
                elif comparison_d[token_idx]['v2.8 feats'] == '' and feats_t != '_':
                    comparison_d[token_idx]['v2.8 feats'] = feats_t
            if in_split == 0:
                in_split = 1
            elif in_split == 1:
                token_idx += 1
                in_split = -1
            elif in_split == -1:
                token_idx += 1

        v2_11_annotation = {}
        token_idx = 0
        in_split = -1
        for i, line in enumerate(v2_11_table.split('\n')):
            fields = line.split('\t')
            id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
            if '-' in id_t:
                in_split = 0
                continue
            while 1:
                if token_idx < len(v2_11_tokens) - 1 and fuzz.ratio(form_t, v2_11_tokens[token_idx + 1]) > fuzz.ratio(form_t, v2_11_tokens[token_idx]):
                    token_idx += 1
                elif token_idx - 1 > -1 and token_idx < len(v2_11_tokens) and fuzz.ratio(form_t, v2_11_tokens[token_idx - 1]) > fuzz.ratio(form_t, v2_11_tokens[token_idx]):
                    token_idx -= 1
                else:
                    break
            v2_11_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_11_annotation[id_t]['space_after'] = False
            if token_idx in comparison_d:
                if 'v2.11 feats' not in comparison_d[token_idx]:
                    comparison_d[token_idx]['v2.11 feats'] = ''
                if comparison_d[token_idx]['v2.11 feats'] != '' and feats_t != '_':
                    comparison_d[token_idx]['v2.11 feats'] += '|'
                    comparison_d[token_idx]['v2.11 feats'] += feats_t
                elif comparison_d[token_idx]['v2.11 feats'] == '' and feats_t != '_':
                    comparison_d[token_idx]['v2.11 feats'] = feats_t
            if in_split == 0:
                in_split = 1
                if token_idx in comparison_d:
                    comparison_d[token_idx]['split'] = True
            elif in_split == 1:
                in_split = -1
            elif in_split == -1:
                token_idx += 1
        
        for key in comparison_d:
            if 'split' not in comparison_d[key]:
                comparison_d[key]['split'] = False
            comparison_d[key]['token'] = original_tokens[key]
            comparison_d[key]['v2.8 token'] = v2_8_tokens[comparison_d[key]['idx_8']]
            comparison_d[key]['v2.11 token'] = v2_11_tokens[comparison_d[key]['idx_11']]

        print(json.dumps(comparison_d, indent=4, ensure_ascii=False))
        input()

        analysis_d['sentences'][sent_id] = comparison_d

    with open(os.path.join(THIS_DIR, 'error_analysis-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()