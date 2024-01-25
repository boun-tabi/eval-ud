import json, argparse
from pathlib import Path
from spacy.lang.tr import Turkish
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    return parser.parse_args()

def get_match_d(original_tokens, llm_tokens):
    original_tokens_len = len(original_tokens)
    match_d = {}
    for i, token in enumerate(original_tokens):
        llm_tokens_len = len(llm_tokens)
        if llm_tokens_len == 0:
            break
        elif llm_tokens_len == 1:
            match_d[i] = llm_tokens[0]
        elif llm_tokens_len == 2:
            ratio1, ratio2 = fuzz.ratio(token, llm_tokens[0]), fuzz.ratio(token, llm_tokens[1])
            if ratio1 > ratio2:
                match_d[i] = llm_tokens[0]
            else:
                match_d[i] = llm_tokens[1]
        elif llm_tokens_len > 2:
            first_three_items = llm_tokens[:3]
            ratio1, ratio2, ratio3 = fuzz.ratio(token, first_three_items[0]), fuzz.ratio(token, first_three_items[1]), fuzz.ratio(token, first_three_items[2])
            max_ratio = max(ratio1, ratio2, ratio3)
            if max_ratio == ratio1:
                match_d[i] = llm_tokens[0]
            elif max_ratio == ratio2:
                match_d[i] = llm_tokens[1]
            else:
                match_d[i] = llm_tokens[2]
        if len(llm_tokens) > original_tokens_len - i:
            llm_tokens = llm_tokens[1:]
    
    return match_d

def main():
    args = get_args()

    dir = Path(args.directory)
    summary_path = dir / 'summary.json'
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    md_path = dir / 'md.json'
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    v28_path = md['v2.8']
    with open(v28_path, 'r', encoding='utf-8') as f:
        v28 = json.load(f)
    v211_path = md['v2.11']
    with open(v211_path, 'r', encoding='utf-8') as f:
        v211 = json.load(f)

    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    token_comparison_d = {}
    lemma_comparison_d = {}
    for sent_id, value in results.items():
        token_comparison_d[sent_id] = {
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

        v28_lemmas = []
        v28_table = v28[sent_id]['table']
        for row in v28_table.split('\n'):
            fields = row.split('\t')
            id_t = fields[0]
            if '-' in id_t:
                continue
            lemma_t = fields[2]
            v28_lemmas.append(lemma_t)
        v211_lemmas = []
        v211_table = v211[sent_id]['table']
        for row in v211_table.split('\n'):
            fields = row.split('\t')
            id_t = fields[0]
            if '-' in id_t:
                continue
            lemma_t = fields[2]
            v211_lemmas.append(lemma_t)

        lemma_comparison_d[sent_id] = {
            'v2.8 llm':
                {'same': 0, 'all': 0},
            'v2.11 llm':
                {'same': 0, 'all': 0}
        }

        v2_8_llm_tokens = [token.text for token in tokenizer(text_v2_8_llm)]
        v2_11_llm_tokens = [token.text for token in tokenizer(text_v2_11_llm)]
        original_tokens = [token.text for token in tokenizer(original_text)]

        match_token_llm_v2_8_d = get_match_d(original_tokens, v2_8_llm_tokens)

        for i, token in enumerate(original_tokens):
            v2_8_llm_token = match_token_llm_v2_8_d[i]
            if token == v2_8_llm_token:
                token_comparison_d[sent_id]['v2.8 llm']['correct'] += 1
            token_comparison_d[sent_id]['v2.8 llm']['all'] += 1

        match_lemma_llm_v2_8_d = get_match_d(v28_lemmas, v2_8_llm_tokens)

        for i, lemma in enumerate(v28_lemmas):
            v2_8_llm_token = match_lemma_llm_v2_8_d[i]
            if lemma == v2_8_llm_token.lower():
                lemma_comparison_d[sent_id]['v2.8 llm']['same'] += 1
            lemma_comparison_d[sent_id]['v2.8 llm']['all'] += 1

        match_token_llm_v2_11_d = get_match_d(original_tokens, v2_11_llm_tokens)

        for i, token in enumerate(original_tokens):
            v2_11_llm_token = match_token_llm_v2_11_d[i]
            if token == v2_11_llm_token:
                token_comparison_d[sent_id]['v2.11 llm']['correct'] += 1
            token_comparison_d[sent_id]['v2.11 llm']['all'] += 1

        match_lemma_llm_v2_11_d = get_match_d(v211_lemmas, v2_11_llm_tokens)

        for i, lemma in enumerate(v211_lemmas):
            v2_11_llm_token = match_lemma_llm_v2_11_d[i]
            if lemma == v2_11_llm_token.lower():
                lemma_comparison_d[sent_id]['v2.11 llm']['same'] += 1
            lemma_comparison_d[sent_id]['v2.11 llm']['all'] += 1

        pass

    analysis_d = {
        'token_comparison_d':
            token_comparison_d,
        'lemma_comparison_d':
            lemma_comparison_d,
        'summary': {
            'v2.8 llm token match ratio': 0,
            'v2.11 llm token match ratio': 0,
            'v2.8 llm lemma match ratio': 0,
            'v2.11 llm lemma match ratio': 0
        }
    }

    for sent_id, value in token_comparison_d.items():
        v2_8_llm_ratio = value['v2.8 llm']['correct'] / value['v2.8 llm']['all']
        v2_11_llm_ratio = value['v2.11 llm']['correct'] / value['v2.11 llm']['all']
        analysis_d['summary']['v2.8 llm token match ratio'] += v2_8_llm_ratio
        analysis_d['summary']['v2.11 llm token match ratio'] += v2_11_llm_ratio

    analysis_d['summary']['v2.8 llm token match ratio'] /= len(token_comparison_d)
    analysis_d['summary']['v2.11 llm token match ratio'] /= len(token_comparison_d)

    for sent_id, value in lemma_comparison_d.items():
        v2_8_llm_ratio = value['v2.8 llm']['same'] / value['v2.8 llm']['all']
        v2_11_llm_ratio = value['v2.11 llm']['same'] / value['v2.11 llm']['all']
        analysis_d['summary']['v2.8 llm lemma match ratio'] += v2_8_llm_ratio
        analysis_d['summary']['v2.11 llm lemma match ratio'] += v2_11_llm_ratio

    analysis_d['summary']['v2.8 llm lemma match ratio'] /= len(lemma_comparison_d)
    analysis_d['summary']['v2.11 llm lemma match ratio'] /= len(lemma_comparison_d)

    path = dir / 'comparison-tokens.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
