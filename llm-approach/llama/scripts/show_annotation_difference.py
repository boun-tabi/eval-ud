import argparse, json

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t8', '--treebank8', type=str, required=True)
    parser.add_argument('-t11', '--treebank11', type=str, required=True)
    parser.add_argument('-s', '--sent_id', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    treebank8 = args.treebank8
    treebank11 = args.treebank11
    sent_id = args.sent_id
    with open(treebank8, 'r', encoding='utf-8') as f:
        t8_data = json.load(f)
    table8 = t8_data[sent_id]['table']
    with open(treebank11, 'r', encoding='utf-8') as f:
        t11_data = json.load(f)
    table11 = t11_data[sent_id]['table']

    for line in table8.split('\n'):
        ...
    
if __name__ == '__main__':
    main()