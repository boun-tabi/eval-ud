import os, json, argparse
from pathlib import Path
from templates import get_sentence_prompt, template_sentence_with_dep

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--treebank', type=str, required=True)
    parser.add_argument('-s', '--sent-id', type=str, required=True)
    parser.add_argument('-d', '--docs', type=str, required=True)
    parser.add_argument('-l', '--language', type=str, required=True, help='The language.')
    parser.add_argument('-lp', '--langs-path', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    THIS_DIR = Path(__file__).resolve().parent
    data_dir = Path(args.docs)
    language = args.language

    langs_path = Path(args.langs_path)
    with open(langs_path, 'r', encoding='utf-8') as f:
        langs_d = json.load(f)
    open_form_lang = langs_d[language]

    feats_path = os.path.join(data_dir, 'feat-{lang}.json'.format(lang=language))
    with open(feats_path, 'r', encoding='utf-8') as f:
        feat_d = json.load(f)
    pos_path = os.path.join(data_dir, 'pos-{lang}.json'.format(lang=language))
    with open(pos_path, 'r', encoding='utf-8') as f:
        pos_d = json.load(f)
    dep_path = os.path.join(data_dir, 'dep-{lang}.json'.format(lang=language))
    with open(dep_path, 'r', encoding='utf-8') as f:
        dep_d = json.load(f)

    sent_id = args.sent_id

    with open(args.treebank, 'r', encoding='utf-8') as f:
        tb_data = json.load(f)

    sentence = tb_data[sent_id]
    text, table = sentence['text'], sentence['table']
    eventual_prompt = get_sentence_prompt(template_sentence_with_dep, open_form_lang, table, pos_d, feat_d, dep_d)

    out_str = 'Prompt:\n'
    out_str += eventual_prompt
    out_str += '\n\n'
    out_str += 'Text:\n'
    out_str += text
    out_str += '\n'
    prompts_dir = THIS_DIR / 'prompts'
    if not os.path.exists(prompts_dir):
        os.mkdir(prompts_dir)
    with open(os.path.join(prompts_dir, f'{sent_id}.txt'), 'w', encoding='utf-8') as f:
        f.write(out_str)

if __name__ == '__main__':
    main()