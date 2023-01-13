import os, pandas as pd
import json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(THIS_DIR, 'scores.json'), 'r') as f:
    scores_d = json.load(f)

bl_type_l = list(scores_d.keys())
for bl_type in bl_type_l:
    print(bl_type)
    tb_version_l = list(scores_d[bl_type].keys())
    score_l = list()
    for tb_version in tb_version_l:
        metric_l = list(scores_d[bl_type][tb_version].keys())
        metric_l.remove('jobs')
        score_m_l = list()
        for metric in metric_l:
            scores_l = scores_d[bl_type][tb_version][metric]
            if len(scores_l) < 5:
                score_m_l.append('-')
            else:
                avg_score = sum(scores_l) / len(scores_l)
                score_m_l.append('{:.2f}'.format(avg_score))
        score_l.append(score_m_l)
    df = pd.DataFrame(score_l, columns=metric_l, index=tb_version_l)
    print(df)
    print()
