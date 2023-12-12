import os, json, argparse
from templates import number_d, template2, example1_input, example1_surface, example1_token

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(THIS_DIR, '../util/ud-docs')

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
parser.add_argument('-s', '--sent-id', type=str, required=True)
parser.add_argument('-l', '--language', type=str, required=True, help='The language.')
args = parser.parse_args()

langs_path = os.path.join(THIS_DIR, 'langs.json')
with open(langs_path, 'r', encoding='utf-8') as f:
    langs_d = json.load(f)
open_form_lang = langs_d[args.language]

feats_path = os.path.join(data_dir, 'feat-{lang}.json'.format(lang=args.language))
with open(feats_path, 'r', encoding='utf-8') as f:
    feat_d = json.load(f)
pos_path = os.path.join(data_dir, 'pos-{lang}.json'.format(lang=args.language))
with open(pos_path, 'r', encoding='utf-8') as f:
    pos_d = json.load(f)
dep_path = os.path.join(data_dir, 'dep-{lang}.json'.format(lang=args.language))
with open(dep_path, 'r', encoding='utf-8') as f:
    dep_d = json.load(f)

sent_id = args.sent_id
lang = args.language

with open(args.treebank, 'r', encoding='utf-8') as f:
    treebank_data = json.load(f)

for sent_id_t in treebank_data:
    if sent_id_t != sent_id:
        continue
    example = treebank_data[sent_id]
    text = example['text']
    table = example['table']
    lines = table.split('\n')
    ids = [line.split('\t')[0] for line in lines if '-' not in line.split('\t')[0]]
    dash_ids = [line.split('\t')[0] for line in lines if '-' in line.split('\t')[0]]
    token_count = len(ids) - len(dash_ids)
    token_order = 1
    in_split, first_part_passed = False, False
    prompt_l = []
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t, head_t, dep_t = fields[0], fields[2], fields[3], fields[5], fields[6], fields[7]
        if '-' in id_t:
            in_split = True
            prompt_l.append('{no} token has 2 parts.'.format(no=number_d[token_order]))
            first_part_passed = False
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        if in_split:
            if not first_part_passed:
                token_str_l = ['{no} token\'s first part\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
                first_part_passed = True
            else:
                token_str_l = ['{no} token\'s second part\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
                in_split = False
                first_part_passed = False
        else:
            token_str_l = ['{no} token\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
        token_str_l.append('its part of speech is {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        for feat in feat_l:
            psor_on = False
            feat_name, feat_value = feat.split('=')
            if feat_name.endswith('[psor]'):
                feat_name = feat_name.replace('[psor]', '')
                psor_on = True
            if feat_name in feat_d:
                tag_shortdef = feat_d[feat_name]['shortdef']
            if feat_value in feat_d[feat_name]:
                feat_value = feat_d[feat_name][feat_value]['shortdef']
            if psor_on:
                token_str_l.append('its possessor\'s {fn} is {fv}'.format(fn=tag_shortdef, fv=feat_value))
            else:
                token_str_l.append('its {fn} is {fv}'.format(fn=tag_shortdef, fv=feat_value))
        if dep_t != '_':
            dep_name = dep_d[dep_t]['shortdef']
            if head_t == '0':
                token_str_l.append('it\'s the root token')
            else:
                token_str_l.append('it depends on the {head} token with the dependency relation of {dep}'.format(dep=dep_name, head=number_d[int(head_t)]))

        token_str_l[-1] = 'and ' + token_str_l[-1]
        prompt_l.append(', '.join(token_str_l) + '.')
        if not in_split:
            token_order += 1
    question = '\n'.join(prompt_l)
    eventual_prompt = template2.format(example_surface=example1_surface, example_token=example1_token, example_input=example1_input, token_count=token_count, test_input=question)

    out_str = 'Prompt:\n'
    out_str += eventual_prompt
    out_str += '\n\n'
    out_str += 'Text:\n'
    out_str += text
    out_str += '\n'
    prompts_dir = os.path.join(THIS_DIR, 'prompts')
    if not os.path.exists(prompts_dir):
        os.mkdir(prompts_dir)
    with open(os.path.join(prompts_dir, f'{sent_id}.txt'), 'w', encoding='utf-8') as f:
        f.write(out_str)