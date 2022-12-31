import os, pandas as pd

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

scores_d = dict()
scores_d['feats_only_baseline'] = {'2.8': {'UFeats': list()}, '2.11': {'UFeats': list()}, '2.11-unr': {'UFeats': list()}}
scores_d['lemma_only_baseline'] = {'2.8': {'Lemmas': list()}, '2.11': {'Lemmas': list()}, '2.11-unr': {'Lemmas': list()}}
scores_d['pos_only_baseline'] = {'2.8': {'UPOS': list()}, '2.11': {'UPOS': list()}, '2.11-unr': {'UPOS': list()}}
scores_d['dep_parsing'] = {'2.8': {'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11': {'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11-unr': {'UAS': list(), 'LAS': list(), 'CLAS': list()}}
scores_d['dep_parsing_upos_feats_MTL'] = {'2.8': {'UPOS': list(), 'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'MLAS': list()}, '2.11': {'UPOS': list(), 'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'MLAS': list()}, '2.11-unr': {'UPOS': list(), 'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'MLAS': list()}}
scores_d['dep_parsing_upos_MTL'] = {'2.8': {'UPOS': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11': {'UPOS': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11-unr': {'UPOS': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}}
scores_d['dep_parsing_feats_MTL'] = {'2.8': {'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11': {'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}, '2.11-unr': {'UFeats': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list()}}
scores_d['dep_parsing_lemma_MTL'] = {'2.8': {'Lemmas': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'BLEX': list()}, '2.11': {'Lemmas': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'BLEX': list()}, '2.11-unr': {'Lemmas': list(), 'UAS': list(), 'LAS': list(), 'CLAS': list(), 'BLEX': list()}}
scores_d['feats_upos_MTL'] = {'2.8': {'UPOS': list(), 'UFeats': list()}, '2.11': {'UPOS': list(), 'UFeats': list()}, '2.11-unr': {'UPOS': list(), 'UFeats': list()}}

scores_d['feats_only_baseline']['2.8']['UFeats'] = [92.49, 92.58, 92.53, 92.88, 92.39]
scores_d['feats_only_baseline']['2.11']['UFeats'] = [82.56, 82.62, 82.86, 82.57, 82.31]
scores_d['feats_only_baseline']['2.11-unr']['UFeats'] = [82.59]

scores_d['lemma_only_baseline']['2.8']['Lemmas'] = [90.00, 90.07, 90.02, 90.05, 89.99, 90.56]
scores_d['lemma_only_baseline']['2.11']['Lemmas'] = [88.57, 88.14, 88.17, 87.99, 87.91]
scores_d['lemma_only_baseline']['2.11-unr']['Lemmas'] = [87.99]

scores_d['pos_only_baseline']['2.8']['UPOS'] = [92.00, 92.00, 91.95, 91.87, 91.77]
scores_d['pos_only_baseline']['2.11']['UPOS'] = [93.10, 93.18, 93.24, 93.10, 92.96]
scores_d['pos_only_baseline']['2.11-unr']['UPOS'] = [93.00]

scores_d['dep_parsing']['2.8']['UAS'] = [82.51]
scores_d['dep_parsing']['2.8']['LAS'] = [76.55]
scores_d['dep_parsing']['2.8']['CLAS'] = [74.78]
scores_d['dep_parsing']['2.11']['UAS'] = [82.09]
scores_d['dep_parsing']['2.11']['LAS'] = [75.20]
scores_d['dep_parsing']['2.11']['CLAS'] = [74.05]
scores_d['dep_parsing']['2.11-unr']['UAS'] = [82.29]
scores_d['dep_parsing']['2.11-unr']['LAS'] = [75.41]
scores_d['dep_parsing']['2.11-unr']['CLAS'] = [74.11]

scores_d['dep_parsing_upos_feats_MTL']['2.8']['UPOS'] = [87.31]
scores_d['dep_parsing_upos_feats_MTL']['2.8']['UFeats'] = [73.39]
scores_d['dep_parsing_upos_feats_MTL']['2.8']['UAS'] = [81.80]
scores_d['dep_parsing_upos_feats_MTL']['2.8']['LAS'] = [75.87]
scores_d['dep_parsing_upos_feats_MTL']['2.8']['CLAS'] = [73.73] # used F1
scores_d['dep_parsing_upos_feats_MTL']['2.8']['MLAS'] = [41.36]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['UPOS'] = [91.17]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['UFeats'] = [68.99]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['UAS'] = [81.19]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['LAS'] = [74.27]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['CLAS'] = [72.89]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['MLAS'] = [39.30]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['UPOS'] = [91.61]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['UFeats'] = [72.38]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['UAS'] = [81.38]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['LAS'] = [74.32]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['CLAS'] = [72.80]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['MLAS'] = [42.91]

scores_d['dep_parsing_upos_MTL']['2.8']['UPOS'] = [87.08]
scores_d['dep_parsing_upos_MTL']['2.8']['UAS'] = [82.52]
scores_d['dep_parsing_upos_MTL']['2.8']['LAS'] = [76.53]
scores_d['dep_parsing_upos_MTL']['2.8']['CLAS'] = [74.56]
scores_d['dep_parsing_upos_MTL']['2.11']['UPOS'] = [91.21]
scores_d['dep_parsing_upos_MTL']['2.11']['UAS'] = [81.96]
scores_d['dep_parsing_upos_MTL']['2.11']['LAS'] = [75.09]
scores_d['dep_parsing_upos_MTL']['2.11']['CLAS'] = [73.74]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['UPOS'] = [91.19]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['UAS'] = [82.06]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['LAS'] = [75.33]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['CLAS'] = [73.97]

scores_d['dep_parsing_feats_MTL']['2.8']['UFeats'] = [70.22]
scores_d['dep_parsing_feats_MTL']['2.8']['UAS'] = [82.36]
scores_d['dep_parsing_feats_MTL']['2.8']['LAS'] = [76.32]
scores_d['dep_parsing_feats_MTL']['2.8']['CLAS'] = [74.14]
scores_d['dep_parsing_feats_MTL']['2.11']['UFeats'] = [66.70]
scores_d['dep_parsing_feats_MTL']['2.11']['UAS'] = [81.78]
scores_d['dep_parsing_feats_MTL']['2.11']['LAS'] = [74.98]
scores_d['dep_parsing_feats_MTL']['2.11']['CLAS'] = [73.50]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['UFeats'] = [68.65]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['UAS'] = [81.88]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['LAS'] = [75.02]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['CLAS'] = [73.64]

scores_d['dep_parsing_lemma_MTL']['2.8']['Lemmas'] = [56.19]
scores_d['dep_parsing_lemma_MTL']['2.8']['UAS'] = [82.25]
scores_d['dep_parsing_lemma_MTL']['2.8']['LAS'] = [76.20]
scores_d['dep_parsing_lemma_MTL']['2.8']['CLAS'] = [73.93]
scores_d['dep_parsing_lemma_MTL']['2.8']['BLEX'] = [30.39]
scores_d['dep_parsing_lemma_MTL']['2.11']['Lemmas'] = [54.82]
scores_d['dep_parsing_lemma_MTL']['2.11']['UAS'] = [81.88]
scores_d['dep_parsing_lemma_MTL']['2.11']['LAS'] = [75.12]
scores_d['dep_parsing_lemma_MTL']['2.11']['CLAS'] = [73.67]
scores_d['dep_parsing_lemma_MTL']['2.11']['BLEX'] = [29.43]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['Lemmas'] = [48.19]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['UAS'] = [81.91]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['LAS'] = [75.01]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['CLAS'] = [73.60]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['BLEX'] = [23.01]

scores_d['feats_upos_MTL']['2.8']['UPOS'] = []
scores_d['feats_upos_MTL']['2.8']['UFeats'] = []
scores_d['feats_upos_MTL']['2.11']['UPOS'] = []
scores_d['feats_upos_MTL']['2.11']['UFeats'] = []
scores_d['feats_upos_MTL']['2.11-unr']['UPOS'] = []
scores_d['feats_upos_MTL']['2.11-unr']['UFeats'] = []

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
