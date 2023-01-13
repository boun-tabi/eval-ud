import os, pandas as pd
import json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(THIS_DIR, '../trains/scores/scores.json'), 'r') as f:
    scores_d = json.load(f)

bl_type_l = list(scores_d.keys())
for bl_type in bl_type_l:
    print(bl_type, ':', sep='')
    tb_version_l = list(scores_d[bl_type].keys())
    score_l = list()
    for tb_version in tb_version_l:

        score_m_l = list()
        if bl_type in ['feats-only', 'upos_feats']:
            metric_t = 'UFeats'
        elif bl_type == 'lemma-only':
            metric_t = 'Lemmas'
        elif bl_type == 'pos-only':
            metric_t = 'UPOS'
        elif bl_type in ['dep-parsing', 'dep-parsing_upos', 'dep-parsing_feats', 'dep-parsing_upos_feats']:
            metric_t = 'LAS'
        scores_l = scores_d[bl_type][tb_version][metric_t]
        if len(scores_l) == 0:
            continue
        job_l = scores_d[bl_type][tb_version]['jobs']
        avg_score = sum(scores_l) / len(scores_l)
        closest_job, minimum_diff = 0, 100
        for score in scores_l:
            diff_t = abs(score - avg_score)
            if diff_t < minimum_diff:
                minimum_diff = diff_t
                closest_job = job_l[scores_l.index(score)]
        print(f'  {tb_version}: {avg_score:.2f} (job {closest_job})')
    print()
