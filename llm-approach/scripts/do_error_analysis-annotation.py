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
    v2_8_match, v2_11_match, all = 0, 0, 0
    v2_8_mismatches, v2_11_mismatches = {}, {}
    v2_8_error_feat_count_d, v2_11_error_feat_count_d = {}, {}
    v2_8_feat_count_d, v2_11_feat_count_d = {}, {}
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
            while True:
                if idx_8 < len(v2_8_tokens) - 1 and fuzz.ratio(token, v2_8_tokens[idx_8 + 1]) > fuzz.ratio(token, v2_8_tokens[idx_8]):
                    idx_8 += 1
                elif idx_8 - 1 > -1 and idx_8 < len(v2_8_tokens) and fuzz.ratio(token, v2_8_tokens[idx_8 - 1]) > fuzz.ratio(token, v2_8_tokens[idx_8]):
                    idx_8 -= 1
                else:
                    break
            while True:
                if idx_11 < len(v2_11_tokens) - 1 and fuzz.ratio(token, v2_11_tokens[idx_11 + 1]) > fuzz.ratio(token, v2_11_tokens[idx_11]):
                    idx_11 += 1
                elif idx_11 - 1 > -1 and idx_11 < len(v2_11_tokens) and fuzz.ratio(token, v2_11_tokens[idx_11 - 1]) > fuzz.ratio(token, v2_11_tokens[idx_11]):
                    idx_11 -= 1
                else:
                    break
            if idx_8 < len(v2_8_tokens) and token != v2_8_tokens[idx_8] and idx_11 < len(v2_11_tokens) and token == v2_11_tokens[idx_11]:
                comparison_d[i] = {'v2.8': 0, 'v2.11': 1, 'idx_8': idx_8, 'idx_11': idx_11}
            elif idx_8 < len(v2_8_tokens) and token == v2_8_tokens[idx_8] and idx_11 < len(v2_11_tokens) and token != v2_11_tokens[idx_11]:
                comparison_d[i] = {'v2.8': 1, 'v2.11': 0, 'idx_8': idx_8, 'idx_11': idx_11}
            if idx_8 < len(v2_8_tokens) and token != v2_8_tokens[idx_8]:
                if sent_id not in v2_8_mismatches:
                    v2_8_mismatches[sent_id] = []
                v2_8_mismatches[sent_id].append(idx_8)
            if idx_11 < len(v2_11_tokens) and token != v2_11_tokens[idx_11]:
                if sent_id not in v2_11_mismatches:
                    v2_11_mismatches[sent_id] = []
                v2_11_mismatches[sent_id].append(idx_11)
            if idx_8 < len(v2_8_tokens) and token == v2_8_tokens[idx_8]:
                v2_8_match += 1
            if idx_11 < len(v2_11_tokens) and token == v2_11_tokens[idx_11]:
                v2_11_match += 1
            all += 1
            idx_8 += 1
            idx_11 += 1
        v2_8_annotation = {}
        token_idx = 0
        in_split = -1
        for i, line in enumerate(v2_8_table.split('\n')):
            fields = line.split('\t')
            id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
            if feats_t != '_':
                feat_l = feats_t.split('|')
                for feat in feat_l:
                    if feat not in v2_8_feat_count_d:
                        v2_8_feat_count_d[feat] = 0
                    v2_8_feat_count_d[feat] += 1
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
            if sent_id in v2_8_mismatches and token_idx in v2_8_mismatches[sent_id]:
                if feats_t == '_':
                    continue
                feat_l = feats_t.split('|')
                for feat in feat_l:
                    if feat not in v2_8_error_feat_count_d:
                        v2_8_error_feat_count_d[feat] = {'mismatch_count': 0}
                    v2_8_error_feat_count_d[feat]['mismatch_count'] += 1
            v2_8_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_8_annotation[id_t]['space_after'] = False
            for key in comparison_d:
                if comparison_d[key]['idx_8'] == token_idx:
                    if 'v2.8 feats' not in comparison_d[key]:
                        comparison_d[key]['v2.8 feats'] = ''
                    if comparison_d[key]['v2.8 feats'] != '' and feats_t != '_':
                        comparison_d[key]['v2.8 feats'] += '|'
                        comparison_d[key]['v2.8 feats'] += feats_t
                    elif comparison_d[key]['v2.8 feats'] == '' and feats_t != '_':
                        comparison_d[key]['v2.8 feats'] = feats_t
                    break
            if in_split == 0:
                in_split = 1
                for key in comparison_d:
                    if comparison_d[key]['idx_8'] == token_idx:
                        comparison_d[key]['split'] = True
                        break
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
            if feats_t != '_':
                feat_l = feats_t.split('|')
                for feat in feat_l:
                    if feat not in v2_11_feat_count_d:
                        v2_11_feat_count_d[feat] = 0
                    v2_11_feat_count_d[feat] += 1
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
            if sent_id in v2_11_mismatches and token_idx in v2_11_mismatches[sent_id]:
                if feats_t == '_':
                    continue
                feat_l = feats_t.split('|')
                for feat in feat_l:
                    if feat not in v2_11_error_feat_count_d:
                        v2_11_error_feat_count_d[feat] = {'mismatch_count': 0}
                    v2_11_error_feat_count_d[feat]['mismatch_count'] += 1
            v2_11_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_11_annotation[id_t]['space_after'] = False
            for key in comparison_d:
                if comparison_d[key]['idx_11'] == token_idx:
                    if 'v2.11 feats' not in comparison_d[key]:
                        comparison_d[key]['v2.11 feats'] = ''
                    if comparison_d[key]['v2.11 feats'] != '' and feats_t != '_':
                        comparison_d[key]['v2.11 feats'] += '|'
                        comparison_d[key]['v2.11 feats'] += feats_t
                    elif comparison_d[key]['v2.11 feats'] == '' and feats_t != '_':
                        comparison_d[key]['v2.11 feats'] = feats_t
                    break
            if in_split == 0:
                in_split = 1
                for key in comparison_d:
                    if comparison_d[key]['idx_11'] == token_idx:
                        comparison_d[key]['split'] = True
                        break
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

        analysis_d['sentences'][sent_id] = comparison_d

    analysis_d['feats'] = {'increase': {}, 'decrease': {}}
    for sent_id in analysis_d['sentences'].keys():
        ids = list(analysis_d['sentences'][sent_id].keys())
        for id_t in ids:
            el = analysis_d['sentences'][sent_id][id_t]
            v2_8, v2_11 = el['v2.8'], el['v2.11']
            if 'v2.8 feats' not in el or 'v2.11 feats' not in el:
                continue
            feats8, feats11 = el['v2.8 feats'], el['v2.11 feats']
            feat_l_8, feat_l_11 = feats8.split('|'), feats11.split('|')
            feat_d_8, feat_d_11 = {}, {}
            for feat in feat_l_8:
                if feat != '':
                    tag, value = feat.split('=')
                    feat_d_8[tag] = value
            tag_s = set(feat_d_8.keys())
            for feat in feat_l_11:
                if feat != '':
                    tag, value = feat.split('=')
                    feat_d_11[tag] = value
            tag_s.update(feat_d_11.keys())
            if v2_8 == 0 and v2_11 == 1:
                for tag in tag_s:
                    if tag not in feat_d_8:
                        tup = ('add', '{}={}'.format(tag, feat_d_11[tag]))
                    elif tag not in feat_d_11:
                        tup = ('remove', '{}={}'.format(tag, feat_d_8[tag]))
                    elif feat_d_8[tag] != feat_d_11[tag]:
                        tup = ('change', '{}={}'.format(tag, feat_d_8[tag]), '{}={}'.format(tag, feat_d_11[tag]))
                    else:
                        continue
                    if tup not in analysis_d['feats']['increase']:
                        analysis_d['feats']['increase'][tup] = 0
                    analysis_d['feats']['increase'][tup] += 1
            elif v2_8 == 1 and v2_11 == 0:
                for tag in tag_s:
                    if tag not in feat_d_8:
                        tup = ('remove', '{}={}'.format(tag, feat_d_11[tag]))
                    elif tag not in feat_d_11:
                        tup = ('add', '{}={}'.format(tag, feat_d_8[tag]))
                    elif feat_d_8[tag] != feat_d_11[tag]:
                        tup = ('change', '{}={}'.format(tag, feat_d_11[tag]), '{}={}'.format(tag, feat_d_8[tag]))
                    else:
                        continue
                    if tup not in analysis_d['feats']['decrease']:
                        analysis_d['feats']['decrease'][tup] = 0
                    analysis_d['feats']['decrease'][tup] += 1

    increase_d = analysis_d['feats']['increase'].copy()
    keys = list(increase_d.keys())
    keys.sort(key=lambda x: increase_d[x], reverse=True)
    analysis_d['feats']['increase'] = []
    for key in keys:
        analysis_d['feats']['increase'].append({'tuple': list(key), 'count': increase_d[key]})
    decrease_d = analysis_d['feats']['decrease'].copy()
    keys = list(decrease_d.keys())
    keys.sort(key=lambda x: decrease_d[x], reverse=True)
    analysis_d['feats']['decrease'] = []
    for key in keys:
        analysis_d['feats']['decrease'].append({'tuple': list(key), 'count': decrease_d[key]})

    with open(os.path.join(THIS_DIR, 'error_analysis-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, indent=4, ensure_ascii=False)
    
    for feat in v2_8_error_feat_count_d:
        v2_8_error_feat_count_d[feat]['all_count'] = v2_8_feat_count_d[feat]
        v2_8_error_feat_count_d[feat]['ratio'] = v2_8_error_feat_count_d[feat]['mismatch_count'] / v2_8_feat_count_d[feat]
    for feat in v2_11_error_feat_count_d:
        v2_11_error_feat_count_d[feat]['all_count'] = v2_11_feat_count_d[feat]
        v2_11_error_feat_count_d[feat]['ratio'] = v2_11_error_feat_count_d[feat]['mismatch_count'] / v2_11_feat_count_d[feat]

    v2_8_error_feat_count_d = {k: v for k, v in sorted(v2_8_error_feat_count_d.items(), key=lambda item: item[1]['mismatch_count'], reverse=True)}
    v2_11_error_feat_count_d = {k: v for k, v in sorted(v2_11_error_feat_count_d.items(), key=lambda item: item[1]['mismatch_count'], reverse=True)}
    with open(os.path.join(THIS_DIR, 'v2_8_error_feat_count_d-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(v2_8_error_feat_count_d, f, indent=4, ensure_ascii=False)
    with open(os.path.join(THIS_DIR, 'v2_11_error_feat_count_d-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(v2_11_error_feat_count_d, f, indent=4, ensure_ascii=False)

    print('Model:', model)
    print('v2.8 ratio: {}'.format(v2_8_match / all))
    print('v2.11 ratio: {}'.format(v2_11_match / all))

if __name__ == '__main__':
    main()