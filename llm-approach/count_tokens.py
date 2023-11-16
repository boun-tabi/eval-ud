import os, json, argparse
from spacy.lang.tr import Turkish
from spacy.tokenizer import Tokenizer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str, required=True)
    parser.add_argument('-s', '--sentence-ids', type=str, required=True)
    args = parser.parse_args()

    tb_d = {}
    with open(args.treebank, 'r') as f:
        tb_data = json.load(f)
    for key, elem in tb_data.items():
        tb_d[key] = elem['text']
    
    with open(args.sentence_ids, 'r') as f:
        sentence_ids = json.load(f)
    
    nlp = Turkish()
    tokenizer = nlp.tokenizer

    all_token_count = 0
    for sent_id in sentence_ids:
        text = tb_d[sent_id]
        current_token_count = len(tokenizer(text))
        print(sent_id, current_token_count)
        all_token_count += current_token_count

    print(all_token_count)

if __name__ == '__main__':
    main()

# 6247 for the selected sentences