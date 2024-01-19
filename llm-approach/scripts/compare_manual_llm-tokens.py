import os, json, argparse, csv
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def main():

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    # tr_boun_dir = os.path.join(THIS_DIR, '..', 'tr_boun')

    parser = argparse.ArgumentParser()
    parser.add_argument('-pl', '--prev-llm', type=str, required=True)
    parser.add_argument('-cl', '--curr-llm', type=str, required=True)
    parser.add_argument('-m', '--manual', type=str, required=True)
    parser.add_argument('-n', '--note', type=str, required=True)
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    args = parser.parse_args()

    with open(args.prev_llm, 'r', encoding='utf-8') as f:
        prev_llm = json.load(f)
    original_d = {}
    v2_8_d = {}
    for sent in prev_llm:
        v2_8_d[sent['sent_id']] = sent['output']
        original_d[sent['sent_id']] = sent['text']
    with open(args.curr_llm, 'r', encoding='utf-8') as f:
        curr_llm = json.load(f)
    v2_11_d = {}
    for sent in curr_llm:
        v2_11_d[sent['sent_id']] = sent['output']
    with open(args.manual, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        sent_id_order = header.index('Sentence ID')
        version_order = header.index('Version')
        text_order = header.index('Text')
        manual = [row for row in reader]
    manual_d = {}
    for row in manual:
        sent_id = row[sent_id_order]
        version = row[version_order]
        text = row[text_order]
        if sent_id not in manual_d:
            manual_d[sent_id] = {}
        manual_d[sent_id][version] = text
    
    dir = args.directory
    summary_path = os.path.join(dir, 'summary.json')
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    md_path = os.path.join(dir, 'md.json')
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    model = md['model']

    # tb8_path, tb11_path = os.path.join(tr_boun_dir, 'v2.8', 'treebank.json'), os.path.join(tr_boun_dir, 'v2.11', 'treebank.json')
    # with open(tb8_path, 'r', encoding='utf-8') as f:
    #     tb8 = json.load(f)
    # with open(tb11_path, 'r', encoding='utf-8') as f:
    #     tb11 = json.load(f)

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    # analysis_d = {'sentences': {}}
    # v2_8_match, v2_11_match, all = 0, 0, 0
    # v2_8_mismatches, v2_11_mismatches = {}, {}
    # v2_8_error_feat_count_d, v2_11_error_feat_count_d = {}, {}
    # v2_8_feat_count_d, v2_11_feat_count_d = {}, {}
    comparison_d = {}
    for sent_id, value in results.items():
        if sent_id not in manual_d:
            continue
        comparison_d[sent_id] = {'v2.8 llm': {'correct': 0, 'all': 0}, 'v2.11 llm': {'correct': 0, 'all': 0}, 'v2.8 manual': {'correct': 0, 'all': 0}, 'v2.11 manual': {'correct': 0, 'all': 0}}
        # v2_8_table, v2_11_table = tb8[sent_id]['table'], tb11[sent_id]['table']
        original_text, text_v2_8_llm, text_v2_11_llm = value['original text'], value['v2.8 text'], value['v2.11 text']
        text_v2_8_manual, text_v2_11_manual = manual_d[sent_id]['v2.8'], manual_d[sent_id]['v2.11']
        if text_v2_8_llm[0] == '"' and text_v2_8_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_8_llm = text_v2_8_llm[1:-1]
        if text_v2_11_llm[0] == '"' and text_v2_11_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_11_llm = text_v2_11_llm[1:-1]

        v2_8_llm_tokens = []
        for token in tokenizer(text_v2_8_llm):
            v2_8_llm_tokens.append(token.text)
        v2_11_llm_tokens = []
        for token in tokenizer(text_v2_11_llm):
            v2_11_llm_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        v2_8_manual_tokens = []
        for token in tokenizer(text_v2_8_manual):
            v2_8_manual_tokens.append(token.text)
        v2_11_manual_tokens = []
        for token in tokenizer(text_v2_11_manual):
            v2_11_manual_tokens.append(token.text)
        match_llm_v2_8_d, match_llm_v2_11_d, match_manual_v2_8_d, match_manual_v2_11_d = {}, {}, {}, {}
        original_tokens_len = len(original_tokens)
        for i, token in enumerate(original_tokens):
            v2_8_llm_tokens_len = len(v2_8_llm_tokens)
            if v2_8_llm_tokens_len == 0:
                break
            elif v2_8_llm_tokens_len == 1:
                match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
            elif v2_8_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_8_llm_tokens[0]), fuzz.ratio(token, v2_8_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
                else:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[1]
            elif v2_8_llm_tokens_len > 2:
                first_three_items = v2_8_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[1]
                else:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[2]
            if len(v2_8_llm_tokens) > original_tokens_len - i:
                v2_8_llm_tokens = v2_8_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_8_llm_token = match_llm_v2_8_d[i]
            if token == v2_8_llm_token:
                comparison_d[sent_id]['v2.8 llm']['correct'] += 1
            comparison_d[sent_id]['v2.8 llm']['all'] += 1
        
        for i, token in enumerate(original_tokens):
            v2_11_llm_tokens_len = len(v2_11_llm_tokens)
            if v2_11_llm_tokens_len == 0:
                break
            elif v2_11_llm_tokens_len == 1:
                match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
            elif v2_11_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_11_llm_tokens[0]), fuzz.ratio(token, v2_11_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
                else:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[1]
            elif v2_11_llm_tokens_len > 2:
                first_three_items = v2_11_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[1]
                else:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[2]
            if len(v2_11_llm_tokens) > original_tokens_len - i:
                v2_11_llm_tokens = v2_11_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_11_llm_token = match_llm_v2_11_d[i]
            if token == v2_11_llm_token:
                comparison_d[sent_id]['v2.11 llm']['correct'] += 1
            comparison_d[sent_id]['v2.11 llm']['all'] += 1

        for i, token in enumerate(original_tokens):
            v2_8_manual_tokens_len = len(v2_8_manual_tokens)
            if v2_8_manual_tokens_len == 0:
                break
            elif v2_8_manual_tokens_len == 1:
                match_manual_v2_8_d[i] = v2_8_manual_tokens[0]
            elif v2_8_manual_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_8_manual_tokens[0]), fuzz.ratio(token, v2_8_manual_tokens[1])
                if ratio1 > ratio2:
                    match_manual_v2_8_d[i] = v2_8_manual_tokens[0]
                else:
                    match_manual_v2_8_d[i] = v2_8_manual_tokens[1]
            elif v2_8_manual_tokens_len > 2:
                first_three_items = v2_8_manual_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_manual_v2_8_d[i] = v2_8_manual_tokens[0]
                elif max_ratio == ratio2:
                    match_manual_v2_8_d[i] = v2_8_manual_tokens[1]
                else:
                    match_manual_v2_8_d[i] = v2_8_manual_tokens[2]
            if len(v2_8_manual_tokens) > original_tokens_len - i:
                v2_8_manual_tokens = v2_8_manual_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_8_manual_token = match_manual_v2_8_d[i]
            if token == v2_8_manual_token:
                comparison_d[sent_id]['v2.8 manual']['correct'] += 1
            comparison_d[sent_id]['v2.8 manual']['all'] += 1

        for i, token in enumerate(original_tokens):
            v2_11_manual_tokens_len = len(v2_11_manual_tokens)
            if v2_11_manual_tokens_len == 0:
                break
            elif v2_11_manual_tokens_len == 1:
                match_manual_v2_11_d[i] = v2_11_manual_tokens[0]
            elif v2_11_manual_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_11_manual_tokens[0]), fuzz.ratio(token, v2_11_manual_tokens[1])
                if ratio1 > ratio2:
                    match_manual_v2_11_d[i] = v2_11_manual_tokens[0]
                else:
                    match_manual_v2_11_d[i] = v2_11_manual_tokens[1]
            elif v2_11_manual_tokens_len > 2:
                first_three_items = v2_11_manual_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_manual_v2_11_d[i] = v2_11_manual_tokens[0]
                elif max_ratio == ratio2:
                    match_manual_v2_11_d[i] = v2_11_manual_tokens[1]
                else:
                    match_manual_v2_11_d[i] = v2_11_manual_tokens[2]
            if len(v2_11_manual_tokens) > original_tokens_len - i:
                v2_11_manual_tokens = v2_11_manual_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_11_manual_token = match_manual_v2_11_d[i]
            if token == v2_11_manual_token:
                comparison_d[sent_id]['v2.11 manual']['correct'] += 1
            comparison_d[sent_id]['v2.11 manual']['all'] += 1

        with open(os.path.join(THIS_DIR, 'manual_llm_comparison-tokens-{}-{}.json'.format(model, args.note)), 'w', encoding='utf-8') as f:
            json.dump(comparison_d, f, ensure_ascii=False, indent=4)

        # v2_8_annotation = {}
        # token_idx = 0
        # in_split = -1
        # for line in v2_8_table.split('\n'):
        #     fields = line.split('\t')
        #     id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
        #     if feats_t != '_':
        #         feat_l = feats_t.split('|')
        #         for feat in feat_l:
        #             if feat not in v2_8_feat_count_d:
        #                 v2_8_feat_count_d[feat] = 0
        #             v2_8_feat_count_d[feat] += 1
        #     if '-' in id_t:
        #         in_split = 0
        #         continue
        #     while 1:
        #         if token_idx < len(v2_8_llm_tokens) - 1 and fuzz.ratio(form_t, v2_8_llm_tokens[token_idx + 1]) > fuzz.ratio(form_t, v2_8_llm_tokens[token_idx]):
        #             token_idx += 1
        #         elif token_idx - 1 > -1 and token_idx < len(v2_8_llm_tokens) and fuzz.ratio(form_t, v2_8_llm_tokens[token_idx - 1]) > fuzz.ratio(form_t, v2_8_llm_tokens[token_idx]):
        #             token_idx -= 1
        #         else:
        #             break
        #     if sent_id in v2_8_mismatches and token_idx in v2_8_mismatches[sent_id]:
        #         if feats_t == '_':
        #             continue
        #         feat_l = feats_t.split('|')
        #         for feat in feat_l:
        #             if feat not in v2_8_error_feat_count_d:
        #                 v2_8_error_feat_count_d[feat] = {'mismatch_count': 0}
        #             v2_8_error_feat_count_d[feat]['mismatch_count'] += 1
        #     v2_8_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
        #     if 'SpaceAfter=No' in misc_t:
        #         v2_8_annotation[id_t]['space_after'] = False
        #     for key in comparison_d:
        #         if comparison_d[key]['idx_8'] == token_idx:
        #             if 'v2.8 feats' not in comparison_d[key]:
        #                 comparison_d[key]['v2.8 feats'] = ''
        #             if comparison_d[key]['v2.8 feats'] != '' and feats_t != '_':
        #                 comparison_d[key]['v2.8 feats'] += '|'
        #                 comparison_d[key]['v2.8 feats'] += feats_t
        #             elif comparison_d[key]['v2.8 feats'] == '' and feats_t != '_':
        #                 comparison_d[key]['v2.8 feats'] = feats_t
        #             break
        #     if in_split == 0:
        #         in_split = 1
        #         for key in comparison_d:
        #             if comparison_d[key]['idx_8'] == token_idx:
        #                 comparison_d[key]['split'] = True
        #                 break
        #     elif in_split == 1:
        #         token_idx += 1
        #         in_split = -1
        #     elif in_split == -1:
        #         token_idx += 1

        # v2_11_annotation = {}
        # token_idx = 0
        # in_split = -1
        # for line in v2_11_table.split('\n'):
        #     fields = line.split('\t')
        #     id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
        #     if feats_t != '_':
        #         feat_l = feats_t.split('|')
        #         for feat in feat_l:
        #             if feat not in v2_11_feat_count_d:
        #                 v2_11_feat_count_d[feat] = 0
        #             v2_11_feat_count_d[feat] += 1
        #     if '-' in id_t:
        #         in_split = 0
        #         continue
        #     while 1:
        #         if token_idx < len(v2_11_llm_tokens) - 1 and fuzz.ratio(form_t, v2_11_llm_tokens[token_idx + 1]) > fuzz.ratio(form_t, v2_11_llm_tokens[token_idx]):
        #             token_idx += 1
        #         elif token_idx - 1 > -1 and token_idx < len(v2_11_llm_tokens) and fuzz.ratio(form_t, v2_11_llm_tokens[token_idx - 1]) > fuzz.ratio(form_t, v2_11_llm_tokens[token_idx]):
        #             token_idx -= 1
        #         else:
        #             break
        #     if sent_id in v2_11_mismatches and token_idx in v2_11_mismatches[sent_id]:
        #         if feats_t == '_':
        #             continue
        #         feat_l = feats_t.split('|')
        #         for feat in feat_l:
        #             if feat not in v2_11_error_feat_count_d:
        #                 v2_11_error_feat_count_d[feat] = {'mismatch_count': 0}
        #             v2_11_error_feat_count_d[feat]['mismatch_count'] += 1
        #     v2_11_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
        #     if 'SpaceAfter=No' in misc_t:
        #         v2_11_annotation[id_t]['space_after'] = False
        #     for key in comparison_d:
        #         if comparison_d[key]['idx_11'] == token_idx:
        #             if 'v2.11 feats' not in comparison_d[key]:
        #                 comparison_d[key]['v2.11 feats'] = ''
        #             if comparison_d[key]['v2.11 feats'] != '' and feats_t != '_':
        #                 comparison_d[key]['v2.11 feats'] += '|'
        #                 comparison_d[key]['v2.11 feats'] += feats_t
        #             elif comparison_d[key]['v2.11 feats'] == '' and feats_t != '_':
        #                 comparison_d[key]['v2.11 feats'] = feats_t
        #             break
        #     if in_split == 0:
        #         in_split = 1
        #         for key in comparison_d:
        #             if comparison_d[key]['idx_11'] == token_idx:
        #                 comparison_d[key]['split'] = True
        #                 break
        #     elif in_split == 1:
        #         in_split = -1
        #     elif in_split == -1:
        #         token_idx += 1

        # for key in comparison_d:
        #     if 'split' not in comparison_d[key]:
        #         comparison_d[key]['split'] = False
        #     comparison_d[key]['token'] = original_tokens[key]
        #     comparison_d[key]['v2.8 token'] = v2_8_llm_tokens[comparison_d[key]['idx_8']]
        #     comparison_d[key]['v2.11 token'] = v2_11_llm_tokens[comparison_d[key]['idx_11']]

        # analysis_d['sentences'][sent_id] = comparison_d

    # analysis_d['feats'] = {'increase': {}, 'decrease': {}}
    # for sent_id in analysis_d['sentences'].keys():
    #     ids = list(analysis_d['sentences'][sent_id].keys())
    #     for id_t in ids:
    #         el = analysis_d['sentences'][sent_id][id_t]
    #         v2_8, v2_11 = el['v2.8'], el['v2.11']
    #         if 'v2.8 feats' not in el or 'v2.11 feats' not in el:
    #             continue
    #         feats8, feats11 = el['v2.8 feats'], el['v2.11 feats']
    #         feat_l_8, feat_l_11 = feats8.split('|'), feats11.split('|')
    #         feat_d_8, feat_d_11 = {}, {}
    #         for feat in feat_l_8:
    #             if feat != '':
    #                 tag, value = feat.split('=')
    #                 feat_d_8[tag] = value
    #         tag_s = set(feat_d_8.keys())
    #         for feat in feat_l_11:
    #             if feat != '':
    #                 tag, value = feat.split('=')
    #                 feat_d_11[tag] = value
    #         tag_s.update(feat_d_11.keys())
    #         if v2_8 == 0 and v2_11 == 1:
    #             for tag in tag_s:
    #                 if tag not in feat_d_8:
    #                     tup = ('add', '{}={}'.format(tag, feat_d_11[tag]))
    #                 elif tag not in feat_d_11:
    #                     tup = ('remove', '{}={}'.format(tag, feat_d_8[tag]))
    #                 elif feat_d_8[tag] != feat_d_11[tag]:
    #                     tup = ('change', '{}={}'.format(tag, feat_d_8[tag]), '{}={}'.format(tag, feat_d_11[tag]))
    #                 else:
    #                     continue
    #                 if tup not in analysis_d['feats']['increase']:
    #                     analysis_d['feats']['increase'][tup] = 0
    #                 analysis_d['feats']['increase'][tup] += 1
    #         elif v2_8 == 1 and v2_11 == 0:
    #             for tag in tag_s:
    #                 if tag not in feat_d_8:
    #                     tup = ('remove', '{}={}'.format(tag, feat_d_11[tag]))
    #                 elif tag not in feat_d_11:
    #                     tup = ('add', '{}={}'.format(tag, feat_d_8[tag]))
    #                 elif feat_d_8[tag] != feat_d_11[tag]:
    #                     tup = ('change', '{}={}'.format(tag, feat_d_11[tag]), '{}={}'.format(tag, feat_d_8[tag]))
    #                 else:
    #                     continue
    #                 if tup not in analysis_d['feats']['decrease']:
    #                     analysis_d['feats']['decrease'][tup] = 0
    #                 analysis_d['feats']['decrease'][tup] += 1

    # increase_d = analysis_d['feats']['increase'].copy()
    # keys = list(increase_d.keys())
    # keys.sort(key=lambda x: increase_d[x], reverse=True)
    # analysis_d['feats']['increase'] = []
    # for key in keys:
    #     analysis_d['feats']['increase'].append({'tuple': list(key), 'count': increase_d[key]})
    # decrease_d = analysis_d['feats']['decrease'].copy()
    # keys = list(decrease_d.keys())
    # keys.sort(key=lambda x: decrease_d[x], reverse=True)
    # analysis_d['feats']['decrease'] = []
    # for key in keys:
    #     analysis_d['feats']['decrease'].append({'tuple': list(key), 'count': decrease_d[key]})


if __name__ == '__main__':
    main()
