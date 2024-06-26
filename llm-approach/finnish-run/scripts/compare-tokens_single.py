import argparse
from spacy.lang.en import English

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s1', '--sentence1', type=str, required=True)
    parser.add_argument('-s2', '--sentence2', type=str, required=True)
    return parser.parse_args()

def get_matches(tokens1, tokens2):
    match_count = 0
    matches = []
    tokens2_matched = {i: False for i in range(len(tokens2))}
    for i, token1 in enumerate(tokens1):
        for j, token2 in enumerate(tokens2):
            if tokens2_matched[j]:
                continue
            if token1 == token2:
                match_count += 1
                tokens2_matched[j] = True
                matches.append({'token': token1, 'idx1': i, 'idx2': j})
                break
    return match_count, matches

def main():
    args = get_args()

    sent1, sent2 = args.sentence1, args.sentence2

    nlp = English()
    tokenizer = nlp.tokenizer

    sent1_tokens = []
    for token in tokenizer(sent1):
        sent1_tokens.append(token.text)
    sent2_tokens = []
    for token in tokenizer(sent2):
        sent2_tokens.append(token.text)
    match_count, matches = get_matches(sent1_tokens, sent2_tokens)
    print(f'Match count: {match_count}')
    print('Matches:')
    for match in matches:
        print(f'{match["token"]} ({match["idx1"]}, {match["idx2"]})')
    token_accuracy = 2 * match_count / (len(sent1_tokens) + len(sent2_tokens))
    print(f'Token accuracy: {token_accuracy:.3f}')

if __name__ == '__main__':
    main()
