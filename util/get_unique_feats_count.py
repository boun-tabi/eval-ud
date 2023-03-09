import argparse, os, re

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

feat_set = set()
for sentence in sentences:
    sent_id, text, lines_str = sentence
    lines = lines_str.split('\n')
    for j, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        feats = fields[5]
        feat_set.add(feats)
print(len(feat_set))