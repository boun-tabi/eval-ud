import os
import re
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sentence_pattern = r'(.*?)\n\n'
conllu_path = f'{THIS_DIR}/../tr_boun_v2/tr_boun_v2-dev.conllu'
with open(conllu_path, 'r', encoding='utf-8') as f:
    tb = f.read()
sentences = re.findall(sentence_pattern, tb, re.DOTALL)
# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}
for sentence in sentences:
    lines = sentence.split('\n')
    for line in lines:
        if line.startswith('#'):
            continue
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        for i, field in enumerate(fields):
            # Editing a specific field
            # if i == field_d['xpos'] and value == 'Zero':
            #     print(line)

            # Editing morphological features
            # if i == field_d['feats']:
            #     feats = field.split('|')
            #     for feat in feats:
            #         if '=' in feat: tag, value = feat.split('=')
            pass
