import argparse
import os
import re

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
args = parser.parse_args()

conllu_filepath = args.conllu
if not conllu_filepath.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
sentence_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
sentences = re.findall(sentence_pattern, tb, re.DOTALL)
# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}
new_tb, sent_id = '', ''

for sentence in sentences:
    sent_id, text, lines_str = sentence
    new_tb += '# sent_id = {sent_id}\n# text = {text}\n'.format(
        sent_id=sent_id, text=text)
    lines = lines_str.split('\n')
    for j, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        if fields[field_d['lemma']] == 'y' or fields[field_d['lemma']] == 'N/A':
            fields[field_d['lemma']] = 'i'
        if fields[field_d['deprel']] == 'dep:der':
            fields[field_d['deprel']] = 'mark'
        if fields[field_d['lemma']] == 'değil' and fields[field_d['deprel']] == 'cop':
            fields[field_d['upos']] = 'AUX'
            fields[field_d['xpos']] = 'Neg'
            fields[field_d['deprel']] = 'aux'
        if fields[field_d['deprel']] == 'discourse:q':
            fields[field_d['deprel']] = 'aux:q'
            fields[field_d['upos']] = 'AUX'
        if fields[field_d['lemma']] == 'dur' and fields[field_d['upos']] == 'AUX':
            fields[field_d['upos']] = 'VERB'
            fields[field_d['deprel']] = 'compound:lvc'
        line = '\t'.join(fields)
        new_tb += f'{line}\n'
    new_tb += '\n'
new_filepath = conllu_filepath.replace('.conllu', '-masked.conllu')
with open(new_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb)
