import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    parser.add_argument('-s', '--summary', type=str, required=True, help='Summary file')
    return parser.parse_args()

def main():
    args = get_args()

    dir = Path(args.directory)
    summary_path = Path(args.summary)
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
        comparison_d[sent_id] = { 'llm': {'correct': 0, 'all': 0} }
        original_text, text_llm = value['original text'], value['output text']
        if text_llm[0] == '"' and original_text[0] != '"':
            text_llm = text_llm[1:]
        if text_llm[-1] == '"' and original_text[-1] != '"':
            text_llm = text_llm[:-1]

        llm_tokens = []
        for token in tokenizer(text_llm):
            llm_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        match_llm_d = {}
        original_tokens_len = len(original_tokens)
        for i, token in enumerate(original_tokens):
            llm_tokens_len = len(llm_tokens)
            if llm_tokens_len == 0:
                break
            elif llm_tokens_len == 1:
                match_llm_d[i] = llm_tokens[0]
            elif llm_tokens_len == 2:
                ratio1, ratio2 = fuzz.ratio(token, llm_tokens[0]), fuzz.ratio(token, llm_tokens[1])
                if ratio1 > ratio2:
                    match_llm_d[i] = llm_tokens[0]
                else:
                    match_llm_d[i] = llm_tokens[1]
            elif llm_tokens_len > 2:
                first_three_items = llm_tokens[:3]
                ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
                max_ratio = max(ratio1, ratio2, ratio3)
                if max_ratio == ratio1:
                    match_llm_d[i] = llm_tokens[0]
                elif max_ratio == ratio2:
                    match_llm_d[i] = llm_tokens[1]
                else:
                    match_llm_d[i] = llm_tokens[2]
            if len(llm_tokens) > original_tokens_len - i:
                llm_tokens = llm_tokens[1:]

        for i, token in enumerate(original_tokens):
            llm_token = match_llm_d[i]
            if token == llm_token:
                comparison_d[sent_id]['llm']['correct'] += 1
            comparison_d[sent_id]['llm']['all'] += 1

    analysis_d = {
        'comparison_d':
            comparison_d,
        'summary': {
            'llm ratios': {'per token': 0, 'per sentence': 0}
        }
    }
    all_token_count, correct_token_count = 0, 0
    for sent_id, value in comparison_d.items():
        llm_ratio = value['llm']['correct'] / value['llm']['all']
        correct_token_count += value['llm']['correct']
        all_token_count += value['llm']['all']
        analysis_d['summary']['llm ratios']['per sentence'] += llm_ratio
    analysis_d['summary']['llm ratios']['per token'] = correct_token_count / all_token_count
    analysis_d['summary']['llm ratios']['per sentence'] /= len(comparison_d)

    path = dir / (summary_path.stem + '-comparison.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
