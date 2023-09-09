import json, argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--treebank', type=str, required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    treebank = args.treebank
    with open(treebank, encoding='utf-8') as f:
        tb_l = json.load(f)
    
    split_sent_count = 0
    split_form_count = 0
    # Count the number of sentences with splits and splits themselves
    for sent in tb_l:
        table = sent['table']
        split_exists = False
        for row in table.split('\n'):
            fields = row.split('\t')
            id_t = fields[0]
            if '-' in id_t:
                split_exists = True
                split_form_count += 1
        if split_exists:
            split_sent_count += 1
    print('Number of sentences with splits: {}'.format(split_sent_count))
    print('Number of splits: {}'.format(split_form_count))
    print('Total number of sentences: {}'.format(len(tb_l)))
    print('Percentage of sentences with splits: {:.2f}%'.format(split_sent_count / len(tb_l) * 100))

if __name__ == '__main__':
    main()

# v2.8:
#     Number of sentences with splits: 1043
#     Number of splits: 1163
#     Total number of sentences: 9761
#     Percentage of sentences with splits: 10.69%
# v2.11:
#     Number of sentences with splits: 2782
#     Number of splits: 3374
#     Total number of sentences: 9761
#     Percentage of sentences with splits: 28.50%