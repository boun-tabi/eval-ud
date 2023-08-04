import argparse, os, re, json

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
args = parser.parse_args()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser('~')
data_path = args.treebank
data_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.conllu')]
data_files = sorted(data_files)

data_l = []
md_pattern = '#(.+)=(.+)'
annotation_pattern = '(.+\t){9}.+'
for f in data_files:
    with open(f, 'r') as f:
        content = f.read()
    sents = content.split('\n\n')
    for sent in sents:
        lines = sent.split('\n')
        d_t = {}
        for i, line in enumerate(lines):
            md_match = re.match(md_pattern, line)
            if md_match:
                field = md_match.group(1).strip()
                value = md_match.group(2).strip()
                d_t[field] = value
            annotation_match = re.match(annotation_pattern, line)
            if annotation_match:
                annotation = '\n'.join(lines[i:])
                d_t['table'] = annotation
                break
        if d_t:
            data_l.append(d_t)

with open(os.path.join(data_path, 'treebank.json'), 'w', encoding='utf-8') as f:
    json.dump(data_l, f, ensure_ascii=False, indent=4)
