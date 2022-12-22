# python3 util/get_vocab.py --source-column 5 --type feats --treebank .
import os, re, argparse

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--source-column', action="store", required=True)
parser.add_argument('--type', action="store", required=True)
parser.add_argument('--treebank', action="store", required=True)
args = parser.parse_args()

treebank = args.treebank
vocab_type = args.type
folder = treebank
# files = ['train.conllu', 'dev.conllu', 'test.conllu']
files = [i for i in os.listdir(folder) if i.endswith('.conllu')]
source_column = int(args.source_column)
cats_pattern = r'(?:.+\t){' + str(source_column) + '}(.+)\t(?:.+\t){' + str(10 - source_column - 2) + '}.+'
vocab_set = set()
for file in files:
    with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
        content = f.read()
    lines = re.findall(cats_pattern, content)
    for l in lines:
        vocab_set.add(l)
tb_name = os.path.dirname(treebank).split('/')[-1]
with open(os.path.join(THIS_DIR, '{tb}-{type}.vocab'.format(tb=tb_name, type=vocab_type)), 'w', encoding='utf-8', newline='\n') as f:
    for el in vocab_set:
        f.write(el + '\n')
