import argparse, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(description='Check different annotations')
    parser.add_argument('-t1', '--treebank1', type=str, required=True, help='Path to the first treebank')
    parser.add_argument('-t2', '--treebank2', type=str, required=True, help='Path to the second treebank')
    parser.add_argument('-f', '--form', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()

    first_treebank_path = Path(args.treebank1)
    with first_treebank_path.open() as f:
        first_treebank = json.load(f)
    
    second_treebank_path = Path(args.treebank2)
    with second_treebank_path.open() as f:
        second_treebank = json.load(f)
    
    sent_ids = list(first_treebank.keys())

    form = args.form
    for sent_id in sent_ids:
        tb1_annotations, tb2_annotations = [], []
        table1, table2 = first_treebank[sent_id]['table'], second_treebank[sent_id]['table']

        for line in table1.split('\n'):
            fields = line.split('\t')
            form_t = fields[1]
            if form_t == form:
                tb1_annotations.append(fields[5]) # feats
        
        for line in table2.split('\n'):
            fields = line.split('\t')
            form_t = fields[1]
            if form_t == form:
                tb2_annotations.append(fields[5]) # feats
        
        for tb1_annotation in tb1_annotations:
            for tb2_annotation in tb2_annotations:
                if tb1_annotation != tb2_annotation:
                    print(f'ID: {sent_id}')
                    feat_d1 = dict([f.split('=') for f in tb1_annotation.split('|') if f != '_'])
                    feat_d2 = dict([f.split('=') for f in tb2_annotation.split('|') if f != '_'])
                    for k, v in feat_d1.items():
                        if k in feat_d2 and feat_d2[k] != v:
                            print(f'{k}: {v} vs {feat_d2[k]}')
                        else:
                            print(f'{k}: {v} vs _')

if __name__ == '__main__':
    main()