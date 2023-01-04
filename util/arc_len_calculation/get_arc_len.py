import os, argparse, re

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--treebank', action="store", required=True)
args = parser.parse_args()

treebank_folderpath = args.treebank
conllu_filepath_l = [os.path.join(treebank_folderpath, i) for i in os.listdir(treebank_folderpath) if i.endswith('.conllu')]

sentence_pattern = r'(.*?)\n\n'
token_count = 0
arc_len_sum = 0
max_arc_len = 0
for conllu_filepath in conllu_filepath_l:
    with open(conllu_filepath, 'r', encoding='utf-8') as f:
        tb = f.read()
    sentences = re.findall(sentence_pattern, tb, re.DOTALL)
    for sentence in sentences:
        lines = sentence.split('\n')
        for line in lines:
            if line.startswith('#'):
                continue
            fields = line.split('\t')
            id_t, head = fields[0], fields[6]
            if not id_t.isnumeric() or head == '0':
                continue
            arc_len = abs(int(id_t) - int(head))
            arc_len_sum += arc_len
            if arc_len > max_arc_len:
                max_arc_len = arc_len
            token_count += 1
print('Max arc length: {max_arc_len}'.format(max_arc_len=max_arc_len))
print('Average arc length: {avg_arc_len}'.format(avg_arc_len=arc_len_sum/token_count))