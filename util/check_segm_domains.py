import os
import argparse
import re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
args = parser.parse_args()

conllu_filepath = args.conllu
if not conllu_filepath.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
metadata_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n'
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
metadata = re.findall(metadata_pattern, tb)
segm_errors = {'bio': 0, 'ins': 0, 'ess': 0, 'news': 0, 'pop': 0}
for sent_id, text in metadata:
    segm_error = False
    if not text.endswith('.'):
        # print(text);input()
        segm_error = True
    if text.count('"') % 2 == 1:
        # print(text);input()
        segm_error = True
    if text.count('(') != text.count(')'):
        # print(text);input()
        segm_error = True
    if segm_error:
        for s_e in segm_errors.keys():
            if sent_id.startswith(s_e):
                segm_errors[s_e] += 1
                break

print('Segmentation errors in {filename}'.format(filename=os.path.basename(conllu_filepath)))
print(segm_errors)
'''
Segmentation errors in tr_boun_v2-dev.conllu
{'bio': 22, 'ins': 45, 'ess': 31, 'news': 45, 'pop': 48}
Segmentation errors in tr_boun_v2-test.conllu
{'bio': 19, 'ins': 50, 'ess': 22, 'news': 32, 'pop': 48}
Segmentation errors in tr_boun_v2-train.conllu
{'bio': 193, 'ins': 339, 'ess': 219, 'news': 363, 'pop': 425}
'''
