import argparse
import os
import re
# import json

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

# used for morphological feature counting by dis/allowed, 9/21/2022 11:25 AM
# with open(os.path.join(THIS_DIR, 'allowed-feats-tr.json'), 'r') as f:
#     allowed_feat_l = json.load(f)
# feats_d = {"allowed_feats": {}, "disallowed_feats": {}}

# count = 0

for sentence in sentences:
    sent_id, text, lines_str = sentence
    new_tb += '# sent_id = {sent_id}\n# text = {text}\n'.format(
        sent_id=sent_id, text=text)
    # text_l = text.split(' ')
    # rem_text = text
    lines = lines_str.split('\n')
    # not_consider = []
    for j, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue

        # used for checking form mismatches, 9/22/2022 8:30 PM
        # if '-' in fields[field_d['id']]:
        #     for el in [id_t for id_t in fields[field_d['id']].split('-')]:
        #         not_consider.append(el)
        # if fields[field_d['id']] in not_consider:
        #     pass
        # elif not rem_text.startswith(fields[field_d['form']]):
        #     print(rem_text, fields[field_d['form']])
        #     print(text)
        #     input()
        #     pass
        # else:
            # print(rem_text)
            # rem_text = rem_text[len(fields[field_d['form']]):].lstrip()
            # print(rem_text);input()
            # print(rem_text, fields[field_d['form']]);input()

        for i, field in enumerate(fields):

            # Editing a specific field
            # if i == field_d['xpos'] and field == 'Zero':
            #     print(line)

            # Editing morphological features
            # if i == field_d['feats']:
            #     feats = field.split('|')
            #     for feat in feats:
            #         if '=' in feat: tag, value = feat.split('=')

            # used to remove SpaceAfter=No (text-form-mismatch & text-extra-chars) in MISC field for dev-test-train, 9/22/2022 9:56 PM
            # if i == field_d['misc'] and 'SpaceAfter=No' in field and j != len(lines)-1 and fields[field_d['form']] + lines[j+1].split('\t')[field_d['form']] not in text and '-' not in fields[field_d['id']]:
            #     misc = fields[field_d['misc']]
            #     misc_l = misc.split('|')
            #     misc_l.remove('SpaceAfter=No')
            #     new_misc = '|'.join(misc_l)
            #     if new_misc == '': new_misc = '_'
            #     fields[field_d['misc']] = new_misc
                # print(line, text, sent_id);input()
                # line = '\t'.join(fields)

            # used to change the forms 'bir' to 'Bir' if text starts with 'Bir', 9/22/2022 1:49 PM
            # print(rem_text);input()
            # if re.search(r'^.*?Bir[ ]+', text) and i == field_d['form'] and field == 'bir':
            #     print(text, fields);input()
            # if j == 0 and text.startswith('Bir ') and fields[field_d['id']] == '1' and i == field_d['form'] and field == 'bir':
            #     fields[i] = 'Bir'
            #     line = '\t'.join(fields)

            # used for morphological feature counting by dis/allowed, 9/21/2022 11:25 AM
            # if i == field_d['feats']:
            #     feats = field.split('|')
            #     for feat in feats:
            #         if feat in allowed_feat_l:
            #             allowed_str = 'allowed'
            #         else:
            #             allowed_str = 'disallowed'
            #         if feat in feats_d["{allowed}_feats".format(allowed=allowed_str)].keys():
            #             feats_d["{allowed}_feats".format(
            #                 allowed=allowed_str)][feat] += 1
            #         else:
            #             feats_d["{allowed}_feats".format(
            #                 allowed=allowed_str)][feat] = 1

            # used for changing obl:tmp to obl:tmod, 9/8/2022 3:35 PM
            # if i == field_d['deprel'] and field == 'obl:tmp':
            #     fields[i] = 'obl:tmod'
            #     line = '\t'.join(fields)

            # used for sorting morphological features, 9/11/2022 & 9/21/2022
            # if i == field_d['feats']:
            #     feats = field.split('|')
            #     if len(feats) == 1 and feats[0] == '_': continue
            #     feat_d = dict()
            #     feat_l = list()
            #     feat_count = 0
            #     for feat in feats:
            #         if feat.count('=') > 1:
            #             # print('more than 1 =:', fields, feat, 'sent_id:', sent_id)
            #             print('more than 1 =:', 'node:', fields[0], 'sent_id:', sent_id)
            #             feat_d[feat[:feat.index('=')]] = 'more than 1 ='
            #             continue
            #         if '=' in feat: tag, value = feat.split('=')
            #         else:
            #             print('empty feat:', 'node:', fields[0], 'sent_id:', sent_id)
            #             continue
            #         if value == '_':
            #             # print('empty value:', fields, 'sent_id:', sent_id)
            #             print('empty value:', 'node:', fields[0], 'sent_id:', sent_id)
            #         feat_d[tag] = value
            #     if len(feats) != len(feat_d.keys()):
            #         # print('duplicate tag:', fields, 'sent_id:', sent_id)
            #         print('duplicate tag:', 'node:', fields[0], 'sent_id:', sent_id)
            #     for tag in sorted(feat_d.keys(), key=str.casefold): # case-insensitive sort
            #         value = feat_d[tag]
            #         feat_l.append('{tag}={value}'.format(tag=tag, value=value))
            #     fields[i] = '|'.join(feat_l)
            #     line = '\t'.join(fields)

            pass
        new_tb += f'{line}\n'
    new_tb += '\n'
# with open(conllu_filepath, 'w', encoding='utf-8', newline='\n') as f:
#     f.write(new_tb)
if new_tb != tb:
    print('Treebank changed!')

# check_len = 1000
# print(new_tb[:check_len] == tb[:check_len])

# used for morphological feature counting by dis/allowed, 9/21/2022 11:25 AM
# feats_count_folder = os.path.join(THIS_DIR, 'Feats-Count')
# if not os.path.exists(feats_count_folder):
#     os.mkdir(feats_count_folder)
# with open(os.path.join(feats_count_folder, '{tb_name}.json'.format(tb_name=os.path.basename(conllu_filepath).replace('.conllu', ''))), 'w') as f:
#     json.dump(feats_d, f)
