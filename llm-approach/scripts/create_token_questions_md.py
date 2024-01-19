import os, json, argparse, random, csv
from templates import template2, get_md_table_prompt

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sent-ids', type=str, required=True, help='The sentence ids.')
parser.add_argument('-tb8', '--treebank-8', type=str, required=True, help='The treebank 8.')
parser.add_argument('-tb11', '--treebank-11', type=str, required=True, help='The treebank 11.')
parser.add_argument('-n', '--note', type=str, required=True, help='The note.')
parser.add_argument('-e', '--exclude', type=str, required=False, help='The exclude.')
args = parser.parse_args()

with open(args.sent_ids, 'r', encoding='utf-8') as f:
    sent_ids = json.load(f)

if args.exclude:
    with open(args.exclude, 'r', encoding='utf-8') as f:
        exclude = json.load(f)
    sent_ids = [sent_id for sent_id in sent_ids if sent_id not in exclude]

print('Number of sentences:', len(sent_ids))

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

template = template2

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'ud-docs')
with open(os.path.join(data_dir, 'feat-tr.json'), 'r', encoding='utf-8') as f:
    feat_d = json.load(f)
with open(os.path.join(data_dir, 'pos-tr.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)
with open(os.path.join(data_dir, 'dep-tr.json'), 'r', encoding='utf-8') as f:
    dep_d = json.load(f)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(args.treebank_8, 'r', encoding='utf-8') as f:
    v2_8_tb = json.load(f)
with open(args.treebank_11, 'r', encoding='utf-8') as f:
    v2_11_tb = json.load(f)

prompts_8 = {}
prompts_11 = {}
for sent_id in sent_ids:
    table_8 = v2_8_tb[sent_id]['table']
    md_prompt_8 = get_md_table_prompt(sent_id, table_8)
    prompts_8[sent_id] = md_prompt_8
    table_11 = v2_11_tb[sent_id]['table']
    md_prompt_11 = get_md_table_prompt(sent_id, table_11)
    prompts_11[sent_id] = md_prompt_11

output_str = f'# Certain {len(sent_ids)} selected sentences for {args.note}\n\n'

prompt_order_8 = list(prompts_8.keys())
random.shuffle(prompt_order_8)
prompt_order_11 = list(prompts_11.keys())
random.shuffle(prompt_order_11)

used_pos = set()
used_feats = set()
used_dep = set()
for sent_id in prompt_order_8:
    table = v2_8_tb[sent_id]['table']
    for row in table.split('\n'):
        fields = row.split('\t')
        pos = fields[3]
        used_pos.add(pos)
        feat_l = fields[5].split('|')
        for feat in feat_l:
            used_feats.add(feat)
        dep = fields[7]
        used_dep.add(dep)

# pos glossary
output_str += '## POS Glossary' + '\n\n'
output_str += '| POS | Description |' + '\n'
output_str += '| --- | --- |' + '\n'
pos_l_sorted = sorted(list(pos_d.keys()))
for pos in pos_l_sorted:
    if pos not in used_pos:
        continue
    output_str += '| {} | {} |'.format(pos, pos_d[pos]['shortdef']) + '\n'
output_str += '\n' + '-' * 50 + '\n\n'

# feat glossary
output_str += '## FEAT Glossary' + '\n\n'
output_str += '| FEAT | Tag | Value |' + '\n'
output_str += '| --- | --- | --- |' + '\n'
feat_l_sorted = sorted(list(feat_d.keys()))
for feat in feat_l_sorted:
    val_l = list(feat_d[feat].keys())
    val_l.remove('shortdef')
    val_l.remove('content')
    val_l.sort()
    for val in val_l:
        if f'{feat}={val}' not in used_feats:
            continue
        output_str += '| {}={} | {} | {} |'.format(feat, val, feat_d[feat]['shortdef'], feat_d[feat][val]['shortdef']) + '\n'
output_str += '\n' + '-' * 50 + '\n\n'

# dep glossary
output_str += '## DEP Glossary' + '\n\n'
output_str += '| DEP | Description |' + '\n'
output_str += '| --- | --- |' + '\n'
dep_l_sorted = sorted(list(dep_d.keys()))
for dep in dep_l_sorted:
    if dep not in used_dep:
        continue
    output_str += '| {} | {} |'.format(dep, dep_d[dep]['shortdef']) + '\n'
output_str += '\n' + '-' * 50 + '\n\n'

starting_str = output_str

str_8 = '## Annotations' + '\n\n'
for sent_id in prompt_order_8:
    str_8 += prompts_8[sent_id] + '\n\n'

str_11 = '## Annotations' + '\n\n'
for sent_id in prompt_order_11:
    str_11 += prompts_11[sent_id] + '\n\n'
output_path = os.path.join(THIS_DIR, 'created-approved-questions_conv-ptcp-advcl-acl-ccomp_{}_8.md'.format(args.note))
with open(os.path.join(THIS_DIR, output_path), 'w', encoding='utf-8') as f:
    f.write(starting_str + str_8)
output_path = os.path.join(THIS_DIR, 'created-approved-questions_conv-ptcp-advcl-acl-ccomp_{}_11.md'.format(args.note))
with open(os.path.join(THIS_DIR, output_path), 'w', encoding='utf-8') as f:
    f.write(starting_str + str_11)

csv_path_8 = os.path.join(THIS_DIR, 'created-approved-questions_conv-ptcp-advcl-acl-ccomp_{}_8.csv'.format(args.note))
with open(csv_path_8, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Sentence ID', 'Text'])
    for sent_id in prompt_order_8:
        writer.writerow([sent_id, ''])
csv_path_11 = os.path.join(THIS_DIR, 'created-approved-questions_conv-ptcp-advcl-acl-ccomp_{}_11.csv'.format(args.note))
with open(csv_path_11, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Sentence ID', 'Text'])
    for sent_id in prompt_order_11:
        writer.writerow([sent_id, ''])

print('Done!')