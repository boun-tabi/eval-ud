import os, subprocess, sys, argparse

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
output = subprocess.run([python_script, validation_script, f'--lang={lang}', '--max-err=0', conllu_filepath], capture_output=True, text=True).stderr
if args.errors:
    error_folder = args.errors
else:
    error_folder = os.path.join(THIS_DIR, 'Errors')
if not os.path.exists(error_folder): os.mkdir(error_folder)
conllu_filename_without_ext = conllu_filename.replace('.conllu', '')
treebank_error_folder = os.path.join(error_folder, conllu_filename_without_ext)
if not os.path.exists(treebank_error_folder): os.mkdir(treebank_error_folder)
with open(os.path.join(treebank_error_folder, 'All.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(output)

lines = output.splitlines()
error_types = ['Metadata', 'Syntax', 'Morpho', 'Format', 'Enhanced']
disregard_l = ["'N/A' is not an auxiliary verb in language [tr]", "'N/A' is not a copula in language [tr]", "'y' is not an auxiliary verb in language [tr]", "'y' is not a copula in language [tr]"]
lines_d = dict()
for err_type in error_types:
    lines_d[err_type] = []
include = True
for line in lines:
    for err_type in error_types:
        if err_type in line:
            for dr in disregard_l:
                if dr in line:
                    include = False
                    break
            if include:
                lines_d[err_type].append(line)
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
