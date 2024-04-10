import argparse, json, re, random, subprocess
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str, help='The treebank name')
    parser.add_argument('-s', '--sent-ids', type=str, help='The sentence IDs file')
    parser.add_argument('-o', '--output-file', type=str, help='The output file')
    return parser.parse_args()

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
    treebank = Path(args.treebank)
    if not treebank.exists():
        treebank_title = treebank.stem
        treebank_url = f'https://github.com/UniversalDependencies/{treebank_title}.git'
        subprocess.run(['git', 'clone', treebank_url, treebank])
        if not treebank.exists():
            raise FileNotFoundError(f'The treebank {treebank_title} was not cloned successfully.')
        conllu_files = list(treebank.glob('*.conllu'))
    sent_ids_file = Path(args.sent_ids)
    output_file = Path(args.output_file)
    conllu_files = list(treebank.glob('*.conllu'))
    tb_d = get_treebank(conllu_files)        
    all_sent_ids = set(tb_d['sentences'].keys())
    sents = tb_d['sentences']
    with sent_ids_file.open('r', encoding='utf-8') as f:
        content = json.load(f)
        selected_sent_ids = set(content['sent_ids'])
        sent_count = len(selected_sent_ids)
    with output_file.open('r', encoding='utf-8') as f:
        output = json.load(f)
    sent_ids_processed = set([el['sent_id'] for el in output])
    # print(selected_sent_ids.difference(sent_ids_processed))
    sent_count_needed = sent_count - len(sent_ids_processed)
    new_sent_ids = set()
    while len(new_sent_ids) < sent_count_needed:
        new_sent_id = random.choice(list(all_sent_ids - selected_sent_ids))
        token_count = len([line for line in sents[new_sent_id]['table'].split('\n') if line and '-' not in line.split('\t')[0]])
        if token_count < 30:
            new_sent_ids.add(new_sent_id)
    all_new_ids = list(sent_ids_processed.union(new_sent_ids))
    content['sent_ids'] = all_new_ids
    with sent_ids_file.open('w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()