import json, argparse, random
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-m', '--manual', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    return parser.parse_args()

def get_accuracy(original_tokens, compared_text, tokenizer):
    original_tokens_len = len(original_tokens)
    compared_tokens = []
    for token in tokenizer(compared_text):
        compared_tokens.append(token.text)
    match_d = {}
    compared_tokens_len = len(compared_tokens)
    for i, token in enumerate(original_tokens):
        compared_tokens_len = len(compared_tokens)
        if compared_tokens_len == 0:
            break
        elif compared_tokens_len == 1:
            match_d[i] = compared_tokens[0]
        elif compared_tokens_len == 2:
            ratio1, ratio2 = fuzz.ratio(token, compared_tokens[0]), fuzz.ratio(token, compared_tokens[1])
            if ratio1 > ratio2:
                match_d[i] = compared_tokens[0]
            else:
                match_d[i] = compared_tokens[1]
        elif compared_tokens_len > 2:
            first_three_items = compared_tokens[:3]
            ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
            max_ratio = max(ratio1, ratio2, ratio3)
            if max_ratio == ratio1:
                match_d[i] = compared_tokens[0]
            elif max_ratio == ratio2:
                match_d[i] = compared_tokens[1]
            else:
                match_d[i] = compared_tokens[2]
        if len(compared_tokens) > original_tokens_len - i:
            compared_tokens = compared_tokens[1:]
    correct, all = 0, 0
    for i, token in enumerate(original_tokens):
        compared_token = match_d[i]
        if token == compared_token:
            correct += 1
        all += 1
    return correct, all

def main():
    args = get_args()

    llm_dir = Path(args.llm_dir)
    version1 = args.version1
    version2 = args.version2
    if llm_dir / '{}_output-cleaned.json'.format(version1) in llm_dir.iterdir():
        file1 = llm_dir / '{}_output-cleaned.json'.format(version1)
        file2 = llm_dir / '{}_output-cleaned.json'.format(version2)
    else:
        file1 = llm_dir / '{}_output.json'.format(version1)
        file2 = llm_dir / '{}_output.json'.format(version2)
    with open(file1, 'r', encoding='utf-8') as f:
        v1_llm = json.load(f)
    with open(file2, 'r', encoding='utf-8') as f:
        v2_llm = json.load(f)
    sent_ids = list(v1_llm.keys())
    random.seed(42)
    random.shuffle(sent_ids)
    sent_ids = sent_ids[:50]
    
    manual = Path(args.manual)
    with open(manual, 'r', encoding='utf-8') as f:
        manual_d = json.load(f)
    people = list(manual_d.keys())

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    comparison_d = {sent_id: {'llm': {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}}, 'manual': {person: {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}} for person in people}} for sent_id in sent_ids}
    for sent_id in sent_ids:
        original_text = v1_llm[sent_id]['original_text']
        text_v1_llm, text_v2_llm = v1_llm[sent_id]['output_text'], v2_llm[sent_id]['output_text']
        person1, person2 = people[0], people[1]
        text_v1_manual_person1, text_v2_manual_person1 = manual_d[person1][version1][sent_id], manual_d[person1][version2][sent_id]
        text_v1_manual_person2, text_v2_manual_person2 = manual_d[person2][version1][sent_id], manual_d[person2][version2][sent_id]
        if text_v1_llm[0] == '"' and text_v1_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v1_llm = text_v1_llm[1:-1]
        if text_v2_llm[0] == '"' and text_v2_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_llm = text_v2_llm[1:-1]

        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        v1_llm_correct, v1_llm_all = get_accuracy(original_tokens, text_v1_llm, tokenizer)
        v2_llm_correct, v2_llm_all = get_accuracy(original_tokens, text_v2_llm, tokenizer)
        v1_manual_person1_correct, v1_manual_person1_all = get_accuracy(original_tokens, text_v1_manual_person1, tokenizer)
        v2_manual_person1_correct, v2_manual_person1_all = get_accuracy(original_tokens, text_v2_manual_person1, tokenizer)
        v1_manual_person2_correct, v1_manual_person2_all = get_accuracy(original_tokens, text_v1_manual_person2, tokenizer)
        v2_manual_person2_correct, v2_manual_person2_all = get_accuracy(original_tokens, text_v2_manual_person2, tokenizer)
        
        comparison_d[sent_id]['llm'][version1]['correct'] = v1_llm_correct
        comparison_d[sent_id]['llm'][version1]['all'] = v1_llm_all
        comparison_d[sent_id]['llm'][version2]['correct'] = v2_llm_correct
        comparison_d[sent_id]['llm'][version2]['all'] = v2_llm_all
        comparison_d[sent_id]['manual'][person1][version1]['correct'] = v1_manual_person1_correct
        comparison_d[sent_id]['manual'][person1][version1]['all'] = v1_manual_person1_all
        comparison_d[sent_id]['manual'][person1][version2]['correct'] = v2_manual_person1_correct
        comparison_d[sent_id]['manual'][person1][version2]['all'] = v2_manual_person1_all
        comparison_d[sent_id]['manual'][person2][version1]['correct'] = v1_manual_person2_correct
        comparison_d[sent_id]['manual'][person2][version1]['all'] = v1_manual_person2_all
        comparison_d[sent_id]['manual'][person2][version2]['correct'] = v2_manual_person2_correct
        comparison_d[sent_id]['manual'][person2][version2]['all'] = v2_manual_person2_all

    accuracies = {'llm': {version1: {'accuracy': None}, version2: {'accuracy': None}}, 'manual': {person: {version1: {'accuracy': None}, version2: {'accuracy': None}} for person in people}}
    v1_llm_accuracy = sum([comparison_d[sent_id]['llm'][version1]['correct'] for sent_id in sent_ids]) / sum([comparison_d[sent_id]['llm'][version1]['all'] for sent_id in sent_ids])
    v2_llm_accuracy = sum([comparison_d[sent_id]['llm'][version2]['correct'] for sent_id in sent_ids]) / sum([comparison_d[sent_id]['llm'][version2]['all'] for sent_id in sent_ids])
    accuracies['llm'][version1]['accuracy'] = v1_llm_accuracy
    accuracies['llm'][version2]['accuracy'] = v2_llm_accuracy
    for person in people:
        v1_manual_accuracy = sum([comparison_d[sent_id]['manual'][person][version1]['correct'] for sent_id in sent_ids]) / sum([comparison_d[sent_id]['manual'][person][version1]['all'] for sent_id in sent_ids])
        v2_manual_accuracy = sum([comparison_d[sent_id]['manual'][person][version2]['correct'] for sent_id in sent_ids]) / sum([comparison_d[sent_id]['manual'][person][version2]['all'] for sent_id in sent_ids])
        accuracies['manual'][person][version1]['accuracy'] = v1_manual_accuracy
        accuracies['manual'][person][version2]['accuracy'] = v2_manual_accuracy

    with open(llm_dir / 'manual-llm-accuracies.json', 'w', encoding='utf-8') as f:
        json.dump(accuracies, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
