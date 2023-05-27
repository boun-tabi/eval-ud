# used to replace sent_ids with original IMST sent_ids
# cmd: python3 util/fill_original_sent-ids.py --imst-treebank ../UD_Turkish-IMST --bimst-treebank tr_bimst-ud
import os
import argparse
import re
import difflib

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--imst-treebank', action="store", required=True)
parser.add_argument('--bimst-treebank', action="store", required=True)
args = parser.parse_args()

imst_folderpath = args.imst_treebank
imst_conllu_filepath_l = [os.path.join(imst_folderpath, i) for i in os.listdir(imst_folderpath) if i.endswith('.conllu')]
imst_d = {'dev': '', 'test': '', 'train': ''}
for f in imst_conllu_filepath_l:
    for key in imst_d.keys():
        if key in f:
            imst_d[key] = f
            break
bimst_folderpath = args.bimst_treebank
bimst_conllu_filepath_l = [os.path.join(bimst_folderpath, i) for i in os.listdir(bimst_folderpath) if i.endswith('.conllu')]
bimst_d = {'dev': '', 'test': '', 'train': ''}
for f in bimst_conllu_filepath_l:
    for key in bimst_d.keys():
        if key in f:
            bimst_d[key] = f
            break
sent_id_pattern = '# sent_id = (.*)'
text_pattern = '# text = (.*)'
metadata_pattern = '# sent_id = (.*)\n# text = (.*)'
file_types = ['dev', 'test', 'train']
metadata_d = dict()
for type_t in file_types:
    with open(imst_d[type_t], 'r', encoding='utf-8') as f:
        imst_tb = f.read()
    metadata_l = re.findall(metadata_pattern, imst_tb)
    for md in metadata_l:
        metadata_d[md[1]] = md[0]
for type_t in file_types:
    with open(bimst_d[type_t], 'r', encoding='utf-8') as f:
        bimst_tb_lines = f.read().split('\n')
    new_tb = ''
    for line in bimst_tb_lines:
        if '# sent_id = ' in line:
            sent_id_search = re.search(sent_id_pattern, line)
            sent_id = sent_id_search.group(1)
        elif '# text = ' in line:
            text_search = re.search(text_pattern, line)
            text = text_search.group(1)
            if text in metadata_d.keys():
                new_tb += '# sent_id = {sent_id}\n# text = {text}\n'.format(sent_id=metadata_d[text], text=text)
            else:
                text_found = False
                for key in metadata_d.keys():
                    diff_count = 0
                    for i, s in enumerate(difflib.ndiff(key, text)):
                        if s[0] in ['+', '-']:
                            diff_count += 1
                    if diff_count < 10:
                        new_tb += '# sent_id = {sent_id}\n# text = {text}\n'.format(sent_id=metadata_d[key], text=text)
                        text_found = True
                        break
                if not text_found:
                    print(sent_id, text)
        else:
            new_tb += '{line}\n'.format(line=line)
    with open(bimst_d[type_t], 'w', encoding='utf-8') as f:
        f.write(new_tb)
