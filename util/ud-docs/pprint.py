import json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f1', '--file1', help='file1', required=True)
parser.add_argument('-f2', '--file2', help='file2', required=True)
args = parser.parse_args()

with open(args.file1, 'r', encoding='utf-8') as f:
    data1 = json.load(f)

tag_dict = {}
for el in data1:
    table = el['table']
    lines = table.split('\n')
    for line in lines:
        fields = line.split('\t')
        feats = fields[5].split('|')
        for feat in feats:
            if '=' in feat:
                tag, value = feat.split('=')
                if tag not in tag_dict:
                    tag_dict[tag] = set()
                tag_dict[tag].add(value)

with open(args.file2, 'r', encoding='utf-8') as f:
    data2 = json.load(f)

with open('feat.json', 'r', encoding='utf-8') as f:
    feat_data = json.load(f)

for key, value in feat_data.items():
    if key not in tag_dict:
        continue
    print(key, ':', value['shortdef'])
    key_l = list(value.keys())
    key_l.remove('shortdef')
    if 'content' in key_l:
        key_l.remove('content')
    key_l = [i for i in key_l if i in tag_dict[key]]
    for val in key_l:
        print('\t', val, ':', value[val]['shortdef'])