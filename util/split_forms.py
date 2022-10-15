# used to split quotation marks from words for dev-test-train, 9/28/2022 4:56 PM ; actually updated treebanks: 10/15/2022 10:36 PM
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
new_tb = ''

forms_split = [{"pattern": r'[\d-]+\t"\w+\t', "direction": "before", "value": 'ID	"	"	PUNCT	Punc	_	HEAD	punct	_	SpaceAfter=No'}, {"pattern": r'[\d-]+\t\w+"\t', "direction": "after", "value": 'ID	"	"	PUNCT	Punc	_	HEAD	punct	_	_'}]

for sentence in sentences:
    to_split = False
    sent_id, text, lines_str = sentence
    new_tb += '# sent_id = {sent_id}\n# text = {text}\n'.format(
        sent_id=sent_id, text=text)
    lines = lines_str.split('\n')

    for i, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue

        form_t = fields[field_d['form']]
        lemma_t = fields[field_d['lemma']]
        id_t = fields[field_d['id']]
        for fs in forms_split:
            fs_found = re.search(fs['pattern'], line)
            if fs_found:
                if id_t.isnumeric():
                    id_split = int(id_t)
                    direction_split = fs['direction']
                    value_split = fs['value']
                    for j, line in enumerate(lines[i+1:]):
                        fields_quote_t = line.split('\t')
                        form_t = fields_quote_t[field_d['form']]
                        id_quote_t = fields_quote_t[field_d['id']]
                        if '-' not in id_quote_t:
                            id_quote_int_t = int(id_quote_t)
                            if form_t == '"':
                                quote_head = id_quote_int_t
                                break
                            elif '"' in form_t:
                                quote_head = id_quote_int_t+1
                                break
                    to_split = True
                    break
        if to_split:
            break
    if to_split:
        lines_str = ''
        line_insert = {"line": '', 'place': -1}
        place_increment_allowed = True
        for i, line in enumerate(lines):
            fields = line.split('\t')
            if len(fields) != 10:
                continue
            id_t = fields[field_d['id']]
            if place_increment_allowed:
                line_insert['place'] += 1
            if id_t.isnumeric():
                id_int_t = int(id_t)
                if id_int_t > id_split:
                    id_int_t += 1
                    id_t = str(id_int_t)
                    fields[field_d['id']] = id_t
                elif id_int_t == id_split:
                    if direction_split == 'before':
                        fields[field_d['id']] = str(id_int_t+1)
                        fields[field_d['form']] = fields[field_d['form']].replace('"', '')
                        fields[field_d['lemma']] = fields[field_d['lemma']].replace('"', '')
                        if quote_head == -1:
                            line_insert['line'] = value_split.replace('ID', id_t).replace('HEAD', str(id_int_t+1))
                        else:
                            line_insert['line'] = value_split.replace('ID', id_t).replace('HEAD', str(quote_head))
                    elif direction_split == 'after':
                        fields[field_d['form']] = fields[field_d['form']].replace('"', '')
                        fields[field_d['lemma']] = fields[field_d['lemma']].replace('"', '')
                        misc_split = fields[field_d['misc']].split('|')
                        if len(misc_split) == 1 and misc_split[0] == '_':
                            fields[field_d['misc']] = 'SpaceAfter=No'
                        else:
                            misc_d = {'SpaceAfter': 'No'}
                            for ms in misc_split:
                                key, value = ms.split('=')
                                misc_d[key] = value
                            new_misc_l = list()
                            for key in sorted(misc_d.keys(), key=str.casefold):
                                new_misc_l.append('{key}={value}'.format(key=key, value=misc_d[key]))
                            fields[field_d['misc']] = '|'.join(new_misc_l)
                        line_insert['line'] = value_split.replace('ID', str(id_int_t+1)).replace('HEAD', id_t)
                        line_insert['place'] = line_insert['place']+1
                    place_increment_allowed = False
                    # if sent_id == 'bio_692':
                    #     print(line_insert, direction_split, fields)
                    #     input()
            elif '-' in id_t:
                id_l = [int(id_t2) for id_t2 in id_t.split('-')]
                if id_l[0] > id_split:
                    id_t = '-'.join([str(id_t2+1) for id_t2 in id_l])
                    fields[field_d['id']] = id_t
            head_t = fields[field_d['head']]
            if head_t.isnumeric():
                head_int_t = int(head_t)
                if head_int_t > id_split or (direction_split == 'before' and head_int_t >= id_split):
                    head_int_t += 1
                    head_t = str(head_int_t)
                    fields[field_d['head']] = head_t
            lines[i] = '\t'.join(fields)
        lines.insert(line_insert['place'], line_insert['line'])
        lines_str = '\n'.join(lines)
        quote_head = -1
    new_tb += f'{lines_str}\n\n'
# with open(os.path.join(THIS_DIR, 'split_forms_output.conllu'), 'w', encoding='utf-8', newline='\n') as f:
with open(conllu_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb)
if new_tb != tb:
    print('Treebank changed!')
