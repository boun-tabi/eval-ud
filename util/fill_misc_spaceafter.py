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
spaceafter_pattern = r'\[Line (\d+?) Sent [a-z0-9_]+?\]: \[L2 Metadata missing-spaceafter\]'
missing_lines = [int(i) for i in re.findall(spaceafter_pattern, md_err, re.DOTALL)]
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
new_tb = str()
for i, line in enumerate(tb.split('\n')):
    if i+1 in missing_lines:
        fields = line.split('\t')
        # print(fields);input()
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
                    print('more than 1 =:', 'line:', i)
                    misc_d[misc_t[:misc_t.index('=')]] = 'more than 1 ='
                    continue
                if '=' in misc_t: tag, value = misc_t.split('=')
                else:
                    print('empty feat:', 'line:', i)
                    continue
                if value == '_':
                    print('empty value:', 'line:', i)
                misc_d[tag] = value
            if len(misc_spl) != len(misc_d.keys()):
                print('duplicate tag:', 'line:', i)
            misc_d['SpaceAfter'] = 'No'
            for tag in sorted(misc_d.keys(), key=str.casefold): # case-insensitive sort
                value = misc_d[tag]
                misc_l.append('{tag}={value}'.format(tag=tag, value=value))
            fields[9] = '|'.join(misc_l)
        line = '\t'.join(fields)
    new_tb += f'{line}\n'
with open(conllu_filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_tb[:-1])
