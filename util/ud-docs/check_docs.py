import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
parser.add_argument('-l', '--lang', type=str, required=True)
args = parser.parse_args()

dep_path = os.path.join(THIS_DIR, 'dep-{}.json'.format(args.lang))
with open(dep_path, 'r', encoding='utf-8') as fin:
    dep_data = json.load(fin)
pos_path = os.path.join(THIS_DIR, 'pos-{}.json'.format(args.lang))
with open(pos_path, 'r', encoding='utf-8') as fin:
    pos_data = json.load(fin)
feat_path = os.path.join(THIS_DIR, 'feat-{}.json'.format(args.lang))
with open(feat_path, 'r', encoding='utf-8') as fin:
    feat_data = json.load(fin)

treebank = args.treebank
with open(treebank, 'r', encoding='utf-8') as fin:
    tb_data = json.load(fin)

unknown_pos, unknown_feat, unknown_dep = list(), dict(), list()
for sent_id in tb_data:
    table = tb_data[sent_id]['table']
    rows = table.split('\n')
    for row in rows:
        fields = row.split('\t')
        upos_t, feats_t, dep_t = fields[3], fields[5], fields[7]
        if upos_t != '_' and upos_t not in pos_data and upos_t not in unknown_pos:
            unknown_pos.append(upos_t)
        if dep_t != '_' and dep_t not in dep_data and dep_t not in unknown_dep:
            unknown_dep.append(dep_t)
        if feats_t != '_':
            feat_l = feats_t.split('|')
            for feat in feat_l:
                tag, value = feat.split('=')
                if tag not in feat_data:
                    if tag not in unknown_feat:
                        unknown_feat[tag] = list()
                    if value not in unknown_feat[tag]:
                        unknown_feat[tag].append(value)
                    print(unknown_feat)
                    input()

unknown_pos_path = os.path.join(THIS_DIR, 'unknown_pos-{}.json'.format(args.lang))
if unknown_pos:
    with open(unknown_pos_path, 'w', encoding='utf-8') as fout:
        json.dump(unknown_pos, fout, ensure_ascii=False, indent=4)
else:
    print('No unknown POS tags found.')
    if os.path.exists(unknown_pos_path):
        os.remove(unknown_pos_path)
unknown_dep_path = os.path.join(THIS_DIR, 'unknown_dep-{}.json'.format(args.lang))
if unknown_dep:
    with open(unknown_dep_path, 'w', encoding='utf-8') as fout:
        json.dump(unknown_dep, fout, ensure_ascii=False, indent=4)
else:
    print('No unknown dependencies found.')
    if os.path.exists(unknown_dep_path):
        os.remove(unknown_dep_path)
unknown_feat_path = os.path.join(THIS_DIR, 'unknown_feat-{}.json'.format(args.lang))
if unknown_feat:
    with open(unknown_feat_path, 'w', encoding='utf-8') as fout:
        json.dump(unknown_feat, fout, ensure_ascii=False, indent=4)
else:
    print('No unknown features found.')
    if os.path.exists(unknown_feat_path):
        os.remove(unknown_feat_path)