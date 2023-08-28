import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument('-t1', '--treebank-1', type=str, required=True)
parser.add_argument('-t2', '--treebank-2', type=str, required=True)
args = parser.parse_args()

with open(args.treebank_1, 'r', encoding='utf-8') as f:
    treebank_1 = json.load(f)
t1_d = {sent['sent_id']: {'text': sent['text'], 'table': sent['table']} for sent in treebank_1}
with open(args.treebank_2, 'r', encoding='utf-8') as f:
    treebank_2 = json.load(f)
t2_d = {sent['sent_id']: {'text': sent['text'], 'table': sent['table']} for sent in treebank_2}

sent_ids = set(t1_d.keys()) & set(t2_d.keys())
for sent_id in sent_ids:
    t1_split, t2_split = False, False
    for token in t1_d[sent_id]['table'].split('\n'):
        fields = token.split('\t')
        id_t = fields[0]
        if '-' in id_t:
            t1_split = True
            break
    for token in t2_d[sent_id]['table'].split('\n'):
        fields = token.split('\t')
        id_t = fields[0]
        if '-' in id_t:
            t2_split = True
            break
    if (t1_split and not t2_split) or (not t1_split and t2_split):
        print(sent_id)
        input()