import json, os
import matplotlib.pyplot as plt

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

mispred_path = os.path.join(THIS_DIR, 'feat_mispred.json')
with open(mispred_path, 'r', encoding='utf-8') as f:
    mispred_d = json.load(f)
tbs = list(mispred_d.keys()) 
feat_l = sorted(list(set(list(mispred_d[tbs[0]].keys()) + list(mispred_d[tbs[1]].keys()))))
feat_l.remove('score')

types = ['all', 'pnexist', 'gnexist', 'nmatch']
fig_folder = os.path.join(THIS_DIR, 'figs')
if not os.path.exists(fig_folder):
    os.mkdir(fig_folder)
plt.figure(figsize=(20, 5))
x_count, y_count, width = 1, 1, 5
for feat_t in feat_l:
    values = list()
    names = list()
    for type_t in types:
        for tb in tbs:
            if feat_t in mispred_d[tb].keys():
                values.append(mispred_d[tb][feat_t][type_t])
                names.append('{tb}_{t}'.format(tb=tb, t=type_t))
    if y_count == width:
        x_count += 1
        y_count = 1
    else:
        y_count += 1

#     plt.subplot(int(str(x_count) + str(y_count)))
    plt.figure(figsize=(10, 5))
    plt.scatter(names, values)
    plt.suptitle(feat_t)
    plt.savefig(os.path.join(fig_folder, '{f}.png'.format(f=feat_t)))
# plt.show()
