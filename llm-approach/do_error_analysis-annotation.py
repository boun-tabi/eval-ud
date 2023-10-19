import os, argparse, json

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

    analysis_d = {'sentences': {}}
    for sent_id, value in results.items():
        v2_8_table, v2_11_table = tb8[sent_id]['table'], tb11[sent_id]['table']
        v2_8_annotation = {}
        for line in v2_8_table.split('\n'):
            fields = line.split('\t')
            id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
            v2_8_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_8_annotation[id_t]['space_after'] = False

        v2_11_annotation = {}
        for line in v2_11_table.split('\n'):
            fields = line.split('\t')
            id_t, form_t, feats_t, misc_t = fields[0], fields[1], fields[5], fields[9]
            v2_11_annotation[id_t] = {'form': form_t, 'space_after': True, 'feats': feats_t}
            if 'SpaceAfter=No' in misc_t:
                v2_11_annotation[id_t]['space_after'] = False

        ratio_v2_8, ratio_v2_11 = value['v2.8 ratio'], value['v2.11 ratio']
        original_text, text_v2_8, text_v2_11 = value['original text'], value['v2.8 text'], value['v2.11 text']

        id_cursor8, id_cursor11 = 1, 1
        for token in original_text.split(' '):
            if '{}-{}'.format(id_cursor8, id_cursor8 + 1) in v2_8_annotation.keys():
                feats1_str = v2_8_annotation[id_cursor8]['feats']
                feats1_d = {}
                for feat in feats1_str.split('|'):
                    feat_k, feat_v = feat.split('=')
                    feats1_d[feat_k] = feat_v
                feats2_str = v2_8_annotation[id_cursor8 + 1]['feats']
                feats2_d = {}
                for feat in feats2_str.split('|'):
                    feat_k, feat_v = feat.split('=')
                    feats2_d[feat_k] = feat_v
                feats1_set = set(feats1_d.keys())
                key_l = feats1_set.union(set(feats2_d.keys()))
                if len(key_l) != len(feats1_set) + len(feats2_d.keys()):
                    print('Error in annotation')
                    input()
                id_cursor8 += 1
            if '{}-{}'.format(id_cursor11, id_cursor11 + 1) in v2_11_annotation.keys():
                feats1 = v2_11_annotation[id_cursor11]['feats']
                feats2 = v2_11_annotation[id_cursor11 + 1]['feats']
                id_cursor11 += 1
            id_cursor8 += 1
            id_cursor11 += 1

        diff = ratio_v2_11 - ratio_v2_8
        d = {'diff': diff, 'original_text': original_text, 'text_v2_8': text_v2_8, 'text_v2_11': text_v2_11}
        analysis_d['sentences'][sent_id] = d

    with open(os.path.join(THIS_DIR, 'error_analysis-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()