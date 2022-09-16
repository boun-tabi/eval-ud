import os
import argparse
import re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
parser.add_argument('--sent-id', action="store", required=True)
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
sent_id = ''
order = 0
sentence_found = False
for sentence in sentences:
    lines = sentence.split('\n')
    for line in lines:
        if line.startswith('# sent_id'):
            found = re.search(sent_id_pattern, line)
            if found:
                sent_id = found.group(1)
                order += 1
                if sent_id == args.sent_id:
                    print('Order: {order}'.format(order=order))
                    sentence_found = True
                    break
    if sentence_found:
        break
