import argparse, json, random
from pathlib import Path
from difflib import SequenceMatcher
from scipy.stats import pearsonr

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
                accuracies[version]['manual'][person].append(SequenceMatcher(None, person_construction.lower(), original_form.lower()).ratio())
    
    p1_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['manual'][person1][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p1_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['manual'][person1][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p2_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['manual'][person2][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    p2_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['manual'][person2][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    llm_v1_l = [ { 'sent_id': v1_data_d[q_id]['sent_id'], 'accuracy': accuracies[version1]['llm'][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]
    llm_v2_l = [ { 'sent_id': v2_data_d[q_id]['sent_id'], 'accuracy': accuracies[version2]['llm'][i], 'q_id': q_id } for i, q_id in enumerate(out_d) ]

    p1_v1_l.sort(key=lambda x: x['sent_id'])
    p1_v1_accuracies = [x['accuracy'] for x in p1_v1_l]
    random_accuracies = [random.random() for _ in range(len(p1_v1_accuracies))]
    p1_v2_l.sort(key=lambda x: x['sent_id'])
    p1_v2_accuracies = [x['accuracy'] for x in p1_v2_l]
    p2_v1_l.sort(key=lambda x: x['sent_id'])
    p2_v1_accuracies = [x['accuracy'] for x in p2_v1_l]
    p2_v2_l.sort(key=lambda x: x['sent_id'])
    p2_v2_accuracies = [x['accuracy'] for x in p2_v2_l]
    llm_v1_l.sort(key=lambda x: x['sent_id'])
    llm_v1_accuracies = [x['accuracy'] for x in llm_v1_l]
    llm_v2_l.sort(key=lambda x: x['sent_id'])
    llm_v2_accuracies = [x['accuracy'] for x in llm_v2_l]

    print('Pearson correlation coefficient between')
    print('{}_{} and {}_{}:		{}'.format(person1, version1, person2, version1, pearsonr(p1_v1_accuracies, p2_v1_accuracies)[0]))
    print('{}_{} and {}_{}:		{}'.format(person1, version2, person2, version2, pearsonr(p1_v2_accuracies, p2_v2_accuracies)[0]))
    print('{}_{} and llm_{}:		{}'.format(person1, version1, version1, pearsonr(p1_v1_accuracies, llm_v1_accuracies)[0]))
    print('{}_{} and llm_{}:		{}'.format(person1, version2, version2, pearsonr(p1_v2_accuracies, llm_v2_accuracies)[0]))
    print('{}_{} and llm_{}:		{}'.format(person2, version1, version1, pearsonr(p2_v1_accuracies, llm_v1_accuracies)[0]))
    print('{}_{} and llm_{}:		{}'.format(person2, version2, version2, pearsonr(p2_v2_accuracies, llm_v2_accuracies)[0]))
    print('{}_{} and {}:		{}'.format(person1, version1, 'random', pearsonr(p1_v1_accuracies, random_accuracies)[0]))
    print('{}_{} and {}:		{}'.format(person1, version2, 'random', pearsonr(p1_v2_accuracies, random_accuracies)[0]))
    print('{}_{} and {}:		{}'.format(person2, version1, 'random', pearsonr(p2_v1_accuracies, random_accuracies)[0]))
    print('{}_{} and {}:		{}'.format(person2, version2, 'random', pearsonr(p2_v2_accuracies, random_accuracies)[0]))
    print('llm_{} and {}:		{}'.format(version1, 'random', pearsonr(llm_v1_accuracies, random_accuracies)[0]))
    print('llm_{} and {}:		{}'.format(version2, 'random', pearsonr(llm_v2_accuracies, random_accuracies)[0]))

if __name__ == '__main__':
    main()

'''
Pearson correlation coefficient between (token)
Tarık_v2.8 and Akif_v2.8:               0.5734503857910465
Tarık_v2.11 and Akif_v2.11:             0.7524227748175509
Tarık_v2.8 and llm_v2.8:                0.2377819590041406
Tarık_v2.11 and llm_v2.11:              0.2738277010455822
Akif_v2.8 and llm_v2.8:                 0.18612946902386446
Akif_v2.11 and llm_v2.11:               0.2544342150045172
Tarık_v2.8 and random:                  0.020206335632594136
Tarık_v2.11 and random:                 -0.5904903500953886
Akif_v2.8 and random:                   -0.1748645426539977
Akif_v2.11 and random:                  -0.5138114188934215
llm_v2.8 and random:                    -0.156241570210788
llm_v2.11 and random:                   -0.3765647009019218
'''

'''
Pearson correlation coefficient between (token with dep)
Tarık_v2.8 and Akif_v2.8:               0.37362911988725334
Tarık_v2.11 and Akif_v2.11:             0.3648889005926477
Tarık_v2.8 and llm_v2.8:                -0.24312289359084102
Tarık_v2.11 and llm_v2.11:              0.5307638125852431
Akif_v2.8 and llm_v2.8:                 0.03278275322595323
Akif_v2.11 and llm_v2.11:               -0.019625780947841495
Tarık_v2.8 and random:                  -0.08635523833262393
Tarık_v2.11 and random:                 0.10435310841341017
Akif_v2.8 and random:                   -0.0861064153845852
Akif_v2.11 and random:                  -0.11804627038232984
llm_v2.8 and random:                    -0.11848878601698677
llm_v2.11 and random:                   0.048936046064712954
'''