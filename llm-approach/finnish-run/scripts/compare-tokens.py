import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--summary', type=str, required=True, help='Summary file')
    return parser.parse_args()

def get_matches(original_tokens, generated_tokens):
    match_generated_d = {}
    for i, token in enumerate(original_tokens):
        for j in range(1, 3):
            ratios = [fuzz.ratio(token, generated_tokens[k]) for k in range(j) if k < len(generated_tokens)]
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

    summary_path = Path(args.summary)
    dir = summary_path.parent
    with summary_path.open('r', encoding='utf-8') as f:
        summary = json.load(f)

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    comparison_d = {}
    for sent_id, value in results.items():
        comparison_d[sent_id] = { 'llm': {} }
        original_text, text_llm = value['original text'], value['output text']

        llm_tokens = []
        for token in tokenizer(text_llm):
            llm_tokens.append(token.text)
        original_tokens = []
        for token in tokenizer(original_text):
            original_tokens.append(token.text)
        original_matches = get_matches(original_tokens, llm_tokens)
        original_correct, original_all = get_correct_all(original_matches)
        recall = original_correct / original_all
        generated_matches = get_matches(llm_tokens, original_tokens)
        generated_correct, generated_all = get_correct_all(generated_matches)
        precision = generated_correct / generated_all

        comparison_d[sent_id]['llm']['precision'] = precision
        comparison_d[sent_id]['llm']['recall'] = recall

    analysis_d = {
        'comparison_d':
            comparison_d,
        'summary': {
            'llm accuracy': {'f1': 0, 'precision': 0, 'recall': 0}
        }
    }

    for sent_id, value in comparison_d.items():
        precision = value['llm']['precision']
        recall = value['llm']['recall']
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        analysis_d['summary']['llm accuracy']['f1'] += f1
        analysis_d['summary']['llm accuracy']['precision'] += precision
        analysis_d['summary']['llm accuracy']['recall'] += recall
    analysis_d['summary']['llm accuracy']['f1'] /= len(comparison_d)
    analysis_d['summary']['llm accuracy']['precision'] /= len(comparison_d)
    analysis_d['summary']['llm accuracy']['recall'] /= len(comparison_d)

    path = dir / (summary_path.stem + '-comparison.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
