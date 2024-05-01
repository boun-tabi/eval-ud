import os, json, argparse, subprocess, re
from pathlib import Path
from templates import get_example_prompt, get_sentence_prompt, template_sentence

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--treebank', type=str, required=True)
    parser.add_argument('-v', '--version', type=str, required=True)
    parser.add_argument('-td', '--treebanks-dir', type=str, required=True)
    parser.add_argument('-s', '--sent-id', type=str, required=True)
    parser.add_argument('-e', '--example', type=str, required=True)
    parser.add_argument('-d', '--docs', type=str, required=True)
    parser.add_argument('-l', '--language', type=str, required=True, help='The language.')
    parser.add_argument('-lp', '--langs-path', type=str, required=True)
    parser.add_argument('--has-dependency', action='store_true')
    return parser.parse_args()

def clone_repo(treebank, treebank_dir):
    treebank_url = f'https://github.com/UniversalDependencies/{treebank}.git'
    subprocess.run(['git', 'clone', treebank_url, treebank_dir])

def get_treebank(conllu_files):
    data_d = {'sentences': {}}
    md_pattern = re.compile('^# (.+?) = (.+?)$')
    annotation_pattern = re.compile('(.+\t){9}.+')
    for conllu_file in conllu_files:
        with conllu_file.open('r', encoding='utf-8') as f:
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
                    break
            if d_t:
                data_d['sentences'][sent_id] = d_t
    return data_d

def main():
    args = get_args()
    THIS_DIR = Path(__file__).parent
    data_dir = Path(args.docs)
    language = args.language

    langs_path = Path(args.langs_path)
    with open(langs_path, 'r', encoding='utf-8') as f:
        langs_d = json.load(f)
    open_form_lang = langs_d[language]

    feats_path = data_dir / f'feat-{language}.json'
    with feats_path.open('r', encoding='utf-8') as f:
        feat_d = json.load(f)
    pos_path = data_dir / f'pos-{language}.json'
    with pos_path.open('r', encoding='utf-8') as f:
        pos_d = json.load(f)
    has_dependency = args.has_dependency
    if has_dependency:
        dep_path = data_dir / f'dep-{language}.json'
        with dep_path.open('r', encoding='utf-8') as f:
            dep_d = json.load(f)
        from templates import preamble_dep as preamble
    else:
        dep_d = None
        from templates import preamble_no_dep as preamble

    treebank_name = args.treebank
    treebanks_dir = Path(args.treebanks_dir)
    treebank_dir = treebanks_dir / treebank_name

    if not treebank_dir.exists():
        clone_repo(treebank_name, treebank_dir)
    treebank_dir_resolve = treebank_dir.resolve()
    os.chdir(treebank_dir)
    version = args.version
    current_tag = f'r{version}'
    subprocess.run(['git', 'checkout', current_tag])
    os.chdir(THIS_DIR)
    treebank_dir = Path(treebank_dir_resolve)
    conllu_files = list(treebank_dir.glob('*.conllu'))
    tb_d = get_treebank(conllu_files)

    example_sent_id = args.example
    sent_id = args.sent_id

    example_sentence = tb_d['sentences'][example_sent_id]
    example_text, example_table = example_sentence['text'], example_sentence['table']
    example_token_count, example_question = get_example_prompt(example_table, pos_d, feat_d, dep_d)

    sentence = tb_d['sentences'][sent_id]
    table, text = sentence['table'], sentence['text']
    prompt = get_sentence_prompt(template_sentence, preamble, example_text, example_token_count, example_question, open_form_lang, table, pos_d, feat_d, dep_d)

    out_d = {'prompt': prompt, 'text': text}
    prompts_dir = THIS_DIR / 'prompts'
    if not prompts_dir.exists():
        prompts_dir.mkdir()
    prompt_path = prompts_dir / f'{treebank_name}-{version}-{sent_id}.json'
    with prompt_path.open('w', encoding='utf-8') as f:
        json.dump(out_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()