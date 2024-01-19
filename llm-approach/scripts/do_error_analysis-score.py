import os, argparse, json

def main():
    DIFF_AMOUNT = 0.2
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    args = parser.parse_args()
    dir = args.directory

    summary_path = os.path.join(dir, 'summary.json')
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    md_path = os.path.join(dir, 'md.json')
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    model = md['model']
    
    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    low_score_sents, high_score_sents = [], []
    for sent_id, value in results.items():
        ratio_v2_8, ratio_v2_11 = value['v2.8 ratio'], value['v2.11 ratio']
        original_text, text_v2_8, text_v2_11 = value['original text'], value['v2.8 text'], value['v2.11 text']
        diff = ratio_v2_11 - ratio_v2_8
        d = {'sent_id': sent_id, 'diff': diff, 'original_text': original_text, 'text_v2_8': text_v2_8, 'text_v2_11': text_v2_11}
        if diff > DIFF_AMOUNT:
            high_score_sents.append(d)
        elif diff < -DIFF_AMOUNT:
            low_score_sents.append(d)
    print('High score sentences: {}'.format(len(high_score_sents)))
    print('Low score sentences: {}'.format(len(low_score_sents)))

    d = {'high_score_sents': high_score_sents, 'low_score_sents': low_score_sents, 'diff_amount': DIFF_AMOUNT, 'file': summary_path}
    with open(os.path.join(THIS_DIR, 'error_analysis-{}-score.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()