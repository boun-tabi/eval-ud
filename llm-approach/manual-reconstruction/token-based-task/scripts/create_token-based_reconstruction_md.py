import os, json, argparse, csv
from templates import get_md_line_prompt

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tokens', type=str, required=True, help='The tokens.')
parser.add_argument('-tb8', '--treebank-8', type=str, required=True, help='The treebank 8.')
parser.add_argument('-tb11', '--treebank-11', type=str, required=True, help='The treebank 11.')
parser.add_argument('-n', '--note', type=str, required=True, help='The note.')
args = parser.parse_args()

with open(args.tokens, 'r', encoding='utf-8') as f:
    tokens = json.load(f)

print('Number of tokens:', len(tokens))

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'ud-docs')
with open(os.path.join(data_dir, 'feat-tr.json'), 'r', encoding='utf-8') as f:
    feat_d = json.load(f)
with open(os.path.join(data_dir, 'pos-tr.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)
with open(os.path.join(data_dir, 'dep-tr.json'), 'r', encoding='utf-8') as f:
    dep_d = json.load(f)

with open(args.treebank_8, 'r', encoding='utf-8') as f:
    v2_8_tb = json.load(f)
with open(args.treebank_11, 'r', encoding='utf-8') as f:
    v2_11_tb = json.load(f)

prompts_8, lines_8 = {}, []
prompts_8_dep = {}
prompts_11, lines_11 = {}, []
prompts_11_dep = {}

normal_l = tokens['normal']
dep_l = tokens['dep']

for v in ['normal', 'dep']:
    if v == 'normal':
        l = normal_l
    else:
        l = dep_l
    for el in l:
        sent_id = el['sent_id']
        id8, id11 = el['id8'], el['id11']
        table_8 = v2_8_tb[sent_id]['table']
        for line in table_8.split('\n'):
            fields = line.split('\t')
            id_t = fields[0]
            if id_t != id8:
                continue
            head_t = fields[6]
            if head_t == '0':
                head_token = 'ROOT'
            for line2 in table_8.split('\n'):
                fields2 = line2.split('\t')
                id_t2 = fields2[0]
                if id_t2 != head_t:
                    continue
                head_token = fields2[1]
                break
            lines_8.append({'sent_id': sent_id, 'line': line, 'head_token': head_token, 'token_id': id_t, 'token_form': fields[1], 'v': v})
        table_11 = v2_11_tb[sent_id]['table']
        for line in table_11.split('\n'):
            fields = line.split('\t')
            id_t = fields[0]
            if id_t != id11:
                continue
            head_t = fields[6]
            for line2 in table_11.split('\n'):
                fields2 = line2.split('\t')
                id_t2 = fields2[0]
                if id_t2 != head_t:
                    continue
                head_token = fields2[1]
                break
            lines_11.append({'sent_id': sent_id, 'line': line, 'head_token': head_token, 'token_id': id_t, 'token_form': fields[1], 'v': v})

for i, line_t in enumerate(lines_8):
    sent_id, line, head_token, token_id, v = line_t['sent_id'], line_t['line'], line_t['head_token'], line_t['token_id'], line_t['v']
    if v == 'normal':
        d = {'sent_id': sent_id, 'md_line': get_md_line_prompt(len(prompts_8)+1, line), 'token_id': token_id, 'token_form': line_t['token_form']}
        prompts_8[len(prompts_8)+1] = d
    else:
        d = {'sent_id': sent_id, 'md_line': get_md_line_prompt(len(prompts_8_dep)+1, line, True, head_token), 'token_id': token_id, 'token_form': line_t['token_form']}
        prompts_8_dep[len(prompts_8_dep)+1] = d
for i, line_t in enumerate(lines_11):
    sent_id, line, head_token, token_id, v = line_t['sent_id'], line_t['line'], line_t['head_token'], line_t['token_id'], line_t['v']
    if v == 'normal':
        d = {'sent_id': sent_id, 'md_line': get_md_line_prompt(len(prompts_11)+1, line), 'token_id': token_id, 'token_form': line_t['token_form']}
        prompts_11[len(prompts_11)+1] = d
    else:
        d = {'sent_id': sent_id, 'md_line': get_md_line_prompt(len(prompts_11_dep)+1, line, True, head_token), 'token_id': token_id, 'token_form': line_t['token_form']}
        prompts_11_dep[len(prompts_11_dep)+1] = d

output_str = f'# Certain tokens selected for {args.note}\n\n'

prompt_8_order = list(prompts_8.keys())
prompt_8_dep_order = list(prompts_8_dep.keys())
prompt_11_order = list(prompts_11.keys())
prompt_11_dep_order = list(prompts_11_dep.keys())

used_pos = set()
used_feats = set()
used_dep = set()
sent_ids = {el['sent_id'] for el in lines_8}
for line in lines_8 + lines_11:
    line_t = line['line']
    fields = line_t.split('\t')
    id_t = fields[0]
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
for order_t in prompt_8_order:
    md_line = prompts_8[order_t]['md_line']
    str_8 += md_line + '\n'

str_8_dep = '## Annotations' + '\n\n'
for order_t in prompt_8_dep_order:
    md_line = prompts_8_dep[order_t]['md_line']
    str_8_dep += md_line + '\n'

str_11 = '## Annotations' + '\n\n'
for order_t in prompt_11_order:
    md_line = prompts_11[order_t]['md_line']
    str_11 += md_line + '\n'

str_11_dep = '## Annotations' + '\n\n'
for order_t in prompt_11_dep_order:
    md_line = prompts_11_dep[order_t]['md_line']
    str_11_dep += md_line + '\n'

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8.json'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(prompts_8, f, indent=4, ensure_ascii=False)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8_dep.json'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(prompts_8_dep, f, indent=4, ensure_ascii=False)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11.json'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(prompts_11, f, indent=4, ensure_ascii=False)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11_dep.json'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(prompts_11_dep, f, indent=4, ensure_ascii=False)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8.md'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(starting_str + str_8)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8_dep.md'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(starting_str + str_8_dep)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11.md'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(starting_str + str_11)

output_path = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11_dep.md'.format(args.note))
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(starting_str + str_11_dep)

csv_path_8 = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8.csv'.format(args.note))
with open(csv_path_8, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Token ID', 'Surface Form'])
    for token_id in prompt_8_order:
        writer.writerow([token_id, ''])

csv_path_8_dep = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_8_dep.csv'.format(args.note))
with open(csv_path_8_dep, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Token ID', 'Surface Form'])
    for token_id in prompt_8_dep_order:
        writer.writerow([token_id, ''])

csv_path_11 = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11.csv'.format(args.note))
with open(csv_path_11, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Token ID', 'Surface Form'])
    for token_id in prompt_11_order:
        writer.writerow([token_id, ''])

csv_path_11_dep = os.path.join(THIS_DIR, 'created-approved-token-questions_conv-ptcp-advcl-acl-ccomp_{}_11_dep.csv'.format(args.note))
with open(csv_path_11_dep, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Token ID', 'Surface Form'])
    for token_id in prompt_11_dep_order:
        writer.writerow([token_id, ''])

print('Done!')