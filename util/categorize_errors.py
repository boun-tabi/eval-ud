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
if not conllu_filepath.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
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
    error_folder = os.path.join(os.path.dirname(conllu_filepath), 'errors')
if not os.path.exists(error_folder):
    os.mkdir(error_folder)
treebank_error_folder = os.path.join(
    error_folder, os.path.basename(conllu_filepath).replace('.conllu', ''))
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
error_d = dict()
for err_type in error_types:
    error_d[err_type] = 0
    disregard_d[err_type] = 0
for line in lines:
    for err_type in error_types:
        if err_type in line:
            for dr in disregard_l:
                if dr in line:
                    include = False
                    break
            if include:
                error_d[err_type] += 1
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

print('{tb_title}'.format(tb_title=os.path.basename(conllu_filepath)))
print('\tError counts by error types:')
for err_type in error_types:
    if error_d[err_type] > 1: # > 1 due to lines like 'Syntax errors: \d+'
        print('\t\t{err_type}: {err_c}'.format(err_type=err_type, err_c=error_d[err_type]-1)) # -1 due to lines like 'Syntax errors: \d+'
print('\t\tAll: {all}'.format(all=sum([error_d[key] for key in error_d.keys()]) - len([i for i in error_d.keys() if error_d[i] != 0]))) # -len(error_d.keys()) due to lines like 'Format errors: \d+'
print('\tDisregarded line counts by error types:')
for err_type in error_types:
    if disregard_d[err_type] != 0:
        print('\t\t{err_type}: {dr_c}'.format(err_type=err_type, dr_c=disregard_d[err_type]))
print('\t\tAll: {all}'.format(all=sum([disregard_d[key] for key in disregard_d.keys()])))
