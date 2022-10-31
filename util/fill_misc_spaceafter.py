# used to add SpaceAfter=No in MISC field for dev-test-train, 9/22/2022 12:22 AM
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
metadata_error_path = os.path.join(THIS_DIR, 'Errors', os.path.basename(conllu_filepath).replace('.conllu', ''), 'Metadata.txt')
with open(metadata_error_path, 'r', encoding='utf-8') as f:
    md_err = f.read()
spaceafter_pattern = r'\[Line .*? Sent (.*?)\]: \[L2 Metadata missing-spaceafter\].*?node #(.*?) because'
missing_spaceafters = [i for i in re.findall(spaceafter_pattern, md_err)]
missing_d = {}
for i in missing_spaceafters:
    missing_d[i[0]] = i[1]
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
new_tb = str()
curr_sent_id = ''
sent_id_pattern = '# sent_id = (.*)'
for i, line in enumerate(tb.split('\n')):
    sent_id_search = re.search(sent_id_pattern, line)
    if sent_id_search:
        curr_sent_id = sent_id_search.group(1)
    elif line.count('\t') == 9:
        fields = line.split('\t')
        id_t = fields[0]
        if curr_sent_id in missing_d.keys() and missing_d[curr_sent_id] == id_t:
            misc = fields[9]
            if misc == '_':
                fields[9] = 'SpaceAfter=No'
            else:
                misc_spl = misc.split('|')
                misc_d = dict()
                misc_l = list()
                misc_count = 0
                for misc_t in misc_spl:
                    if misc_t.count('=') > 1:
                        print('more than 1 =:', 'line:', i, 'sent_id:', curr_sent_id, 'id:', id_t)
                        misc_d[misc_t[:misc_t.index('=')]] = 'more than 1 ='
                        continue
                    if '=' in misc_t: tag, value = misc_t.split('=')
                    else:
                        print('empty misc:', 'line:', i, 'sent_id:', curr_sent_id, 'id:', id_t)
                        continue
                    if value == '_':
                        print('empty value:', 'line:', i, 'sent_id:', curr_sent_id, 'id:', id_t)
                    misc_d[tag] = value
                if len(misc_spl) != len(misc_d.keys()):
                    print('duplicate tag:', 'line:', i, 'sent_id:', curr_sent_id, 'id:', id_t)
                misc_d['SpaceAfter'] = 'No'
                for tag in sorted(misc_d.keys(), key=str.casefold): # case-insensitive sort
                    value = misc_d[tag]
                    misc_l.append('{tag}={value}'.format(tag=tag, value=value))
                fields[9] = '|'.join(misc_l)
        line = '\t'.join(fields)
    new_tb += f'{line}\n'
new_tb = new_tb[:-1]
with open(conllu_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb)
if new_tb != tb:
    print('Treebank changed!')
