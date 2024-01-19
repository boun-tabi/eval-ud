# scratched...

import argparse, json, os, random

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--features', required=True, help='Path to the file containing the features')
    return parser.parse_args()

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    args = get_args()

    with open(args.features, 'r') as f:
        features = json.load(f)

    feat_count_per_sent = {'conv': 0, 'ptcp': 0, 'advcl': 0, 'acl': 0, 'ccomp': 0}
    sent_ids = list(features['v2.8'].keys())
    random.shuffle(sent_ids)
    normal_l, dep_l = [], []
    last_added = None
    sent_ids_added = []
    for sent_id in sent_ids:
        keys8, keys11 = features['v2.8'][sent_id].keys(), features['v2.11'][sent_id].keys()
        for id8, id11 in zip(keys8, keys11):
            if features['v2.8'][sent_id][id8]['has_conv'] or features['v2.11'][sent_id][id11]['has_conv'] or features['v2.8'][sent_id][id8]['has_ptcp'] or features['v2.11'][sent_id][id11]['has_ptcp'] or features['v2.8'][sent_id][id8]['has_advcl'] or features['v2.11'][sent_id][id11]['has_advcl'] or features['v2.8'][sent_id][id8]['has_acl'] or features['v2.11'][sent_id][id11]['has_acl'] or features['v2.8'][sent_id][id8]['has_ccomp'] or features['v2.11'][sent_id][id11]['has_ccomp']:
                if last_added == 'dep':
                    normal_l.append({'sent_id': sent_id, 'id8': id8, 'id11': id11})
                else:
                    dep_l.append({'sent_id': sent_id, 'id8': id8, 'id11': id11})
                    last_added = 'dep'
                sent_ids_added.append(sent_id)
    rem_ids = list(set(sent_ids) - set(sent_ids_added))
    random.shuffle(rem_ids)
    for i, sent_id in enumerate(rem_ids):
        if i % 2 == 0:
            normal_l.append(sent_id)
        else:
            dep_l.append(sent_id)
    print('Normal:', len(normal_l))
    print('Dep:', len(dep_l))

    for sent_id in sent_ids:
        keys8, keys11 = features['v2.8'][sent_id].keys(), features['v2.11'][sent_id].keys()
        for id8, id11 in zip(keys8, keys11):
            if features['v2.8'][sent_id][id8]['has_conv'] or features['v2.11'][sent_id][id11]['has_conv']:
                feat_count_per_sent['conv'] += 1
            if features['v2.8'][sent_id][id8]['has_ptcp'] or features['v2.11'][sent_id][id11]['has_ptcp']:
                feat_count_per_sent['ptcp'] += 1
            if features['v2.8'][sent_id][id8]['has_advcl'] or features['v2.11'][sent_id][id11]['has_advcl']:
                feat_count_per_sent['advcl'] += 1
            if features['v2.8'][sent_id][id8]['has_acl'] or features['v2.11'][sent_id][id11]['has_acl']:
                feat_count_per_sent['acl'] += 1
            if features['v2.8'][sent_id][id8]['has_ccomp'] or features['v2.11'][sent_id][id11]['has_ccomp']:
                feat_count_per_sent['ccomp'] += 1
    print('feat_count_per_sent:', feat_count_per_sent)
    for version in features.keys():
        count_d = {'has_conv': 0, 'has_ptcp': 0, 'has_advcl': 0, 'has_acl': 0, 'has_ccomp': 0}
        for sent_id in features[version].keys():
            for id_t in features[version][sent_id].keys():
                for feat in count_d.keys():
                    if features[version][sent_id][id_t][feat]:
                        count_d[feat] += 1
        print('Version:', version)
        token_count = 0
        for sent_id in features[version].keys():
            token_count += len(features[version][sent_id].keys())
        print('Token count:', token_count)
        print('count_d:', count_d)
        print('Feature count:', sum(count_d.values()))
        print()

if __name__ == '__main__':
    main()
