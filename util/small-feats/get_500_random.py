import argparse, os, re, random

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
parser.add_argument('--output', action="store", required=True)
args = parser.parse_args()

conllu_filepath = args.conllu
if not conllu_filepath.endswith('.conllu'):
    print('conllu file does not have the appropriate extension')
sentence_pattern = r'(.*?)\n\n'
with open(conllu_filepath, 'r', encoding='utf-8') as f:
    tb = f.read()
sentences = re.findall(sentence_pattern, tb, re.DOTALL)
sent_count = len(sentences)
sel_l = []

for i in range(500):
    random_sentence = random.choice(sentences)
    del sentences[sentences.index(random_sentence)]
    sel_l.append(random_sentence)

with open(args.output, 'w', encoding='utf-8') as f:
    for sent in sel_l:
        f.write(sent)
        f.write('\n\n')