import argparse
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s1', '--sentence1', type=str, required=True)
    parser.add_argument('-s2', '--sentence2', type=str, required=True)
    return parser.parse_args()

def get_matches(original_tokens, generated_tokens):
    match_generated_d = {}
    for i, token in enumerate(original_tokens):
        ratios = [fuzz.ratio(token, generated_tokens[k]) for k in range(3) if k < len(generated_tokens)]
        max_ratio = max(ratios)
        max_index = ratios.index(max_ratio)
        match_generated_d[i] = generated_tokens[max_index]
        if len(generated_tokens) > len(original_tokens) - i:
            generated_tokens = generated_tokens[1:]
    matches = [(original_tokens[i], match_generated_d[i]) for i in range(len(original_tokens))]
    return matches

def get_correct_all(matches):
    correct, all = 0, 0
    for original, match in matches:
        if original == match:
            correct += 1
        all += 1
    return correct, all

def main():
    args = get_args()

    sent1, sent2 = args.sentence1, args.sentence2

    from spacy.lang.en import English
    nlp = English()
    tokenizer = nlp.tokenizer

    sent1_tokens = []
    for token in tokenizer(sent1):
        sent1_tokens.append(token.text)
    sent2_tokens = []
    for token in tokenizer(sent2):
        sent2_tokens.append(token.text)
    original_matches = get_matches(sent2_tokens, sent1_tokens)
    original_correct, original_all = get_correct_all(original_matches)
    recall = original_correct / original_all
    generated_matches = get_matches(sent1_tokens, sent2_tokens)
    generated_correct, generated_all = get_correct_all(generated_matches)
    precision = generated_correct / generated_all
    f1 = 2 * (precision * recall) / (precision + recall)

    print(f'Recall: {recall}')
    print(f'Precision: {precision}')
    print(f'F1: {f1}')

if __name__ == '__main__':
    main()
