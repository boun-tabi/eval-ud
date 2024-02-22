import argparse, csv, json, re
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
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

    out_d = {sent_id: {'original': '', person1: {version1: '', version2: ''}, person2: {version1: '', version2: ''}, 'llm': {version1: '', version2: ''}} for sent_id in v1_data.keys()}
    for sent_id in out_d.keys():
        out_d[sent_id]['original'] = v1_data[sent_id]['original_text']
        out_d[sent_id][person1][version1] = constructions[person1][version1][sent_id]
        out_d[sent_id][person1][version2] = constructions[person1][version2][sent_id]
        out_d[sent_id][person2][version1] = constructions[person2][version1][sent_id]
        out_d[sent_id][person2][version2] = constructions[person2][version2][sent_id]
        out_d[sent_id]['llm'][version1] = v1_data[sent_id]['output_text']
        out_d[sent_id]['llm'][version2] = v2_data[sent_id]['output_text']
    
    with open(llm_dir / 'llm-manual.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sent_id', 'original', '{}_{}'.format(person1, version1), '{}_{}'.format(person1, version2), '{}_{}'.format(person2, version1), '{}_{}'.format(person2, version2), 'llm_{}'.format(version1), 'llm_{}'.format(version2)])
        for sent_id in out_d.keys():
            writer.writerow([sent_id, out_d[sent_id]['original'], out_d[sent_id][person1][version1], out_d[sent_id][person1][version2], out_d[sent_id][person2][version1], out_d[sent_id][person2][version2], out_d[sent_id]['llm'][version1], out_d[sent_id]['llm'][version2]])

if __name__ == '__main__':
    main()