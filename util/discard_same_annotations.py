import os, re, argparse, json

parser = argparse.ArgumentParser()
parser.add_argument('--tb1', action="store", required=True)
parser.add_argument('--tb2', action="store", required=True)
args = parser.parse_args()

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
tb1 = args.tb1
tb2 = args.tb2

tb1_files = [os.path.join(tb1, f) for f in os.listdir(tb1) if f.endswith('.conllu')]
tb2_files = [os.path.join(tb2, f) for f in os.listdir(tb2) if f.endswith('.conllu')]

tb1_s = ''
for file in tb1_files:
    with open(file, 'r', encoding='utf-8') as f:
        tb1_s += f.read()
tb2_s = ''
for file in tb2_files:
    with open(file, 'r', encoding='utf-8') as f:
        tb2_s += f.read()

annotation_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'

tb1_annotations = re.findall(annotation_pattern, tb1_s, re.DOTALL)
tb1_d = {i[0]: i[2] for i in tb1_annotations}
tb2_d = {i[0]: i[2] for i in re.findall(annotation_pattern, tb2_s, re.DOTALL)}
tb1_keys = set(tb1_d.keys())
tb2_keys = set(tb2_d.keys())
text_d = {i[0]: i[1] for i in tb1_annotations}

merged_d = {}
for k in tb1_keys.intersection(tb2_keys):
    if tb1_d[k] != tb2_d[k]:
        merged_d[k] = {'text': text_d[k], 'v2.8': tb1_d[k], 'v2.11': tb2_d[k]}

print(len(merged_d))

with open('merged.json', 'w', encoding='utf-8') as f:
    json.dump(merged_d, f, ensure_ascii=False, indent=4)