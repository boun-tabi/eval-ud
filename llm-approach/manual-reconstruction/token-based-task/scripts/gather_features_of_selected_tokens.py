import argparse, json, os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t8', '--treebank8', required=True, help='Path to treebank v2.8')
    parser.add_argument('-t11', '--treebank11', required=True, help='Path to treebank v2.11')
    parser.add_argument('-t', '--tokens', required=True, help='Path to the file containing the tokens')
    return parser.parse_args()

def check_features(table, token_ids):
    out_d = {id_t: {'has_conv': False, 'has_ptcp': False, 'has_advcl': False, 'has_acl': False, 'has_ccomp': False} for id_t in token_ids}
    for line in table.split('\n'):
        fields = line.split('\t')
        id_t = fields[0]
        if id_t not in token_ids:
            continue
        feats_t, deprel_t = fields[5], fields[7]
        feats_l = feats_t.split('|')
        for feat_t in feats_l:
            if feat_t == 'VerbForm=Conv':
                out_d[id_t]['has_conv'] = True
            elif feat_t == 'VerbForm=Part':
                out_d[id_t]['has_ptcp'] = True
        if deprel_t == 'advcl':
            out_d[id_t]['has_advcl'] = True
        elif deprel_t == 'acl':
            out_d[id_t]['has_acl'] = True
        elif deprel_t == 'ccomp':
            out_d[id_t]['has_ccomp'] = True
    return out_d

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    args = get_args()

    with open(args.treebank8, 'r') as f:
        treebank8 = json.load(f)

    with open(args.treebank11, 'r') as f:
        treebank11 = json.load(f)

    with open(args.tokens, 'r') as f:
        tokens = json.load(f)

    features = {'v2.8': {}, 'v2.11': {}}
    for sent_id in tokens.keys():
        features['v2.8'][sent_id], features['v2.11'][sent_id] = {}, {}
        token_l = tokens[sent_id]
        table8, table11 = treebank8[sent_id]['table'], treebank11[sent_id]['table']
        features['v2.8'][sent_id] = check_features(table8, token_l['v2.8'])
        features['v2.11'][sent_id] = check_features(table11, token_l['v2.11'])

    with open(os.path.join(THIS_DIR, 'features-gathered-of-selected-tokens.json'), 'w') as f:
        json.dump(features, f, indent=4)


if __name__ == '__main__':
    main()
