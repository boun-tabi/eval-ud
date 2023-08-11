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
function_type = 'SequenceMatcher.ratio'
string_type = 'entire table'
similarity_type = '{} between entire table strings ; 1.0 means identical, 0.0 means completely different'.format(function_type)
for i, sent_id in enumerate(sent_ids):
    table1, table2 = f_d[sent_id], s_d[sent_id]
    ratio = SequenceMatcher(None, table1, table2).ratio()
    change_d[sent_id] = ratio
    if i % 1000 == 0:
        print('Remaining: {} / {}'.format(len_sent_ids - i, len_sent_ids))
# sort dict
change_d = {'similarity_type': similarity_type, 'ratios': {k: v for k, v in sorted(change_d.items(), key=lambda item: item[1], reverse=True)}}
with open(os.path.join(THIS_DIR, 'different_annotations-{}-{}.json'.format(function_type, string_type)), 'w', encoding='utf-8') as f:
    json.dump(change_d, f, ensure_ascii=False, indent=4)