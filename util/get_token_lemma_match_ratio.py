import argparse, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--treebank', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    treebank_path = Path(args.treebank)
    with open(treebank_path, 'r') as f:
        treebank = json.load(f)
    treebank_name = treebank_path.parent
    print('Treebank: {}'.format(treebank_name))
    
    match, all = 0, 0
    for sent_id in treebank.keys():
        table = treebank[sent_id]['table']
        for row in table.split('\n'):
            fields = row.split('\t')
            id_t = fields[0]
            if '-' in id_t:
                continue
            lemma_t, form_t = fields[2], fields[1]
            if lemma_t.lower() == form_t.lower():
                match += 1
            all += 1
    print('Token-lemma match ratio: {:.2f}%'.format(match / all * 100))

# Treebank: tr_boun/v2.8
# Token-lemma match ratio: 53.27%
# --------------------------------
# Treebank: tr_boun/v2.11
# Token-lemma match ratio: 55.16%

if __name__ == '__main__':
    main()