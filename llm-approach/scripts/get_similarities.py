import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='File to read from', required=True)
parser.add_argument('-s', '--sentences', required=True)
args = parser.parse_args()
file = args.file
sents_path = args.sentences

filename = file.split('/')[-1]
filename_without_ext = filename.split('.')[0]

with open(file, 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(sents_path, 'r', encoding='utf-8') as f:
    sents = json.load(f)

all_sent_ids = list(data['ratios'].keys())
for sent_id in all_sent_ids:
    if sent_id not in sents:
        del data['ratios'][sent_id]

with open(os.path.join(THIS_DIR, '{}-selected.json'.format(filename_without_ext)), 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)