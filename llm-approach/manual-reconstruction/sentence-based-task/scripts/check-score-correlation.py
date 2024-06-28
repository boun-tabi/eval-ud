import argparse, json, random
from pathlib import Path
from spacy.lang.tr import Turkish
from get_best_worst import get_accuracy
from scipy.stats import pearsonr
import numpy as np
from scipy.stats import norm

def fisher_r_to_z(r):
    return 0.5 * np.log((1 + r) / (1 - r))

def z_to_p(z):
    return 2 * (1 - norm.cdf(abs(z)))

def compare_correlations(r1, r2, n):
    z1 = fisher_r_to_z(r1) # Convert r1 to z value
    z2 = fisher_r_to_z(r2) # Convert r2 to z value

    delta_z = z1 - z2 # Calculate the difference between z values

    se = np.sqrt(2 / (n - 3)) # Standard error of the difference

    z = delta_z / se # z score for the difference

    p_value = z_to_p(z) # p-value for the difference

    return z, p_value

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

    p1_v1_l, p1_v2_l, p2_v1_l, p2_v2_l, llm_v1_l, llm_v2_l = [], [], [], [], [], []

    random.seed(42)
    sent_ids = list(v1_data.keys())
    random.shuffle(sent_ids)
    sent_ids = sent_ids[:50] # ['bio_1990', 'bio_889', 'bio_433'] removed
    for sent_id in out_d.keys():
        if sent_id not in sent_ids:
            continue
        p1_v1_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version1], tokenizer)
        p1_v1_l.append({'sent_id': sent_id, 'accuracy': p1_v1_accuracy})
        p1_v2_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version2], tokenizer)
        p1_v2_l.append({'sent_id': sent_id, 'accuracy': p1_v2_accuracy})
        p2_v1_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version1], tokenizer)
        p2_v1_l.append({'sent_id': sent_id, 'accuracy': p2_v1_accuracy})
        p2_v2_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version2], tokenizer)
        p2_v2_l.append({'sent_id': sent_id, 'accuracy': p2_v2_accuracy})
        llm_v1_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version1], tokenizer)
        llm_v1_l.append({'sent_id': sent_id, 'accuracy': llm_v1_accuracy})
        llm_v2_accuracy = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version2], tokenizer)
        llm_v2_l.append({'sent_id': sent_id, 'accuracy': llm_v2_accuracy})
    
    accuracies = {person: {version: [] for version in [version1, version2]} for person in [person1, person2, 'llm', 'random']}
    p1_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies[person1][version1] = [x['accuracy'] for x in p1_v1_l]
    accuracies['random'][version1] = [random.random() for _ in range(len(accuracies[person1][version1]))]
    p2_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies[person2][version1] = [x['accuracy'] for x in p2_v1_l]
    llm_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies['llm'][version1] = [x['accuracy'] for x in llm_v1_l]
    p1_v2_l.sort(key=lambda x: x['sent_id'])
    accuracies[person1][version2] = [x['accuracy'] for x in p1_v2_l]
    accuracies['random'][version2] = [random.random() for _ in range(len(accuracies[person1][version2]))]
    p2_v2_l.sort(key=lambda x: x['sent_id'])
    accuracies[person2][version2] = [x['accuracy'] for x in p2_v2_l]
    llm_v2_l.sort(key=lambda x: x['sent_id'])
    accuracies['llm'][version2] = [x['accuracy'] for x in llm_v2_l]

    print('Pearson correlation coefficient between:\n')
    pearsons = {}
    for version in [version1, version2]:
        for p1 in [person1, person2, 'llm', 'random']:
            for p2 in [person1, person2, 'llm', 'random']:
                if p1 == p2:
                    continue
                pearson = pearsonr(accuracies[p1][version], accuracies[p2][version])[0]
                if version not in pearsons:
                    pearsons[version] = {}
                pearsons[version][(p1, p2)] = pearson
                pearson_rounded = round(pearson, 3)
                print('{}_{} and {}_{}: {}'.format(p1, version, p2, version, pearson_rounded))
    print()

    print('Significance test between Pearson correlation coefficients:\n')
    for version in pearsons.keys():
        for (p1, p2) in pearsons[version].keys():
            for (p3, p4) in pearsons[version].keys():
                _, p_value = compare_correlations(pearsons[version][(p1, p2)], pearsons[version][(p3, p4)], len(accuracies[p1][version]))
                if p_value < 0.05:
                    print('{}_{} and {}_{} to {}_{} and {}_{}: p = {}'.format(p1, version, p2, version, p3, version, p4, version, 'significant'))
                else:
                    print('{}_{} and {}_{} to {}_{} and {}_{}: p = {}'.format(p1, version, p2, version, p3, version, p4, version, 'not significant'))

if __name__ == '__main__':
    main()
