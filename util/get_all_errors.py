import os
import subprocess
import sys
import argparse
import json

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--treebank', action="store", required=True)
parser.add_argument('--errors', action="store")
parser.add_argument('--ud-validation', action="store")
args = parser.parse_args()

treebank_folderpath = args.treebank
conllu_dev_filepath = os.path.join(
    treebank_folderpath, '{tb_title}-dev.conllu'.format(tb_title=os.path.basename(treebank_folderpath)))
conllu_test_filepath = os.path.join(
    treebank_folderpath, '{tb_title}-test.conllu'.format(tb_title=os.path.basename(treebank_folderpath)))
conllu_train_filepath = os.path.join(
    treebank_folderpath, '{tb_title}-train.conllu'.format(tb_title=os.path.basename(treebank_folderpath)))
if not conllu_dev_filepath.endswith('.conllu') or not conllu_test_filepath.endswith('.conllu') or not conllu_train_filepath.endswith('.conllu'):
    print('At least one of the conllu files does not have the appropriate extension')
home = os.path.expanduser('~')
python_script = sys.executable
if args.ud_validation:
    validation_script = args.ud_validation
else:
    validation_script = os.path.join(THIS_DIR, 'validate.py')
    if not os.path.exists(validation_script):
        print("You did not use the 'ud-validation' flag for the validation script's path and it doesn't exist in the 'util' folder either. Aborting.")
        exit()
lang = 'tr'
with open(conllu_dev_filepath, 'r', encoding='utf-8') as f:
    tb_dev = f.read()
dev_sent_count = tb_dev.count('\n\n')
print('Sentence count in dev: {dev_count}'.format(dev_count=dev_sent_count))
with open(conllu_test_filepath, 'r', encoding='utf-8') as f:
    tb_test = f.read()
test_sent_count = tb_test.count('\n\n')
print('Sentence count in test: {test_count}'.format(
    test_count=test_sent_count))
with open(conllu_train_filepath, 'r', encoding='utf-8') as f:
    tb_train = f.read()
train_sent_count = tb_train.count('\n\n')
print('Sentence count in train: {train_count}'.format(
    train_count=train_sent_count))
print('All the sentences added: {all_count}'.format(
    all_count=dev_sent_count+test_sent_count+train_sent_count))
entire_treebank_filepath = os.path.join(
    treebank_folderpath, '{tb_title}-entire.conllu'.format(tb_title=os.path.basename(treebank_folderpath)))
with open(entire_treebank_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(tb_dev)
    f.write(tb_test)
    f.write(tb_train)

output = subprocess.run([python_script, validation_script,
                        f'--lang={lang}', '--max-err=0', entire_treebank_filepath], capture_output=True, text=True).stderr
if args.errors:
    error_folder = args.errors
else:
    error_folder = os.path.join(THIS_DIR, 'Errors')
if not os.path.exists(error_folder):
    os.mkdir(error_folder)
treebank_error_folder = os.path.join(error_folder, os.path.basename(
    entire_treebank_filepath).replace('.conllu', ''))
if not os.path.exists(treebank_error_folder):
    os.mkdir(treebank_error_folder)
with open(os.path.join(treebank_error_folder, 'All.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(output)

lines = output.splitlines()
error_types = ['Metadata', 'Syntax', 'Morpho', 'Format', 'Enhanced']
disregard_l = list()
with open(os.path.join(THIS_DIR, 'disregard_list.json'), 'r', encoding='utf-8') as f:
    disregard_d = json.load(f)
for key in disregard_d.keys():
    for label in disregard_d[key]['labels']:
        disregard_l.append(label)
lines_d = dict()
for err_type in error_types:
    lines_d[err_type] = list()
include = True
disregard_d = dict()
for err_type in error_types:
    disregard_d[err_type] = 0
for line in lines:
    for err_type in error_types:
        if err_type in line:
            for dr in disregard_l:
                if dr in line:
                    include = False
                    break
            if include:
                lines_d[err_type].append(line)
            else:
                disregard_d[err_type] += 1
            break
    include = True

for err_type in error_types:
    err_txt_path = os.path.join(treebank_error_folder, f'{err_type}.txt')
    if len(lines_d[err_type]) == 0:
        if os.path.exists(err_txt_path):
            os.remove(err_txt_path)
        continue
    with open(err_txt_path, 'w', encoding='utf-8', newline='\n') as f:
        for line in lines_d[err_type]:
            f.write(f'{line}\n')

print('Disregarded line counts by error types in {tb_title}:'.format(tb_title=os.path.basename(entire_treebank_filepath)))
for err_type in error_types:
    if disregard_d[err_type] != 0:
        print('\t{err_type}: {dr_c}'.format(err_type=err_type, dr_c=disregard_d[err_type]))
print('\tAll: {all}'.format(all=sum([disregard_d[key] for key in disregard_d.keys()])))
