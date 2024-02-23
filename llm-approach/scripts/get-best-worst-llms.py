import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()

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
    sent_ids = list(v1_output.keys())
    for sent_id in sent_ids:
        original_text = v1_output[sent_id]['original_text']
        v1_llm = v1_output[sent_id]['output_text']
        v2_llm = v2_output[sent_id]['output_text']
        output_d[sent_id] = {'original_text': original_text, version1: v1_llm, version2: v2_llm}
    
    nlp = Turkish()
    tokenizer = nlp.tokenizer

    comparison_d = {sent_id: {version1: {'correct': 0, 'all': 0}, version2: {'correct': 0, 'all': 0}} for sent_id in sent_ids}
    for sent_id in sent_ids:
        original_text, text_v1_llm, text_v2_llm = output_d[sent_id]['original_text'], output_d[sent_id][version1], output_d[sent_id][version2]
        if text_v1_llm[0] == '"' and text_v1_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v1_llm = text_v1_llm[1:-1]
        if text_v2_llm[0] == '"' and text_v2_llm[-1] == '"' and original_text[0] != '"' and original_text[-1] != '"':
            text_v2_llm = text_v2_llm[1:-1]

        v1_llm_tokens = []
        for token in tokenizer(text_v1_llm):
            v1_llm_tokens.append(token.text)
        v2_llm_tokens = []
        for token in tokenizer(text_v2_llm):
            v2_llm_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        match_llm_v1_d, match_llm_v2_d = {}, {}
        original_tokens_len = len(original_tokens)
        for i, token in enumerate(original_tokens):
            v1_llm_tokens_len = len(v1_llm_tokens)
            if v1_llm_tokens_len == 0:
                break
            elif v1_llm_tokens_len == 1:
                match_llm_v1_d[i] = v1_llm_tokens[0]
            elif v1_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v1_llm_tokens[0]), fuzz.ratio(token, v1_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v1_d[i] = v1_llm_tokens[0]
                else:
                    match_llm_v1_d[i] = v1_llm_tokens[1]
            elif v1_llm_tokens_len > 2:
                first_three_items = v1_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v1_d[i] = v1_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v1_d[i] = v1_llm_tokens[1]
                else:
                    match_llm_v1_d[i] = v1_llm_tokens[2]
            if len(v1_llm_tokens) > original_tokens_len - i:
                v1_llm_tokens = v1_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v1_llm_token = match_llm_v1_d[i]
            if token == v1_llm_token:
                comparison_d[sent_id][version1]['correct'] += 1
            comparison_d[sent_id][version1]['all'] += 1
        
        for i, token in enumerate(original_tokens):
            v2_llm_tokens_len = len(v2_llm_tokens)
            if v2_llm_tokens_len == 0:
                break
            elif v2_llm_tokens_len == 1:
                match_llm_v2_d[i] = v2_llm_tokens[0]
            elif v2_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_llm_tokens[0]), fuzz.ratio(token, v2_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v2_d[i] = v2_llm_tokens[0]
                else:
                    match_llm_v2_d[i] = v2_llm_tokens[1]
            elif v2_llm_tokens_len > 2:
                first_three_items = v2_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v2_d[i] = v2_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v2_d[i] = v2_llm_tokens[1]
                else:
                    match_llm_v2_d[i] = v2_llm_tokens[2]
            if len(v2_llm_tokens) > original_tokens_len - i:
                v2_llm_tokens = v2_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_llm_token = match_llm_v2_d[i]
            if token == v2_llm_token:
                comparison_d[sent_id][version2]['correct'] += 1
            comparison_d[sent_id][version2]['all'] += 1
    
    accuracies = []
    for sent_id in sent_ids:
        accuracy1 = comparison_d[sent_id][version1]['correct'] / comparison_d[sent_id][version1]['all']
        accuracies.append((accuracy1, sent_id, version1))
        accuracy2 = comparison_d[sent_id][version2]['correct'] / comparison_d[sent_id][version2]['all']
        accuracies.append((accuracy2, sent_id, version2))
    
    accuracies.sort(reverse=True)
    best_worst_llms = {'best': [], 'worst': []}
    for i, (accuracy, sent_id, version) in enumerate(accuracies):
        if i < 10 or i >= len(accuracies) - 10:
            d = {'sent_id': sent_id, 'version': version, 'accuracy': accuracy, 'original_text': output_d[sent_id]['original_text'], version: output_d[sent_id][version]}
            if i < 10:
                best_worst_llms['best'].append(d)
            else:
                best_worst_llms['worst'].append(d)
    
    with open(llm_dir / 'best-worst-llms.json', 'w', encoding='utf-8') as f:
        json.dump(best_worst_llms, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
