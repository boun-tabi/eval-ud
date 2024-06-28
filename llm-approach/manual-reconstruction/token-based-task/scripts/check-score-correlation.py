import argparse, json, random
from pathlib import Path
from difflib import SequenceMatcher
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
    parser.add_argument('-t', '--type', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with open(args.constructions, 'r', encoding='utf-8') as f:
        constructions = json.load(f)
    llm_dir = Path(args.llm_dir)
    version1 = args.version1
    version2 = args.version2
    task_type = args.type
    if task_type == 'token with dep':
        v1_output = llm_dir / '{}_output_dep.json'.format(version1)
        v2_output = llm_dir / '{}_output_dep.json'.format(version2)
    else:
        v1_output = llm_dir / '{}_output.json'.format(version1)
        v2_output = llm_dir / '{}_output.json'.format(version2)
    with open(v1_output, 'r', encoding='utf-8') as f:
        v1_data = json.load(f)
    v1_data_d = {el['q_id']: el for el in v1_data}
    out_d = {el['q_id']: {} for el in v1_data}
    with open(v2_output, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
    v2_data_d = {el['q_id']: el for el in v2_data}
    person1 = args.person1
    person2 = args.person2
    accuracies = { version: { 'manual': { person: [] for person in [person1, person2]}, 'llm': [] } for version in [version1, version2] }
    outputs = { q_id: { version: {} for version in [version1, version2] } for q_id in out_d }
    for q_id in out_d:
        sent_id = v1_data_d[q_id]['sent_id']
        v1_token_id = v1_data_d[q_id]['token_id']
        v2_token_id = v2_data_d[q_id]['token_id']
        original_form = v1_data_d[q_id]['form']
        outputs[q_id]['original_form'] = original_form
        v1_llm_output = v1_data_d[q_id]['output']
        outputs[q_id][version1]['llm'] = v1_llm_output
        accuracies[version1]['llm'].append(SequenceMatcher(None, v1_llm_output.lower(), original_form.lower()).ratio())
        v2_llm_output = v2_data_d[q_id]['output']
        outputs[q_id][version2]['llm'] = v2_llm_output
        accuracies[version2]['llm'].append(SequenceMatcher(None, v2_llm_output.lower(), original_form.lower()).ratio())
        for person in [person1, person2]:
            for version in [version1, version2]:
                if version == version1:
                    person_construction = constructions[person][version][sent_id][v1_token_id]
                else:
                    person_construction = constructions[person][version][sent_id][v2_token_id]
                outputs[q_id][version][person] = person_construction
                accuracies[version]['manual'][person].append(SequenceMatcher(None, person_construction[0].lower(), original_form.lower()).ratio())
    
    p1_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['manual'][person1][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p1_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['manual'][person1][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p2_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['manual'][person2][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p2_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['manual'][person2][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    llm_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['llm'][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    llm_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['llm'][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]

    accuracies = {person: {version: [] for version in [version1, version2]} for person in [person1, person2, 'llm', 'random']}
    p1_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies[person1][version1] = [x['accuracy'] for x in p1_v1_l]
    accuracies['random'][version1] = [random.random() for _ in range(len(accuracies[person1][version1]))]
    p1_v2_l.sort(key=lambda x: x['sent_id'])
    accuracies[person1][version2] = [x['accuracy'] for x in p1_v2_l]
    accuracies['random'][version2] = [random.random() for _ in range(len(accuracies[person1][version2]))]
    p2_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies[person2][version1] = [x['accuracy'] for x in p2_v1_l]
    p2_v2_l.sort(key=lambda x: x['sent_id'])
    accuracies[person2][version2] = [x['accuracy'] for x in p2_v2_l]
    llm_v1_l.sort(key=lambda x: x['sent_id'])
    accuracies['llm'][version1] = [x['accuracy'] for x in llm_v1_l]
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
