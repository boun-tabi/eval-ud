import os, json, argparse
from templates import number_d, template2, example1_input, example1_surface, example1_token, get_prompt

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
    eventual_prompt = get_prompt(table, pos_d, feat_d, dep_d)

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