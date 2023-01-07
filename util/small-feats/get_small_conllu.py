import argparse, os, re, json

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
with open(os.path.join(THIS_DIR, 'sent_id_list.txt'), 'r', encoding='utf-8') as f:
    sent_id_list = json.load(f)
new_conllu = ''
for sent in sentences:
    sent_id = sent[0]
    text = sent[1]
    annotation = sent[2]
    if sent_id in sent_id_list:
        new_conllu += '# sent_id = ' + sent_id + '\n# text = ' + text + '\n' + annotation + '\n\n'
output_filepath = os.path.join(THIS_DIR, 'small.conllu')
with open(output_filepath, 'w', encoding='utf-8') as f:
    f.write(new_conllu)
        