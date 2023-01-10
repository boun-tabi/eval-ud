import os, pandas as pd

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

scores_d = dict()
# single-task
scores_d['feats_only_baseline'] = {'2.8': {'UFeats': list(), 'IndFeats': list()}, '2.11': {'UFeats': list(), 'IndFeats': list()}, '2.11-unr': {'UFeats': list(), 'IndFeats': list()}}
scores_d['lemma_only_baseline'] = {'2.8': {'Lemmas': list()}, '2.11': {'Lemmas': list()}, '2.11-unr': {'Lemmas': list()}}
scores_d['pos_only_baseline'] = {'2.8': {'UPOS': list()}, '2.11': {'UPOS': list()}, '2.11-unr': {'UPOS': list()}}
scores_d['dep_parsing'] = {'2.8': {'UAS': list(), 'LAS': list()}, '2.11': {'UAS': list(), 'LAS': list()}, '2.11-unr': {'UAS': list(), 'LAS': list()}}
# MTL
scores_d['dep_parsing_upos_feats_MTL'] = {'2.8': {'UAS': list(), 'LAS': list()}, '2.11': {'UAS': list(), 'LAS': list()}, '2.11-unr': {'UAS': list(), 'LAS': list()}}
scores_d['dep_parsing_upos_MTL'] = {'2.8': {'UPOS': list(), 'UAS': list(), 'LAS': list()}, '2.11': {'UPOS': list(), 'UAS': list(), 'LAS': list()}, '2.11-unr': {'UPOS': list(), 'UAS': list(), 'LAS': list()}}
scores_d['dep_parsing_feats_MTL'] = {'2.8': {'UAS': list(), 'LAS': list()}, '2.11': {'UAS': list(), 'LAS': list()}, '2.11-unr': {'UAS': list(), 'LAS': list()}}
scores_d['dep_parsing_lemma_MTL'] = {'2.8': {'UAS': list(), 'LAS': list()}, '2.11': {'UAS': list(), 'LAS': list()}, '2.11-unr': {'UAS': list(), 'LAS': list()}}
scores_d['upos_feats_MTL'] = {'2.8': {'UFeats': list(), 'IndFeats': list()}, '2.11': {'UFeats': list(), 'IndFeats': list()}, '2.11-unr': {'UFeats': list(), 'IndFeats': list()}}

for key in scores_d.keys():
    tbs = list(scores_d[key].keys())
    for key2 in tbs:
        scores_d[key][key2 + '-small'] = scores_d[key][key2].copy()

scores_d['feats_only_baseline']['2.8']['UFeats'] = [92.49, 92.58, 92.53, 92.88, 92.39]
scores_d['feats_only_baseline']['2.8']['IndFeats'] = []
scores_d['feats_only_baseline']['2.8-small']['UFeats'] = []
scores_d['feats_only_baseline']['2.8-small']['IndFeats'] = []
scores_d['feats_only_baseline']['2.11']['UFeats'] = [82.56, 82.62, 82.86, 82.57, 82.31]
scores_d['feats_only_baseline']['2.11']['IndFeats'] = []
scores_d['feats_only_baseline']['2.11-small']['UFeats'] = [77.06]
scores_d['feats_only_baseline']['2.11-small']['IndFeats'] = []
scores_d['feats_only_baseline']['2.11-unr']['UFeats'] = [82.59]
scores_d['feats_only_baseline']['2.11-unr']['IndFeats'] = []
scores_d['feats_only_baseline']['2.11-unr-small']['UFeats'] = []
scores_d['feats_only_baseline']['2.11-unr-small']['IndFeats'] = []

scores_d['lemma_only_baseline']['2.8']['Lemmas'] = [90.00, 90.07, 90.02, 90.05, 89.99, 90.56]
scores_d['lemma_only_baseline']['2.11']['Lemmas'] = [88.57, 88.14, 88.17, 87.99, 87.91]
scores_d['lemma_only_baseline']['2.11-unr']['Lemmas'] = [87.99]

scores_d['pos_only_baseline']['2.8']['UPOS'] = [92.00, 92.00, 91.95, 91.87, 91.77]
scores_d['pos_only_baseline']['2.11']['UPOS'] = [93.10, 93.18, 93.24, 93.10, 92.96]
scores_d['pos_only_baseline']['2.11-unr']['UPOS'] = [93.00]

scores_d['dep_parsing']['2.8']['UAS'] = [82.51]
scores_d['dep_parsing']['2.8']['LAS'] = [76.55]
scores_d['dep_parsing']['2.8-small']['UAS'] = []
scores_d['dep_parsing']['2.8-small']['LAS'] = []
scores_d['dep_parsing']['2.11']['UAS'] = [82.09]
scores_d['dep_parsing']['2.11']['LAS'] = [75.20]
scores_d['dep_parsing']['2.11-small']['UAS'] = [76.58]
scores_d['dep_parsing']['2.11-small']['LAS'] = [68.34]
scores_d['dep_parsing']['2.11-unr']['UAS'] = [82.29]
scores_d['dep_parsing']['2.11-unr']['LAS'] = [75.41]
scores_d['dep_parsing']['2.11-unr-small']['UAS'] = []
scores_d['dep_parsing']['2.11-unr-small']['LAS'] = []

