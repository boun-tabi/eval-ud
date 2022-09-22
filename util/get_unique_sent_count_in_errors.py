import os
import subprocess
import sys
import argparse
import re
import json

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
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

lines = output.splitlines()
disregard_l = []
with open(os.path.join(THIS_DIR, 'disregard_list.json'), 'r', encoding='utf-8') as f:
    disregard_d = json.load(f)
for key in disregard_d.keys():
    for label in disregard_d[key]['labels']:
        disregard_l.append(label)
sent_s = set()
include = True
sent_pattern = r'Sent (\w+)'
for line in lines:
    for dr in disregard_l:
        if dr in line:
            include = False
            break
    if include:
        sent_search = re.search(sent_pattern, line)
        if sent_search:
            sent_s.add(sent_search.group(1))
    else:
        include = True
print('Unique count: {unique_count}'.format(unique_count=len(sent_s)))