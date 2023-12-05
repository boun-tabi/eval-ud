import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-n", "--note", type=str, required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf8") as f:
        comparison_d = json.load(f)
    
    sent_ids = list(comparison_d.keys())

    type_l = ['v2.8 llm', 'v2.11 llm', 'v2.8 manual', 'v2.11 manual']
    token_accuracy_summary_d = {type_t: {'correct': 0, 'all': 0, 'ratio': None} for type_t in type_l}
    for sent_id in sent_ids:
        for type_t in type_l:
            token_accuracy_summary_d[type_t]['correct'] += comparison_d[sent_id][type_t]['correct']
            token_accuracy_summary_d[type_t]['all'] += comparison_d[sent_id][type_t]['all']
    for type_t in type_l:
        token_accuracy_summary_d[type_t]['ratio'] = token_accuracy_summary_d[type_t]['correct'] / token_accuracy_summary_d[type_t]['all']
    
    with open(os.path.join(THIS_DIR, f"token-accuracy-summary-{args.note}.json"), "w", encoding="utf8") as f:
        json.dump(token_accuracy_summary_d, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
