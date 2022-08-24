import os, re
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
treebank_name = 'tr_boun-ud'
folder = f'{THIS_DIR}/UD_Turkish-BOUN'
files = ['tr_boun-ud-train.conllu', 'tr_boun-ud-dev.conllu', 'tr_boun-ud-test.conllu']
source_column = 5
cats_pattern = r'(?:.+\t){5}(.+)\t(?:.+\t){3}.+'
feats_set = set()
for file in files:
    with open(f'{folder}/{file}', 'r', encoding='utf-8') as f:
        content = f.read()
    lines = re.findall(cats_pattern, content)
    for l in lines:
        # feat_l = l.split('|')
        # for feat_t in feat_l:
        feats_set.add(l)
with open(f'{THIS_DIR}/{treebank_name}.vocab', 'w', encoding='utf-8') as f:
    for feat_t in feats_set:
        f.write(feat_t + '\n')