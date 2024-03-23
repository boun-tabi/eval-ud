import argparse, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb1', '--treebank1', type=str, required=True)
    parser.add_argument('-tb2', '--treebank2', type=str, required=True)
    parser.add_argument('-a', '--all-tokens', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    treebank1, treebank2, all_tokens = Path(args.treebank1), Path(args.treebank2), Path(args.all_tokens)
    with treebank1.open('r', encoding='utf-8') as f:
        tb1_data = json.load(f)
    with treebank2.open('r', encoding='utf-8') as f:
        tb2_data = json.load(f)
    with all_tokens.open('r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    for d in all_data:
        sent_id = d['sent_id']
        v1, v2 = d['v1'], d['v2']
        id_v1, id_v2 = v1['id'], v2['id']

        table1, table2 = tb1_data[sent_id]['table'], tb2_data[sent_id]['table']
        for table in [table1, table2]:
            lines = table.split('\n')
            line = [line for line in lines if line.startswith(id_v1 + '\t')][0]
            fields = line.split('\t')
            upos = fields[3]
            if table == table1:
                v1['upos'] = upos
            else:
                v2['upos'] = upos
        d['v1'], d['v2'] = v1, v2

    with all_tokens.open('w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()