scores_d['dep_parsing_upos_feats_MTL']['2.8']['UAS'] = [81.80]
scores_d['dep_parsing_upos_feats_MTL']['2.8']['LAS'] = [75.87]
scores_d['dep_parsing_upos_feats_MTL']['2.8-small']['UAS'] = []
scores_d['dep_parsing_upos_feats_MTL']['2.8-small']['LAS'] = []
scores_d['dep_parsing_upos_feats_MTL']['2.11']['UAS'] = [81.19]
scores_d['dep_parsing_upos_feats_MTL']['2.11']['LAS'] = [74.27]
scores_d['dep_parsing_upos_feats_MTL']['2.11-small']['UAS'] = [75.32]
scores_d['dep_parsing_upos_feats_MTL']['2.11-small']['LAS'] = [67.14]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['UAS'] = [81.38]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr']['LAS'] = [74.32]
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr-small']['UAS'] = []
scores_d['dep_parsing_upos_feats_MTL']['2.11-unr-small']['LAS'] = []

scores_d['dep_parsing_upos_MTL']['2.8']['UAS'] = [82.52]
scores_d['dep_parsing_upos_MTL']['2.8']['LAS'] = [76.53]
scores_d['dep_parsing_upos_MTL']['2.8-small']['UAS'] = []
scores_d['dep_parsing_upos_MTL']['2.8-small']['LAS'] = []
scores_d['dep_parsing_upos_MTL']['2.11']['UAS'] = [81.96]
scores_d['dep_parsing_upos_MTL']['2.11']['LAS'] = [75.09]
scores_d['dep_parsing_upos_MTL']['2.11-small']['UAS'] = [76.48]
scores_d['dep_parsing_upos_MTL']['2.11-small']['LAS'] = [68.37]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['UAS'] = [82.06]
scores_d['dep_parsing_upos_MTL']['2.11-unr']['LAS'] = [75.33]
scores_d['dep_parsing_upos_MTL']['2.11-unr-small']['UAS'] = []
scores_d['dep_parsing_upos_MTL']['2.11-unr-small']['LAS'] = []

scores_d['dep_parsing_feats_MTL']['2.8']['UAS'] = [82.36]
scores_d['dep_parsing_feats_MTL']['2.8']['LAS'] = [76.32]
scores_d['dep_parsing_feats_MTL']['2.8-small']['UAS'] = []
scores_d['dep_parsing_feats_MTL']['2.8-small']['LAS'] = []
scores_d['dep_parsing_feats_MTL']['2.11']['UAS'] = [81.78]
scores_d['dep_parsing_feats_MTL']['2.11']['LAS'] = [74.98]
scores_d['dep_parsing_feats_MTL']['2.11-small']['UAS'] = [76.57]
scores_d['dep_parsing_feats_MTL']['2.11-small']['LAS'] = [68.17]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['UAS'] = [81.88]
scores_d['dep_parsing_feats_MTL']['2.11-unr']['LAS'] = [75.02]
scores_d['dep_parsing_feats_MTL']['2.11-unr-small']['UAS'] = []
scores_d['dep_parsing_feats_MTL']['2.11-unr-small']['LAS'] = []

scores_d['dep_parsing_lemma_MTL']['2.8']['UAS'] = [82.25]
scores_d['dep_parsing_lemma_MTL']['2.8']['LAS'] = [76.20]
scores_d['dep_parsing_lemma_MTL']['2.8-small']['UAS'] = []
scores_d['dep_parsing_lemma_MTL']['2.8-small']['LAS'] = []
scores_d['dep_parsing_lemma_MTL']['2.11']['UAS'] = [81.88]
scores_d['dep_parsing_lemma_MTL']['2.11']['LAS'] = [75.12]
scores_d['dep_parsing_lemma_MTL']['2.11-small']['UAS'] = [76.71]
scores_d['dep_parsing_lemma_MTL']['2.11-small']['LAS'] = [68.40]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['UAS'] = [81.91]
scores_d['dep_parsing_lemma_MTL']['2.11-unr']['LAS'] = [75.01]
scores_d['dep_parsing_lemma_MTL']['2.11-unr-small']['UAS'] = []
scores_d['dep_parsing_lemma_MTL']['2.11-unr-small']['LAS'] = []

scores_d['upos_feats_MTL']['2.8']['UFeats'] = [87.09]
scores_d['upos_feats_MTL']['2.8']['IndFeats'] = []
scores_d['upos_feats_MTL']['2.8-small']['UFeats'] = []
scores_d['upos_feats_MTL']['2.8-small']['IndFeats'] = []
scores_d['upos_feats_MTL']['2.11']['UFeats'] = [82.68]
scores_d['upos_feats_MTL']['2.11']['IndFeats'] = []
scores_d['upos_feats_MTL']['2.11-small']['UFeats'] = [77.06]
scores_d['upos_feats_MTL']['2.11-small']['IndFeats'] = []
scores_d['upos_feats_MTL']['2.11-unr']['UFeats'] = [82.78]
scores_d['upos_feats_MTL']['2.11-unr']['IndFeats'] = []
scores_d['upos_feats_MTL']['2.11-unr-small']['UFeats'] = []
scores_d['upos_feats_MTL']['2.11-unr-small']['IndFeats'] = []

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
