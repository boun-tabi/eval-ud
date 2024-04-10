import os, json, argparse
from difflib import SequenceMatcher
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions-path', type=str, required=True)
    parser.add_argument('-t1', '--treebank1', type=str, required=True)
    parser.add_argument('-t2', '--treebank2', type=str, required=True)
    return parser.parse_args()

def get_accuracy(results):
    ratio_acc, all_count = 0, 0
    for sent_id in results:
        original_text = results[sent_id]['original_text']
        output_text = results[sent_id]['output_text']
        ratio = SequenceMatcher(None, original_text, output_text).ratio()
        ratio_acc += ratio
        all_count += 1
    return ratio_acc / all_count

def main():
    args = get_args()

    constructions_path = Path(args.constructions_path)

    with constructions_path.open('r', encoding='utf-8') as f:
        constructions = json.load(f)
    
    people = list(constructions.keys())
    versions = list(constructions[people[0]].keys())

    tb1, tb2 = Path(args.treebank1), Path(args.treebank2)
    with tb1.open('r', encoding='utf-8') as f:
        tb1_data = json.load(f)
    tb1_texts = {sent_id: tb1_data[sent_id]['text'] for sent_id in tb1_data}
    with tb2.open('r', encoding='utf-8') as f:
        tb2_data = json.load(f)
    tb2_texts = {sent_id: tb2_data[sent_id]['text'] for sent_id in tb2_data}

    out_d = {'results': {person: {version: {} for version in versions} for person in people}}
    for person in people:
        for version in versions:
            ratio_acc, all_count = 0, 0
            for sent_id in constructions[person][version]:
                if version == 'v2.8':
                    original_text = tb1_texts[sent_id]
                elif version == 'v2.11':
                    original_text = tb2_texts[sent_id]
                output_text = constructions[person][version][sent_id]
                ratio = SequenceMatcher(None, original_text, output_text).ratio()
                ratio_acc += ratio
                all_count += 1
                d = {'ratio': float('{:.3f}'.format(ratio)), 'original text': original_text, 'output text': output_text}
                out_d['results'][person][version][sent_id] = d
            out_d['results'][person][version]['average ratio'] = ratio_acc / all_count

    out_d['sentence_count'] = all_count

    keys = list(out_d.keys())
    keys.sort()
    out_d = {k: out_d[k] for k in keys}

    summary_path = constructions_path.parent / (constructions_path.stem + '-summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(out_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()