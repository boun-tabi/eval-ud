import os, json, argparse
from difflib import SequenceMatcher

THIS_DIR = os.path.dirname(os.path.abspath(__file__)) # util
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True)
parser.add_argument('-s', type=str, required=True)
args = parser.parse_args()

first_path = args.f
with open(first_path, 'r', encoding='utf-8') as f:
    first_data = json.load(f)
f_d = {}
for el in first_data:
    f_d[el['sent_id']] = el['table']
second_path = args.s
with open(second_path, 'r', encoding='utf-8') as f:
    second_data = json.load(f)
s_d = {}
for el in second_data:
    s_d[el['sent_id']] = el['table']
sent_ids = list(set(f_d.keys()).union(set(s_d.keys())))
len_sent_ids = len(sent_ids)
change_d = {}
split_included = False
similarity_type = 'exact matches among form, lemma, upos and feats strings ; 1 means identical, 0 means completely different ; sentences without splits and with same number of rows'
small_tag = 'exact_match-upos_feats-no_split'
for i, sent_id in enumerate(sent_ids):
    table1, table2 = f_d[sent_id], s_d[sent_id]
    l1, l2 = [], []
    split_found = False
    all_count, change_count = 0, 0
    for el in table1.split('\n'):
        if el.startswith('#'):
            continue
        fields = el.split('\t')
        if len(fields) == 10:
            if '-' in fields[0]:
                split_found = True
                if not split_included:
                    break
            l1.append((fields[1], fields[2], fields[3], fields[5]))
    if split_found and not split_included:
        continue
    for el in table2.split('\n'):
        if el.startswith('#'):
            continue
        fields = el.split('\t')
        if len(fields) == 10:
            if '-' in fields[0]:
                split_found = True
                if not split_included:
                    break
            l2.append((fields[1], fields[2], fields[3], fields[5]))
    if split_found and not split_included:
        continue
    if len(l1) != len(l2):
        continue
    for row in range(len(l1)):
        form1, lemma1, upos1, feats1 = l1[row]
        form2, lemma2, upos2, feats2 = l2[row]
        if form1 != form2:
            change_count += 1
        if lemma1 != lemma2:
            change_count += 1
        if upos1 != upos2:
            change_count += 1
        if feats1 != feats2:
            change_count += 1
        all_count += 4
    change_d[sent_id] = change_count / all_count
    if i % 1000 == 0:
        print('Remaining: {} / {}'.format(len_sent_ids - i, len_sent_ids))
# sort dict
change_d = {'similarity_type': similarity_type, 'ratios': {k: v for k, v in sorted(change_d.items(), key=lambda item: item[1], reverse=True)}}
with open(os.path.join(THIS_DIR, 'different_annotations-{}.json'.format(small_tag)), 'w', encoding='utf-8') as f:
    json.dump(change_d, f, ensure_ascii=False, indent=4)