import argparse, json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sentences', type=str, required=True)
    parser.add_argument('-r', '--results', type=str, required=True)
    args = parser.parse_args()
    sent_ids_path = args.sentences
    results = args.results
    with open(sent_ids_path, 'r', encoding='utf-8') as f:
        sent_ids = json.load(f)
    with open(results, 'r', encoding='utf-8') as f:
        results = json.load(f)
        if 'results' not in results:
            exit('Error: must have a "results" key')
        all_avg_2_8 = results['average v2.8 ratio']
        all_avg_2_11 = results['average v2.11 ratio']
        results = results['results']

    avg_2_8 = 0
    avg_2_11 = 0
    for i, sent_id in enumerate(sent_ids):
        scores = results[sent_id]
        ratio_2_8 = scores['v2.8 ratio']
        avg_2_8 += ratio_2_8
        ratio_2_11 = scores['v2.11 ratio']
        avg_2_11 += ratio_2_11
        print(f'{i+1}\t{sent_id}\t{ratio_2_8}\t{ratio_2_11}')
    avg_2_8 /= len(sent_ids)
    avg_2_11 /= len(sent_ids)
    print(f'Average ratio (v2.8 all):\t{all_avg_2_8:.3f}')
    print(f'Average ratio (v2.8 current):\t{avg_2_8:.3f}')
    print(f'Average ratio (v2.11 all):\t{all_avg_2_11:.3f}')
    print(f'Average ratio (v2.11 current):\t{avg_2_11:.3f}')

if __name__ == '__main__':
    main()


# python3 llm-approach/get_scores.py -s llm-approach/selected_sents_25.json -r llm-approach/experiment_outputs/eventual_experiment/poe_GPT-4-20231015231246/summary.json
# Average ratio (v2.8 all):       0.917
# Average ratio (v2.8 current):   0.930
# Average ratio (v2.11 all):      0.930
# Average ratio (v2.11 current):  0.948