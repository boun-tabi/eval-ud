import argparse, os, re, json

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
args = parser.parse_args()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser('~')
data_path = args.treebank
tb_name = os.path.basename(data_path)
version = 'v2.13'
data_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.conllu')]
data_files = sorted(data_files)

data_d = {'treebank_name': tb_name, 'version': version, 'sentences': {}}
md_pattern = re.compile('^# (.+?) = (.+?)$')
annotation_pattern = re.compile('(.+\t){9}.+')
for f in data_files:
    if 'train' in f:
        split = 'train'
    elif 'dev' in f:
        split = 'dev'
    elif 'test' in f:
        split = 'test'
    else:
        raise ValueError('File {} does not contain train, dev, or test'.format(f))
    with open(f, 'r', encoding='utf-8') as f:
        content = f.read()
    sents = content.split('\n\n')
    for sent in sents:
        lines = sent.split('\n')
        sent_id = ''
        d_t = {}
        for i, line in enumerate(lines):
            md_match = md_pattern.match(line)
            if md_match:
                field = md_match.group(1).strip()
                value = md_match.group(2).strip()
                if field == 'sent_id':
                    sent_id = value
                else:
                    d_t[field] = value
            annotation_match = annotation_pattern.match(line)
            if annotation_match:
                annotation = '\n'.join(lines[i:])
                d_t['table'] = annotation
                d_t['split'] = split
                break
        if d_t:
            data_d['sentences'][sent_id] = d_t

with open(os.path.join(data_path, 'treebank-splits-{}-{}.json').format(tb_name, version),
          'w', encoding='utf-8') as f:
    json.dump(data_d, f, ensure_ascii=False, indent=4)
