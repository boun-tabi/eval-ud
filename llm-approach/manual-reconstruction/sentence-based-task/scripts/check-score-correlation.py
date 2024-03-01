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
    for sent_id in out_d.keys():
        p1_v1_correct, p1_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version1], tokenizer)
        p1_v1_accuracy = p1_v1_correct / p1_v1_all
        # p1_v1_accuracy = '{:.2f}'.format(p1_v1_correct / p1_v1_all * 100)
        p1_v1_l.append({'sent_id': sent_id, 'accuracy': p1_v1_accuracy})
        p1_v2_correct, p1_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person1][version2], tokenizer)
        p1_v2_accuracy = p1_v2_correct / p1_v2_all
        # p1_v2_accuracy = '{:.2f}'.format(p1_v2_correct / p1_v2_all * 100)
        p1_v2_l.append({'sent_id': sent_id, 'accuracy': p1_v2_accuracy})
        p2_v1_correct, p2_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version1], tokenizer)
        p2_v1_accuracy = p2_v1_correct / p2_v1_all
        # p2_v1_accuracy = '{:.2f}'.format(p2_v1_correct / p2_v1_all * 100)
        p2_v1_l.append({'sent_id': sent_id, 'accuracy': p2_v1_accuracy})
        p2_v2_correct, p2_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id][person2][version2], tokenizer)
        p2_v2_accuracy = p2_v2_correct / p2_v2_all
        # p2_v2_accuracy = '{:.2f}'.format(p2_v2_correct / p2_v2_all * 100)
        p2_v2_l.append({'sent_id': sent_id, 'accuracy': p2_v2_accuracy})
        llm_v1_correct, llm_v1_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version1], tokenizer)
        llm_v1_accuracy = llm_v1_correct / llm_v1_all
        # llm_v1_accuracy = '{:.2f}'.format(llm_v1_correct / llm_v1_all * 100)
        llm_v1_l.append({'sent_id': sent_id, 'accuracy': llm_v1_accuracy})
        llm_v2_correct, llm_v2_all = get_accuracy(out_d[sent_id]['original'], out_d[sent_id]['llm'][version2], tokenizer)
        # llm_v2_accuracy = '{:.2f}'.format(llm_v2_correct / llm_v2_all * 100)
        llm_v2_accuracy = llm_v2_correct / llm_v2_all
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

    # p1_v1_l.sort(key=lambda x: x['sent_id'])
    # p1_v1_l.sort(key=lambda x: x['accuracy'])
    # p1_v1_sent_ids = '-'.join([x['sent_id'] for x in p1_v1_l])
    # random_v1_sent_ids = [x['sent_id'] for x in p1_v1_l]
    # random.shuffle(random_v1_sent_ids)
    # random_v1_sent_ids = '-'.join(random_v1_sent_ids)
    # p1_v2_l.sort(key=lambda x: x['sent_id'])
    # p1_v2_l.sort(key=lambda x: x['accuracy'])
    # p1_v2_sent_ids = '-'.join([x['sent_id'] for x in p1_v2_l])
    # random_v2_sent_ids = [x['sent_id'] for x in p1_v2_l]
    # random.shuffle(random_v2_sent_ids)
    # random_v2_sent_ids = '-'.join(random_v2_sent_ids)
    # p2_v1_l.sort(key=lambda x: x['sent_id'])
    # p2_v1_l.sort(key=lambda x: x['accuracy'])
    # p2_v1_sent_ids = '-'.join([x['sent_id'] for x in p2_v1_l])
    # p2_v2_l.sort(key=lambda x: x['sent_id'])
    # p2_v2_l.sort(key=lambda x: x['accuracy'])
    # p2_v2_sent_ids = '-'.join([x['sent_id'] for x in p2_v2_l])
    # llm_v1_l.sort(key=lambda x: x['sent_id'])
    # llm_v1_l.sort(key=lambda x: x['accuracy'])
    # llm_v1_sent_ids = '-'.join([x['sent_id'] for x in llm_v1_l])
    # llm_v2_l.sort(key=lambda x: x['sent_id'])
    # llm_v2_l.sort(key=lambda x: x['accuracy'])
    # llm_v2_sent_ids = '-'.join([x['sent_id'] for x in llm_v2_l])

    # print('fuzz.ratio between {}_{} and {}_{}: {}'.format(person1, version1, person2, version1, fuzz.ratio(p1_v1_sent_ids, p2_v1_sent_ids)))
    # print('fuzz.ratio between {}_{} and {}_{}: {}'.format(person1, version2, person2, version2, fuzz.ratio(p1_v2_sent_ids, p2_v2_sent_ids)))
    # print('fuzz.ratio between {}_{} and llm_{}: {}'.format(person1, version1, version1, fuzz.ratio(p1_v1_sent_ids, llm_v1_sent_ids)))
    # print('fuzz.ratio between {}_{} and llm_{}: {}'.format(person1, version2, version2, fuzz.ratio(p1_v2_sent_ids, llm_v2_sent_ids)))
    # print('fuzz.ratio between {}_{} and llm_{}: {}'.format(person2, version1, version1, fuzz.ratio(p2_v1_sent_ids, llm_v1_sent_ids)))
    # print('fuzz.ratio between {}_{} and llm_{}: {}'.format(person2, version2, version2, fuzz.ratio(p2_v2_sent_ids, llm_v2_sent_ids)))
    # print('fuzz.ratio between {}_{} and {}_{}: {}'.format(person1, version1, 'random', version1, fuzz.ratio(p1_v1_sent_ids, random_v1_sent_ids)))
    # print('fuzz.ratio between {}_{} and {}_{}: {}'.format(person1, version2, 'random', version2, fuzz.ratio(p1_v2_sent_ids, random_v2_sent_ids)))

if __name__ == '__main__':
    main()

'''
Pearson correlation coefficient between:

Tarık_v2.8 and Akif_v2.8:	0.4429585134314543
Tarık_v2.11 and Akif_v2.11:	0.43517720228151874
Tarık_v2.8 and llm_v2.8:	-0.13433693009452538
Tarık_v2.11 and llm_v2.11:	0.5302166693989327
Akif_v2.8 and llm_v2.8:	    -0.032525321480106735
Akif_v2.11 and llm_v2.11:	0.21785170546886162
Tarık_v2.8 and random:	    -0.05960489303232497
Tarık_v2.11 and random:	    -0.31099951534107984
Akif_v2.8 and random:	    -0.23488581726523558
Akif_v2.11 and random:	    -0.0911716915826565
llm_v2.8 and random:	    -0.1027797223804541
llm_v2.11 and random:	    -0.00985869223401618
'''