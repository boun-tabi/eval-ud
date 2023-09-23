import json

with open('tr_feats_values.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for key, value in data.items():
    print(key, ':', value['phrase'])
    for val in value['values']:
        print('\t', val, ':', value['values'][val])