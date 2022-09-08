import argparse
import os
import re
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

opt_parser = argparse.ArgumentParser()
arg_group = opt_parser.add_argument_group("Argument Group")
arg_group.add_argument('--conllu', action="store", required=True)
arg_group.add_argument('--ud-validation', action="store")
args = opt_parser.parse_args()

conllu_filepath = args.conllu
conllu_filename = os.path.split(conllu_filepath)[-1]
if not conllu_filename.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
home = os.path.expanduser('~')
sentence_pattern = r'(.*?)\n\n'
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
sentences = re.findall(sentence_pattern, tb, re.DOTALL)
# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}
new_tb = ''
for sentence in sentences:
    lines = sentence.split('\n')
    for line in lines:
        if line.startswith('#'):
            new_tb += f'{line}\n'
            continue
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        for i, field in enumerate(fields):
            # Editing a specific field
            # if i == field_d['xpos'] and field == 'Zero':
            #     print(line)

            # Editing morphological features
            # if i == field_d['feats']:
            #     feats = field.split('|')
            #     for feat in feats:
            #         if '=' in feat: tag, value = feat.split('=')

            # used for changing obl:tmp to obl:tmod, 9/8/2022 3:35 PM
            # if i == field_d['deprel'] and field == 'obl:tmp':
            #     fields[i] = 'obl:tmod'
            #     line = '\t'.join(fields)
            pass
        new_tb += f'{line}\n'
    new_tb += '\n'
with open(conllu_filepath, 'w', encoding='utf-8') as f:
    f.write(new_tb)