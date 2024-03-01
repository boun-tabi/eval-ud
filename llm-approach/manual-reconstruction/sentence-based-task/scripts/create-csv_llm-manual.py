import argparse, csv, json
from pathlib import Path
from spacy.lang.tr import Turkish
from get_best_worst import get_accuracy

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    parser.add_argument('-o', '--order', type=str)
    return parser.parse_args()

def main():
    args = get_args()
    with open(args.constructions, 'r', encoding='utf-8') as f:
        constructions = json.load(f)
    llm_dir = Path(args.llm_dir)
    version1 = args.version1
    version2 = args.version2
    if '{}_output-cleaned.json'.format(version1) in [f.name for f in llm_dir.iterdir()]:
        v1_output = llm_dir / '{}_output-cleaned.json'.format(version1)
        v2_output = llm_dir / '{}_output-cleaned.json'.format(version2)
        with open(v1_output, 'r', encoding='utf-8') as f:
            v1_data = json.load(f)
        with open(v2_output, 'r', encoding='utf-8') as f:
            v2_data = json.load(f)
    else:
        v1_output = llm_dir / '{}_output.json'.format(version1)
        v2_output = llm_dir / '{}_output.json'.format(version2)
        with open(v1_output, 'r', encoding='utf-8') as f:
            v1_data = json.load(f)
        with open(v2_output, 'r', encoding='utf-8') as f:
            v2_data = json.load(f)

    person1 = args.person1
    person2 = args.person2

    nlp = Turkish()
    tokenizer = nlp.tokenizer

    out_d = {sent_id: {'original': '', person1: {version1: '', version2: ''}, person2: {version1: '', version2: ''}, 'llm': {version1: '', version2: ''}} for sent_id in constructions[person1][version1].keys()}
    for sent_id in out_d.keys():
        out_d[sent_id]['original'] = v1_data[sent_id]['original_text']
        out_d[sent_id][person1][version1] = constructions[person1][version1][sent_id]
        out_d[sent_id][person1][version2] = constructions[person1][version2][sent_id]
        out_d[sent_id][person2][version1] = constructions[person2][version1][sent_id]
        out_d[sent_id][person2][version2] = constructions[person2][version2][sent_id]
        out_d[sent_id]['llm'][version1] = v1_data[sent_id]['output_text']
        out_d[sent_id]['llm'][version2] = v2_data[sent_id]['output_text']

    if args.order:
        filepath = llm_dir / 'llm-manual-{}.csv'.format(args.order)
    else:
        filepath = llm_dir / 'llm-manual.csv'

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sent_id', 'original', '{}_{}'.format(person1, version1), '{}_{}'.format(person1, version2), '{}_{}'.format(person2, version1), '{}_{}'.format(person2, version2), 'llm_{}'.format(version1), 'llm_{}'.format(version2), 'accuracy_{}_{}'.format(person1, version1), 'accuracy_{}_{}'.format(person1, version2), 'accuracy_{}_{}'.format(person2, version1), 'accuracy_{}_{}'.format(person2, version2), 'accuracy_llm_{}'.format(version1), 'accuracy_llm_{}'.format(version2)])
        for sent_id in out_d.keys():
            p1_v1_correct, p1_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version1], tokenizer)
            p1_v1_accuracy = '{:.2f}'.format(p1_v1_correct / p1_v1_all * 100)
            p1_v2_correct, p1_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version2], tokenizer)
            p1_v2_accuracy = '{:.2f}'.format(p1_v2_correct / p1_v2_all * 100)
            p2_v1_correct, p2_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version1], tokenizer)
            p2_v1_accuracy = '{:.2f}'.format(p2_v1_correct / p2_v1_all * 100)
            p2_v2_correct, p2_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version2], tokenizer)
            p2_v2_accuracy = '{:.2f}'.format(p2_v2_correct / p2_v2_all * 100)
            llm_v1_correct, llm_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version1], tokenizer)
            llm_v1_accuracy = '{:.2f}'.format(llm_v1_correct / llm_v1_all * 100)
            llm_v2_correct, llm_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version2], tokenizer)
            llm_v2_accuracy = '{:.2f}'.format(llm_v2_correct / llm_v2_all * 100)

            writer.writerow([sent_id, out_d[sent_id]['original'], out_d[sent_id][person1][version1], out_d[sent_id][person1][version2], out_d[sent_id][person2][version1], out_d[sent_id][person2][version2], out_d[sent_id]['llm'][version1], out_d[sent_id]['llm'][version2],
                                p1_v1_accuracy, p1_v2_accuracy, p2_v1_accuracy, p2_v2_accuracy, llm_v1_accuracy, llm_v2_accuracy])

if __name__ == '__main__':
    main()