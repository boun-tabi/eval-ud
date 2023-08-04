import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
tr_dep_path = os.path.join(THIS_DIR, 'tr_dep.json')
with open(tr_dep_path, 'r', encoding='utf-8') as fin:
    tr_dep = json.load(fin)
tr_pos_path = os.path.join(THIS_DIR, 'tr_pos.json')
with open(tr_pos_path, 'r', encoding='utf-8') as fin:
    tr_pos = json.load(fin)
tr_feat_path = os.path.join(THIS_DIR, 'tr_feat.json')
with open(tr_feat_path, 'r', encoding='utf-8') as fin:
    tr_feat = json.load(fin)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
args = parser.parse_args()

treebank = args.treebank
with open(treebank, 'r', encoding='utf-8') as fin:
    tb_data = json.load(fin)

unknown_pos, unknown_feat, unknown_dep = list(), dict(), list()
for sent in tb_data:
    table = sent['table']
    rows = table.split('\n')
    for row in rows:
        fields = row.split('\t')
        upos, feats, dep = fields[3], fields[5], fields[7]
        if upos != '_' and upos not in tr_pos and upos not in unknown_pos:
            unknown_pos.append(upos)
        if dep != '_' and dep not in tr_dep and dep not in unknown_dep:
            unknown_dep.append(dep)
        if feats != '_':
            feat_l = feats.split('|')
            for feat in feat_l:
                tag, value = feat.split('=')
                if tag not in tr_feat:
                    if tag not in unknown_feat:
                        unknown_feat[tag] = list()
                    if value not in unknown_feat[tag]:
                        unknown_feat[tag].append(value)

if unknown_pos:
    with open(os.path.join(THIS_DIR, 'unknown_pos.json'), 'w', encoding='utf-8') as fout:
        json.dump(unknown_pos, fout, ensure_ascii=False, indent=4)
if unknown_dep:
    with open(os.path.join(THIS_DIR, 'unknown_dep.json'), 'w', encoding='utf-8') as fout:
        json.dump(unknown_dep, fout, ensure_ascii=False, indent=4)
if unknown_feat:
    with open(os.path.join(THIS_DIR, 'unknown_feat.json'), 'w', encoding='utf-8') as fout:
        json.dump(unknown_feat, fout, ensure_ascii=False, indent=4)