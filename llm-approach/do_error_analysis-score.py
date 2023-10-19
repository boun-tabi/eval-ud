import os, argparse, json

def main():
    DIFF_AMOUNT = 0.2
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='File to be analyzed')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'results' not in data:
        print('No results found in file')
        return
    results = data['results']

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

    d = {'high_score_sents': high_score_sents, 'low_score_sents': low_score_sents, 'file': args.file, 'diff_amount': DIFF_AMOUNT}
    with open(os.path.join(THIS_DIR, 'error_analysis-score.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()