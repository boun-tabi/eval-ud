import argparse, json, os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t8', '--treebank8', required=True, help='Path to treebank v2.8')
    parser.add_argument('-t11', '--treebank11', required=True, help='Path to treebank v2.11')
    parser.add_argument('-t', '--tokens', required=True, help='Path to the file containing the tokens')
    return parser.parse_args()

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    args = get_args()

    with open(args.treebank8, 'r') as f:
        treebank8 = json.load(f)
    
    with open(args.treebank11, 'r') as f:
        treebank11 = json.load(f)
    
    with open(args.tokens, 'r') as f:
        tokens = json.load(f)
    
    tokens_to_remove = []
    for sent_id in tokens:
        table8, table11 = treebank8[sent_id]['table'], treebank11[sent_id]['table']
        token_ids = tokens[sent_id]
        lines8, lines11 = table8.split('\n'), table11.split('\n')
        for token_8, token_11 in zip(token_ids['v2.8'], token_ids['v2.11']):
            line8 = None
            for line_t in lines8:
                fields_t = line_t.split('\t')
                id_t = fields_t[0]
                if id_t == token_8:
                    line8 = line_t
                    break
            line11 = None
            for line_t in lines11:
                fields_t = line_t.split('\t')
                id_t = fields_t[0]
                if id_t == token_11:
                    line11 = line_t
                    break
            fields8, fields11 = line8.split('\t'), line11.split('\t')
            features8, features11 = fields8[5], fields11[5]
            if features8 == features11:
                tokens_to_remove.append({'sent_id': sent_id, 'token_id': token_8})
    
    for token in tokens_to_remove:
        sent_id, token_id = token['sent_id'], token['token_id']
        idx8 = tokens[sent_id]['v2.8'].index(token_id)
        tokens[sent_id]['v2.8'].remove(token_id)
        tokens[sent_id]['v2.11'].remove(tokens[sent_id]['v2.11'][idx8])
    
    with open(os.path.join(THIS_DIR, 'token_selections_in_both_treebank_versions-filtered.json'), 'w') as f:
        json.dump(tokens, f, indent=4)

if __name__ == '__main__':
    main()
