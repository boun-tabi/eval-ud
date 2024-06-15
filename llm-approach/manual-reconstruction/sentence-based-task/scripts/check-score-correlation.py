import argparse, json, random
from pathlib import Path
from spacy.lang.tr import Turkish
from get_best_worst import get_accuracy
from rapidfuzz import fuzz
from scipy.stats import pearsonr

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

    print('Pearson correlation coefficient between {}_{} and {}_{}: {}'.format(person1, version1, person2, version1, pearsonr(p1_v1_accuracies, p2_v1_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and {}_{}: {}'.format(person1, version2, person2, version2, pearsonr(p1_v2_accuracies, p2_v2_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and llm_{}: {}'.format(person1, version1, version1, pearsonr(p1_v1_accuracies, llm_v1_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and llm_{}: {}'.format(person1, version2, version2, pearsonr(p1_v2_accuracies, llm_v2_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and llm_{}: {}'.format(person2, version1, version1, pearsonr(p2_v1_accuracies, llm_v1_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and llm_{}: {}'.format(person2, version2, version2, pearsonr(p2_v2_accuracies, llm_v2_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and {}: {}'.format(person1, version1, 'random', pearsonr(p1_v1_accuracies, random_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and {}: {}'.format(person1, version2, 'random', pearsonr(p1_v2_accuracies, random_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and {}: {}'.format(person2, version1, 'random', pearsonr(p2_v1_accuracies, random_accuracies)[0]))
    print('Pearson correlation coefficient between {}_{} and {}: {}'.format(person2, version2, 'random', pearsonr(p2_v2_accuracies, random_accuracies)[0]))
    print('Pearson correlation coefficient between llm_{} and {}: {}'.format(version1, 'random', pearsonr(llm_v1_accuracies, random_accuracies)[0]))
    print('Pearson correlation coefficient between llm_{} and {}: {}'.format(version2, 'random', pearsonr(llm_v2_accuracies, random_accuracies)[0]))

if __name__ == '__main__':
    main()

'''
Pearson correlation coefficient between:

Tarık_v2.8 and Akif_v2.8: 0.4017330248281491
Tarık_v2.11 and Akif_v2.11: 0.5634848457338214
Tarık_v2.8 and llm_v2.8: 0.20495715591867494
Tarık_v2.11 and llm_v2.11: 0.32564391165039824
Akif_v2.8 and llm_v2.8: 0.2992647619615047
Akif_v2.11 and llm_v2.11: 0.3367023953105025
Tarık_v2.8 and random: 0.09374457833957385
Tarık_v2.11 and random: 0.02284347843878367
Akif_v2.8 and random: -0.0530533012966345
Akif_v2.11 and random: 0.061313008650800326
llm_v2.8 and random: 0.12957605818179854
llm_v2.11 and random: 0.14830011885974398
'''