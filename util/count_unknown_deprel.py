import re
import os
import subprocess
import sys
import argparse

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

pattern = "Unknown DEPREL label: '(.*?)'"
deprel_l = re.findall(pattern, output)
deprel_d = dict()
for label in deprel_l:
    if label in deprel_d.keys():
        deprel_d[label] += 1
    else:
        deprel_d[label] = 1
print(deprel_d)
# tr_boun_v2-dev.conllu : {'obl:tmp': 10, 'advcl:cond': 27, 'dep:der': 34}
# tr_boun_v2-test.conllu : {'advcl:cond': 34, 'dep:der': 18, 'obl:tmp': 6, 'compound:red': 1}
# tr_boun_v2-train.conllu : {'dep:der': 520, 'advcl:cond': 56, 'obl:cl': 22, 'discourse:q': 217, 'obl:comp': 5, 'discourse:tag': 2, 'obl:tmp': 106, 'compund:redup': 1, 'advl': 1, 'nsbuj': 1, 'bol': 1, 'compoun': 1, 'cconj': 1, 'discouse': 1, 'subj': 1, 'nmof': 1}
