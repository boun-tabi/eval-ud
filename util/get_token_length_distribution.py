import os, json, argparse
from matplotlib import pyplot as plt

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the file containing the sentences')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_len_l = []
    for el in data:
        table = el['table']
        lines = table.split('\n')
        last_line = lines[-1]
        last_id = last_line.split('\t')[0]
        token_len_l.append(int(last_id))

    plt.hist(token_len_l, bins=100, color='green', alpha=0.8)
    plt.savefig(os.path.join(THIS_DIR, 'token_len_distribution.png'))

if __name__ == '__main__':
    main()
