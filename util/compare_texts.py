import os
import argparse
import re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu1', action="store", required=True)
parser.add_argument('--conllu2', action="store", required=True)
args = parser.parse_args()

conllu1_filepath = args.conllu1
conllu2_filepath = args.conllu2
if not conllu1_filepath.endswith('.conllu') or not conllu2_filepath.endswith('.conllu'):
    print('At least one of the conllu files does not have the appropriate extension')
home = os.path.expanduser('~')
metadata_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n'
with open(conllu1_filepath, 'r', encoding='utf-8') as f:
    tb1 = f.read()
with open(conllu2_filepath, 'r', encoding='utf-8') as f:
    tb2 = f.read()
tb1_md = re.findall(metadata_pattern, tb1)
tb1_d = dict()
for md in tb1_md:
    sent_id, text = md
    if sent_id in tb1_d.keys():
        print('duplicate sent_id', sent_id)
    else:
        tb1_d[sent_id] = text
tb2_md = re.findall(metadata_pattern, tb2)
tb2_d = dict()
for md in tb2_md:
    sent_id, text = md
    if sent_id in tb2_d.keys():
        print('duplicate sent_id', sent_id)
    else:
        tb2_d[sent_id] = text
if len(tb1_d.keys()) != len(tb2_d.keys()):
    print('not same amount of keys')
# diff_text_count = 0
# for sent_id in tb1_d.keys():
#     if tb1_d[sent_id] != tb2_d[sent_id]:
#         print(tb1_d[sent_id])
#         print(tb2_d[sent_id])
#         print()
#         input()
#         diff_text_count += 1
#         # print('text different')
# print(diff_text_count) # dev: 41; test: 38; train: 19
new_tb2 = ''
sent_id_pattern = '# sent_id = (.*)'
text_pattern = '# text = (.*)'
sent_id = ''
for line in tb2.split('\n'):
    sent_id_search = re.search(sent_id_pattern, line)
    text_search = re.search(text_pattern, line)
    if sent_id_search:
        sent_id = sent_id_search.group(1)
        new_tb2 += line
    elif text_search:
        text = text_search.group(1)
        if tb1_d[sent_id] != text:
            new_tb2 += '# text = {text}'.format(text=tb1_d[sent_id])
        else:
            new_tb2 += line
    else:
        new_tb2 += line
    new_tb2 += '\n'
with open(args.conllu2, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb2)
