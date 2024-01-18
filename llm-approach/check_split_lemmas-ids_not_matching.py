import argparse, json

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t8', '--treebank8', type=str, required=True, help='Path to the treebank v2.8 file')
    parser.add_argument('-t11', '--treebank11', type=str, required=True, help='Path to the treebank v2.11 file')
    parser.add_argument('-t', '--tokens', type=str, required=True, help='Path to the tokens file')
    return parser.parse_args()

def main():
    args = get_args()

    # Get the tokens
    with open(args.tokens, 'r') as f:
        tokens = json.load(f)
    
    # Get the treebank files
    with open(args.treebank8, 'r') as f:
        treebank8 = json.load(f)
    with open(args.treebank11, 'r') as f:
        treebank11 = json.load(f)

    for sent_id in tokens:
        table8, table11 = treebank8[sent_id]['table'], treebank11[sent_id]['table']
        token_ids = [int(i) for i in tokens[sent_id]]
        highest_id = max(token_ids)
        first_split = None
        forms8, forms11 = {}, {}
        for line in table8.split('\n'):
            fields = line.split('\t')
            id_t, form_t = fields[0], fields[1]
            forms8[id_t] = form_t
            if '-' in id_t:
                split_number = int(id_t.split('-')[0])
                if first_split is None:
                    first_split = split_number
                elif split_number < first_split:
                    first_split = split_number
        for line in table11.split('\n'):
            fields = line.split('\t')
            id_t, form_t = fields[0], fields[1]
            forms11[id_t] = form_t
            if '-' in id_t:
                split_number = int(id_t.split('-')[0])
                if first_split is None:
                    first_split = split_number
                elif split_number < first_split:
                    first_split = split_number
        # if first_split and first_split < highest_id:
        #     print(sent_id)
        for token_id in token_ids:
            token_id = str(token_id)
            if token_id not in forms8 or token_id not in forms11:
                # print(sent_id)
                print(sent_id, token_id)
                # break
            # elif forms8[token_id] != forms11[token_id]:
                # print(sent_id)
                # print(sent_id, token_id, forms8[token_id], forms11[token_id])
                # break

if __name__ == '__main__':
    main()