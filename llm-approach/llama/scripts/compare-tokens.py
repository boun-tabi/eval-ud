import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    return parser.parse_args()

def main():
    args = get_args()

    dir = Path(args.directory)
    summary_path = dir / 'summary.json'
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    comparison_d = {}
    for sent_id, value in results.items():
        comparison_d[sent_id] = {
            'v2.8 llm':
                {'correct': 0, 'all': 0},
            'v2.11 llm':
                {'correct': 0, 'all': 0}
        }
        original_text, text_v2_8_llm, text_v2_11_llm = value['original text'], value['v2.8 text'], value['v2.11 text']
        if text_v2_8_llm[0] == '"' and original_text[0] != '"':
            text_v2_8_llm = text_v2_8_llm[1:]
        if text_v2_8_llm[-1] == '"' and original_text[-1] != '"':
            text_v2_8_llm = text_v2_8_llm[:-1]
        if text_v2_11_llm[0] == '"' and original_text[0] != '"':
            text_v2_11_llm = text_v2_11_llm[1:]
        if text_v2_11_llm[-1] == '"' and original_text[-1] != '"':
            text_v2_11_llm = text_v2_11_llm[:-1]

        v2_8_llm_tokens = []
        for token in tokenizer(text_v2_8_llm):
            v2_8_llm_tokens.append(token.text)
        v2_11_llm_tokens = []
        for token in tokenizer(text_v2_11_llm):
            v2_11_llm_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        match_llm_v2_8_d, match_llm_v2_11_d = {}, {}
        original_tokens_len = len(original_tokens)
        for i, token in enumerate(original_tokens):
            v2_8_llm_tokens_len = len(v2_8_llm_tokens)
            if v2_8_llm_tokens_len == 0:
                break
            elif v2_8_llm_tokens_len == 1:
                match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
            elif v2_8_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_8_llm_tokens[0]), fuzz.ratio(token, v2_8_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
                else:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[1]
            elif v2_8_llm_tokens_len > 2:
                first_three_items = v2_8_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[1]
                else:
                    match_llm_v2_8_d[i] = v2_8_llm_tokens[2]
            if len(v2_8_llm_tokens) > original_tokens_len - i:
                v2_8_llm_tokens = v2_8_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_8_llm_token = match_llm_v2_8_d[i]
            if token == v2_8_llm_token:
                comparison_d[sent_id]['v2.8 llm']['correct'] += 1
            comparison_d[sent_id]['v2.8 llm']['all'] += 1

        for i, token in enumerate(original_tokens):
            v2_11_llm_tokens_len = len(v2_11_llm_tokens)
            if v2_11_llm_tokens_len == 0:
                break
            elif v2_11_llm_tokens_len == 1:
                match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
            elif v2_11_llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, v2_11_llm_tokens[0]), fuzz.ratio(token, v2_11_llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
                else:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[1]
            elif v2_11_llm_tokens_len > 2:
                first_three_items = v2_11_llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[1]
                else:
                    match_llm_v2_11_d[i] = v2_11_llm_tokens[2]
            if len(v2_11_llm_tokens) > original_tokens_len - i:
                v2_11_llm_tokens = v2_11_llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            v2_11_llm_token = match_llm_v2_11_d[i]
            if token == v2_11_llm_token:
                comparison_d[sent_id]['v2.11 llm']['correct'] += 1
            comparison_d[sent_id]['v2.11 llm']['all'] += 1
        pass

    analysis_d = {
        'comparison_d': 
            comparison_d, 
        'summary': {
            'v2.8 llm ratio': 0, 
            'v2.11 llm ratio': 0
        }
    }
    for sent_id, value in comparison_d.items():
        v2_8_llm_ratio = value['v2.8 llm']['correct'] / value['v2.8 llm']['all']
        v2_11_llm_ratio = value['v2.11 llm']['correct'] / value['v2.11 llm']['all']
        analysis_d['summary']['v2.8 llm ratio'] += v2_8_llm_ratio
        analysis_d['summary']['v2.11 llm ratio'] += v2_11_llm_ratio
    analysis_d['summary']['v2.8 llm ratio'] /= len(comparison_d)
    analysis_d['summary']['v2.11 llm ratio'] /= len(comparison_d)

    path = dir / 'comparison-tokens.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
