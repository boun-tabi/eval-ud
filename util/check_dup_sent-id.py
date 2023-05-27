import os
import argparse
import re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--treebank', action="store", required=True)
args = parser.parse_args()

treebank_folderpath = args.treebank
conllu_filepath_l = [os.path.join(treebank_folderpath, i) for i in os.listdir(treebank_folderpath) if i.endswith('.conllu')]
file_types = ['dev', 'test', 'train']
conllu_file_d = {'dev': '', 'test': '', 'train': ''}
for type_t in file_types:
    for f in conllu_filepath_l:
        if type_t in f:
            conllu_file_d[type_t] = f
sent_id_pattern = '# sent_id = (.*)'
sent_ids_d = dict()
dups = dict()
for type_t in file_types:
    conllu_filepath = conllu_file_d[type_t]
    with open(conllu_filepath, 'r', encoding='utf-8') as f:
        tb = f.read()
    sent_ids_t = re.findall(sent_id_pattern, tb)
    for id_t in sent_ids_t:
        if id_t in sent_ids_d.keys():
            dups[id_t] = [type_t, sent_ids_d[id_t][0]]
            sent_ids_d[id_t] = [type_t, sent_ids_d[id_t][0]]
        else:
            sent_ids_d[id_t] = [type_t]
for key in dups.keys():
    print('sent_id:', key, 'files:', dups[key])