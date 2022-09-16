import os
import subprocess
import sys
import argparse
import json

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
parser.add_argument('--errors', action="store")
parser.add_argument('--ud-validation', action="store")
args = parser.parse_args()

conllu_filepath = args.conllu
conllu_filename = os.path.split(conllu_filepath)[-1]
if not conllu_filename.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
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
output = subprocess.run([python_script, validation_script,
                        f'--lang={lang}', '--max-err=0', conllu_filepath], capture_output=True, text=True).stderr
if args.errors:
    error_folder = args.errors
else:
    error_folder = os.path.join(THIS_DIR, 'Errors')
if not os.path.exists(error_folder):
    os.mkdir(error_folder)
conllu_filename_without_ext = conllu_filename.replace('.conllu', '')
treebank_error_folder = os.path.join(error_folder, conllu_filename_without_ext)
if not os.path.exists(treebank_error_folder):
    os.mkdir(treebank_error_folder)
with open(os.path.join(treebank_error_folder, 'All.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(output)

lines = output.splitlines()
error_types = ['Metadata', 'Syntax', 'Morpho', 'Format', 'Enhanced']
disregard_l = []
with open(os.path.join(THIS_DIR, 'disregard_list.json'), 'r', encoding='utf-8') as f:
    disregard_d = json.load(f)
for key in disregard_d.keys():
    for label in disregard_d[key]['labels']:
        disregard_l.append(label)
lines_d = dict()
for err_type in error_types:
    lines_d[err_type] = []
include = True
disregard_count = 0
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
                disregard_count += 1
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
print('Disregarded lines: {dr_c}'.format(dr_c=disregard_count))
