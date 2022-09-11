import argparse
import os
import re
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
parser.add_argument('--ud-validation', action="store")
args = parser.parse_args()

conllu_filepath = args.conllu
conllu_filename = os.path.split(conllu_filepath)[-1]
if not conllu_filename.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
home = os.path.expanduser('~')
sentence_pattern = r'(.*?)\n\n'
sent_id_pattern = r'# sent_id = (.*)'
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
sentences = re.findall(sentence_pattern, tb, re.DOTALL)
# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}
new_tb, sent_id = '', ''
for sentence in sentences:
    lines = sentence.split('\n')
    for line in lines:
        if line.startswith('#'):
            new_tb += f'{line}\n'
            if line.startswith('# sent_id'):
                found = re.search(sent_id_pattern, line)
                if found:
                    sent_id = found.group(1)
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

            # used for sorting morphological features
            if i == field_d['feats']:
                feats = field.split('|')
                if len(feats) == 1 and feats[0] == '_': continue
                feat_d = dict()
                feat_l = list()
                for feat in feats:
                    if feat.count('=') > 1:
                        # print('more than 1 =:', fields, feat, 'sent_id:', sent_id)
                        print('more than 1 =:', 'node:', fields[0], 'sent_id:', sent_id)
                        feat_d[feat[:feat.index('=')]] = 'more than 1 ='
                        continue
                    if '=' in feat: tag, value = feat.split('=')
                    if value == '_':
                        # print('empty value:', fields, 'sent_id:', sent_id)
                        print('empty value:', 'node:', fields[0], 'sent_id:', sent_id)
                    feat_d[tag] = value
                if len(feats) != len(feat_d.keys()):
                    # print('duplicate tag:', fields, 'sent_id:', sent_id)
                    print('duplicate tag:', 'node:', fields[0], 'sent_id:', sent_id)
                for tag in sorted(feat_d.keys(), key=str.casefold): # case-insensitive sort
                    value = feat_d[tag]
                    feat_l.append('{tag}={value}'.format(tag=tag, value=value))
                fields[i] = '|'.join(feat_l)
                line = '\t'.join(fields)
            pass
        new_tb += f'{line}\n'
    new_tb += '\n'
with open(conllu_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb)