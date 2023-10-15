import os, json, argparse
from matplotlib import pyplot as plt

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--sent-ids', type=str, help='Path to the file containing the sentence ids')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the file containing the sentences')
    parser.add_argument('-n', '--note', type=str, required=True, help='Note to be added to the output file')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tb_d = {}
    for el in data:
        tb_d[el['sent_id']] = el['table']
    
    if args.sent_ids:
        with open(args.sent_ids, 'r', encoding='utf-8') as f:
            sent_ids = json.load(f)
    else:
        sent_ids = list(tb_d.keys())

    token_len_l = []
    for sent_id in sent_ids:
        table = tb_d[sent_id] 
        lines = table.split('\n')
        last_line = lines[-1]
        last_id = last_line.split('\t')[0]
        token_len_l.append(int(last_id))

    plt.hist(token_len_l, bins=100, color='green', alpha=0.8)
    plt.savefig(os.path.join(THIS_DIR, 'token_len_distribution-{}.png'.format(args.note)))

if __name__ == '__main__':
    main()
