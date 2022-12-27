import os
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

scores_d = dict()
scores_d['feats_only_baseline'] = {'2.8': {'UFeats': list()}, '2.11': {'UFeats': list()}, '2.11-unr': {'UFeats': list()}}
scores_d['lemma_only_baseline'] = {'2.8': {'Lemmas': list()}, '2.11': {'Lemmas': list()}, '2.11-unr': {'Lemmas': list()}}
scores_d['pos_only_baseline'] = {'2.8': {'UPOS': list()}, '2.11': {'UPOS': list()}, '2.11-unr': {'UPOS': list()}}

scores_d['feats_only_baseline']['2.8']['UFeats'] = [92.49, 92.58, 92.53, 92.88, 92.39]
scores_d['feats_only_baseline']['2.11']['UFeats'] = [82.56, 82.62, 82.86, 82.57, 82.31]
scores_d['feats_only_baseline']['2.11-unr']['UFeats'] = [82.59]

scores_d['lemma_only_baseline']['2.8']['Lemmas'] = [90.00, 90.07, 90.02, 90.05, 89.99, 90.56]
scores_d['lemma_only_baseline']['2.11']['Lemmas'] = [88.57, 88.14, 88.17, 87.99, 87.91]
scores_d['lemma_only_baseline']['2.11-unr']['Lemmas'] = [87.99]

scores_d['pos_only_baseline']['2.8']['UPOS'] = [92.00, 92.00, 91.95, 91.87, 91.77]
scores_d['pos_only_baseline']['2.11']['UPOS'] = [93.10, 93.18, 93.24, 93.10, 92.96]
scores_d['pos_only_baseline']['2.11-unr']['UPOS'] = [93.00]

import pandas as pd
bl_type_l = list(scores_d.keys())
for bl_type in bl_type_l:
    print(bl_type)
    tb_version_l = list(scores_d[bl_type].keys())
    score_l = list()
    for tb_version in tb_version_l:
        metric_l = list(scores_d[bl_type][tb_version].keys())
        score_m_l = list()
        for metric in metric_l:
            scores_l = scores_d[bl_type][tb_version][metric]
            if len(scores_l) == 0:
                score_m_l.append('-')
            else:
                avg_score = sum(scores_l) / len(scores_l)
                score_m_l.append('{:.2f}'.format(avg_score))
        score_l.append(score_m_l)
    df = pd.DataFrame(score_l, columns=metric_l, index=tb_version_l)
    print(df)
    print()
