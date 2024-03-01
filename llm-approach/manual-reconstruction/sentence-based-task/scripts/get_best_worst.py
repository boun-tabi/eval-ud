import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    return parser.parse_args()

def get_accuracy(original_text, output_text, tokenizer):
    original_tokens = []
    for token in tokenizer(original_text):
        original_tokens.append(token.text)
    output_tokens = []
    for token in tokenizer(output_text):
        output_tokens.append(token.text)
    match_d = {}
    original_tokens_len = len(original_tokens)
    for i, token in enumerate(original_tokens):
        output_tokens_len = len(output_tokens)
        if output_tokens_len == 0:
            break
        elif output_tokens_len == 1:
            match_d[i] = output_tokens[0]
        elif output_tokens_len == 2:
            ratio1, ratio2 = fuzz.ratio(token, output_tokens[0]), fuzz.ratio(token, output_tokens[1])
            if ratio1 > ratio2:
                match_d[i] = output_tokens[0]
            else:
                match_d[i] = output_tokens[1]
        elif output_tokens_len > 2:
            first_three_items = output_tokens[:3]
            ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
            max_ratio = max(ratio1, ratio2, ratio3)
            if max_ratio == ratio1:
                match_d[i] = output_tokens[0]
            elif max_ratio == ratio2:
                match_d[i] = output_tokens[1]
            else:
                match_d[i] = output_tokens[2]
        if len(output_tokens) > original_tokens_len - i:
            output_tokens = output_tokens[1:]
    correct = 0
    for i, token in enumerate(original_tokens):
        output_token = match_d[i]
        if token == output_token:
            correct += 1
    return correct, len(original_tokens)

def get_best_worst(accuracies, output_d, type_t):
    accuracies.sort(reverse=True)
    best_l, worst_l = [], []
    for i, (accuracy, sent_id, version) in enumerate(accuracies):
        if i < 10 or i >= len(accuracies) - 10:
            d = {'sent_id': sent_id, 'version': version, 'accuracy': accuracy, 'original_text': output_d[sent_id]['original_text'], version: output_d[sent_id][type_t][version]}
            if i < 10:
                best_l.append(d)
            else:
                worst_l.append(d)
    return best_l, worst_l

def main():
    args = get_args()

    constructions = Path(args.constructions)
    with open(constructions, 'r', encoding='utf-8') as f:
        constructions_d = json.load(f)

    person1, person2 = args.person1, args.person2

    llm_dir = Path(args.llm_dir)
    version1, version2 = args.version1, args.version2

    if llm_dir / '{}_output-cleaned.json'.format(version1) not in llm_dir.iterdir():
        file1, file2 = '{}_output.json'.format(version1), '{}_output.json'.format(version2)
    else:
        file1, file2 = '{}_output-cleaned.json'.format(version1), '{}_output-cleaned.json'.format(version2)

    with open(llm_dir / file1, 'r', encoding='utf-8') as f:
        v1_output = json.load(f)
    with open(llm_dir / file2, 'r', encoding='utf-8') as f:
        v2_output = json.load(f)
    output_d = {}
    sent_ids = list(constructions_d[person1][version1].keys())
    for sent_id in sent_ids:
        original_text = v1_output[sent_id]['original_text']
        v1_llm = v1_output[sent_id]['output_text']
        v2_llm = v2_output[sent_id]['output_text']
        v1_p1 = constructions_d[person1][version1][sent_id]
        v2_p1 = constructions_d[person1][version2][sent_id]
        v1_p2 = constructions_d[person2][version1][sent_id]
        v2_p2 = constructions_d[person2][version2][sent_id]
        output_d[sent_id] = {'original_text': original_text, 'llm': {version1: v1_llm, version2: v2_llm}, person1: {version1: v1_p1, version2: v1_p2}, person2: {version1: v2_p1, version2: v2_p2}}

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    comparison_d = {sent_id: {'llm': {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}}, person1: {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}}, person2: {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}}} for sent_id in sent_ids}
    for sent_id in sent_ids:
        original_text, text_v1_llm, text_v2_llm = output_d[sent_id]['original_text'], output_d[sent_id]['llm'][version1], output_d[sent_id]['llm'][version2]
        if text_v1_llm[0] == '"' and text_v1_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v1_llm = text_v1_llm[1:-1]
        if text_v2_llm[0] == '"' and text_v2_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_llm = text_v2_llm[1:-1]
        text_v1_p1, text_v2_p1 = output_d[sent_id][person1][version1], output_d[sent_id][person1][version2]
        text_v1_p2, text_v2_p2 = output_d[sent_id][person2][version1], output_d[sent_id][person2][version2]

        comparison_d[sent_id]['llm'][version1]['correct'], comparison_d[sent_id]['llm'][version1]['all'] = get_accuracy(original_text, text_v1_llm, tokenizer)
        comparison_d[sent_id]['llm'][version2]['correct'], comparison_d[sent_id]['llm'][version2]['all'] = get_accuracy(original_text, text_v2_llm, tokenizer)
        comparison_d[sent_id][person1][version1]['correct'], comparison_d[sent_id][person1][version1]['all'] = get_accuracy(original_text, text_v1_p1, tokenizer)
        comparison_d[sent_id][person1][version2]['correct'], comparison_d[sent_id][person1][version2]['all'] = get_accuracy(original_text, text_v2_p1, tokenizer)
        comparison_d[sent_id][person2][version1]['correct'], comparison_d[sent_id][person2][version1]['all'] = get_accuracy(original_text, text_v1_p2, tokenizer)
        comparison_d[sent_id][person2][version2]['correct'], comparison_d[sent_id][person2][version2]['all'] = get_accuracy(original_text, text_v2_p2, tokenizer)

    p1_accuracies, p2_accuracies, llm_accuracies = [], [], []
    for sent_id in sent_ids:
        for type_t in ['llm', person1, person2]:
            for version in [version1, version2]:
                accuracy = comparison_d[sent_id][type_t][version]['correct'] / comparison_d[sent_id][type_t][version]['all']
                if type_t == 'llm':
                    llm_accuracies.append((accuracy, sent_id, version))
                elif type_t == person1:
                    p1_accuracies.append((accuracy, sent_id, version))
                else:
                    p2_accuracies.append((accuracy, sent_id, version))

    best_worst_d = {'llm': {'best': [], 'worst': []}, person1: {'best': [], 'worst': []}, person2: {'best': [], 'worst': []}}
    best_worst_d['llm']['best'], best_worst_d['llm']['worst'] = get_best_worst(llm_accuracies, output_d, 'llm')
    best_worst_d[person1]['best'], best_worst_d[person1]['worst'] = get_best_worst(p1_accuracies, output_d, person1)
    best_worst_d[person2]['best'], best_worst_d[person2]['worst'] = get_best_worst(p2_accuracies, output_d, person2)

    with open(llm_dir / 'best-worst.json', 'w', encoding='utf-8') as f:
        json.dump(best_worst_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
