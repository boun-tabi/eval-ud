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
text_pattern = '# text = (.*)'
text_d = dict()
dups = dict()
for type_t in file_types:
    conllu_filepath = conllu_file_d[type_t]
    with open(conllu_filepath, 'r', encoding='utf-8') as f:
        tb = f.read()
    sent_ids_t = re.findall(text_pattern, tb)
    for id_t in sent_ids_t:
        if id_t in text_d.keys():
            dups[id_t] = [type_t, text_d[id_t][0]]
            text_d[id_t] = [type_t, text_d[id_t][0]]
        else:
            text_d[id_t] = [type_t]
for key in dups.keys():
    print('text:', key, 'files:', dups[key])
print(len(dups.keys()))