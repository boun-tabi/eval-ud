import argparse, json, random, os
from pathlib import Path
from colorama import Fore, Style

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    parser.add_argument('-d', '--difficulty', type=str, required=True)
    parser.add_argument('--has-dep', action='store_true')
    parser.add_argument('--token-count', type=int, default=25)
    return parser.parse_args()

def main():
    args = get_args()
    version1 = Path(args.version1)
    version2 = Path(args.version2)
    with version1.open('r', encoding='utf-8') as f:
        v1_data = json.load(f)
    with version2.open('r', encoding='utf-8') as f:
        v2_data = json.load(f)

    sent_ids = list(v1_data.keys())
    random.shuffle(sent_ids)

    has_dep = args.has_dep
    difficulty = args.difficulty

    tokens = []
    for sent_id in sent_ids:
        table1, table2 = v1_data[sent_id]['table'], v2_data[sent_id]['table']
        v2_form_d = {}
        d = {'sent_id': sent_id, 'v1': {}, 'v2': {}}
        found_token = False
        v1_splits = set()
        for line in table1.split('\n'):
            id_t = line.split('\t')[0]
            if '-' in id_t:
                ids = id_t.split('-')
                for i in range(int(ids[0]), int(ids[1]) + 1):
                    v1_splits.add(str(i))
        v2_splits = set()
        for line in table2.split('\n'):
            id_t = line.split('\t')[0]
            if '-' in id_t:
                ids = id_t.split('-')
                for i in range(int(ids[0]), int(ids[1]) + 1):
                    v2_splits.add(str(i))
        for line in table2.split('\n'):
            fields = line.split('\t')
            id_t, form, lemma, feats = *fields[:3], fields[5].split('|')
            v2_form_d[id_t] = form
            if found_token:
                continue
            if '-' in id_t or (len(feats) == 1 and feats[0] == '_'):
                continue
            keys = [feat.split('=')[0] for feat in feats]
            if difficulty == 'easy':
                if 'Case=Nom' in feats and 'Number=Sing' in feats:
                    continue
                if ('Case=Nom' not in feats or 'Number=Sing' not in feats) and 2 <= len(keys) <= 4 and id_t not in v2_splits and not lemma.startswith('"'):
                    found_token = True
            elif difficulty == 'medium':
                if 'Evident' in keys or 'Voice' in keys or 'Tense' in keys and id_t not in v2_splits and not lemma.startswith('"'):
                    found_token = True
            if found_token:
                d['v2'] = {'id': id_t, 'form': form, 'lemma': lemma, 'feats': feats}
                if has_dep:
                    d['v2']['head'] = fields[6]
                    d['v2']['deprel'] = fields[7]
        if d['v2'] == {}:
            continue
        same_feats = False
        for line in table1.split('\n'):
            fields = line.split('\t')
            id_t = fields[0]
            if id_t == d['v2']['id']:
                feats = fields[5].split('|')
                if d['v2']['feats'] == feats:
                    same_feats = True
                    break
        if same_feats:
            continue
        if has_dep:
            if d['v2']['head'] == '0':
                d['v2']['head'] = 'root'
            else:
                d['v2']['head'] = v2_form_d[d['v2']['head']]
        os.system('clear')
        print(d['v2']['form'])
        ids_v1_d = {}
        v1_form_d = {}
        for line in table1.split('\n'):
            fields = line.split('\t')
            id_t, form, lemma, feats = *fields[:3], fields[5].split('|')
            v1_form_d[id_t] = form
            d['v1'] = {'id': id_t, 'form': form, 'lemma': lemma, 'feats': feats}
            if has_dep:
                d['v1']['head'] = fields[6]
                d['v1']['deprel'] = fields[7]
            ids_v1_d[id_t] = d['v1']
            if id_t == d['v2']['id']:
                print(f'{Fore.GREEN}{line}{Style.RESET_ALL}')
            else:
                print(line)
        print()
        id_v1 = input()
        if id_v1 == 'e': # exclude
            continue
        if id_v1 == '':
            id_v1 = d['v2']['id']
        d['v1'] = ids_v1_d[id_v1]
        if has_dep:
            if d['v1']['head'] == '0':
                d['v1']['head'] = 'root'
            else:
                d['v1']['head'] = v1_form_d[d['v1']['head']]
        if d['v1']['feats'] == d['v2']['feats']:
            continue
        tokens.append(d)
        if len(tokens) == args.token_count:
            break

    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / f'../data/{difficulty}'
    output_dir.mkdir(parents=True, exist_ok=True)
    if has_dep:
        output_path = output_dir / 'tokens-dep.json'
    else:
        output_path = output_dir / 'tokens.json'
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()