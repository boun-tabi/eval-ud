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
sentences = re.findall(metadata_pattern, tb, re.DOTALL)
with open(os.path.join(THIS_DIR, 'sentences_with_ids-texts.txt'), 'a', encoding='utf-8') as f:
	for sentence in sentences:
		f.write('sent_id: {sent_id}\ntext: {text}\n\n'.format(sent_id=sentence[0], text=sentence[1]))
