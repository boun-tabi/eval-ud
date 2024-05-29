import json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--summary', type=str, required=True, help='Summary file')
    return parser.parse_args()

def get_matches(tokens1, tokens2):
    idx1, idx2 = 0, 0
    match_count = 0
    matches = []
    while True:
        if idx1 >= len(tokens1) or idx2 >= len(tokens2):
            break
        if tokens1[idx1] == tokens2[idx2]:
            match_count += 1
            matches.append({
                'token': tokens1[idx1],
                'idx1': idx1,
                'idx2': idx2
            })
            idx1 += 1
            idx2 += 1
        else:
            idx2 += 1
    return match_count, matches    

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
    md_file = dir / 'md.json'
    with md_file.open('r', encoding='utf-8') as f:
        md = json.load(f)
    language = md['language']

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    if language == 'tr':
        from spacy.lang.tr import Turkish
        nlp = Turkish()
    elif language == 'eu':
        from spacy.lang.eu import Basque
        nlp = Basque()
    elif language == 'fi':
        from spacy.lang.fi import Finnish
        nlp = Finnish()
    elif language == 'ga':
        from spacy.lang.ga import Irish
        nlp = Irish()
    elif language == 'hi':
        from spacy.lang.hi import Hindi
        nlp = Hindi()
    elif language == 'zh':
        from spacy.lang.zh import Chinese
        nlp = Chinese()
    else:
        from spacy.lang.en import English
        nlp = English()
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
        match_count, _ = get_matches(original_tokens, llm_tokens)
        accuracy = 2 * match_count / (len(original_tokens) + len(llm_tokens))
        comparison_d[sent_id]['llm']['accuracy'] = accuracy

    analysis_d = {
        'comparison_d':
            comparison_d,
        'summary': {
            'llm accuracy': accuracy
        }
    }

    for sent_id, value in comparison_d.items():
        analysis_d['summary']['llm accuracy'] += value['llm']['accuracy']
    analysis_d['summary']['llm accuracy'] /= len(comparison_d)

    path = dir / (summary_path.stem + '-comparison.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
