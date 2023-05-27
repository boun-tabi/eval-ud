import os
import argparse
import re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--type', action="store", required=True)
parser.add_argument('--conllu', action="store", required=True)
args = parser.parse_args()

if args.type == 'folder':
    conllu_folderpath = args.conllu
    conllu_filepath_l = [os.path.join(conllu_folderpath, i) for i in os.listdir(conllu_folderpath)]
else:
    conllu_filepath_l = [args.conllu]

metadata_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n'
tb_d = dict()
error_l = ['doesn\'t end with a sentence ending, . ! ? " ”', 'odd number of normal quotation, "', 'unmatched parentheses, ( )', 'unmatched fancy quotation, “ ”']
sent_endings = ['.', '!', '?', '"', '”']
for file in conllu_filepath_l:
    with open(file, 'r', encoding='utf-8') as f:
        tb = f.read()
    tb_name = os.path.basename(file)
    metadata = re.findall(metadata_pattern, tb)
    tb_d[tb_name] = {'errors': {'count': 0}, 'sent_count': len(metadata)}
    for err_type in error_l:
        tb_d[tb_name]['errors'][err_type] = 0
    error_count = 0
    for sent_id, text in metadata:
        segm_error = False
        if text[-1] not in sent_endings:
            tb_d[tb_name]['errors'][error_l[0]] += 1
            segm_error = True
        if text.count('"') % 2 == 1:
            tb_d[tb_name]['errors'][error_l[1]] += 1
            segm_error = True
        if text.count('(') != text.count(')'):
            tb_d[tb_name]['errors'][error_l[2]] += 1
            segm_error = True
        if text.count('“') != text.count('”'):
            tb_d[tb_name]['errors'][error_l[3]] += 1
            segm_error = True
        if segm_error:
            error_count += 1
    tb_d[tb_name]['errors']['count'] = error_count

for tb in tb_d.keys():
    print('{tb}'.format(tb=tb))
    print('\tSentence count: {count}'.format(count=tb_d[tb]['sent_count']))
    print('\tSegmentation errors: {count}'.format(count=tb_d[tb]['errors']['count']))
    for err in [i for i in tb_d[tb]['errors'].keys() if i != 'count']:
        print('\t\t{type}: {count}'.format(type=err, count=tb_d[tb]['errors'][err]))