import argparse, os, re, json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--gold', action="store", required=True)
parser.add_argument('--pred', action="store", required=True)
args = parser.parse_args()

gold_filepath = args.gold
pred_filepath = args.pred

gold_sent_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'
pred_sent_pattern = r'(.*?)\n\n'
with open(gold_filepath, 'r', encoding='utf-8') as f:
    gold_tb = f.read()
with open(pred_filepath, 'r', encoding='utf-8') as f:
    pred_tb = f.read()
gold_sents = re.findall(gold_sent_pattern, gold_tb, re.DOTALL)
pred_sents = re.findall(pred_sent_pattern, pred_tb, re.DOTALL)

pred_correct = 0
feat_count = 0
conf_d = dict()
feat_count_d = dict()
for i in range(len(gold_sents)):
    g_sent_id, g_text, g_lines_str = gold_sents[i]
    p_lines_str = pred_sents[i]

    g_lines = g_lines_str.split('\n')
    p_lines = p_lines_str.split('\n')
    for j in range(len(g_lines)):
        g_feats = g_lines[j].split('\t')[5].split('|')
        p_feats = p_lines[j].split('\t')[5].split('|')
        g_feat_d = dict()
        p_feat_d = dict()
        for g_feat_t in g_feats:
            if g_feat_t == '_':
                continue
            g_tag_t, g_val_t = g_feat_t.split('=')
            g_feat_d[g_tag_t] = g_val_t
        for p_feat_t in p_feats:
            if p_feat_t == '_':
                continue
            p_tag_t, p_val_t = p_feat_t.split('=')
            p_feat_d[p_tag_t] = p_val_t
        all_feats_s = set(list(g_feat_d.keys()) + list(p_feat_d.keys()))

        feat_count += len(all_feats_s)
        for feat_t in all_feats_s:
            if feat_t not in feat_count_d.keys():
                feat_count_d[feat_t] = 0
            feat_count_d[feat_t] += 1
            if feat_t not in conf_d.keys():
                conf_d[feat_t] = {'all': 0, 'nmatch': 0, 'gnexist': 0, 'pnexist': 0}
            if feat_t in g_feat_d.keys() and feat_t in p_feat_d.keys() and g_feat_d[feat_t] == p_feat_d[feat_t]:
                conf_d[feat_t]['all'] += 1
            else:
                if feat_t not in p_feat_d.keys():
                    conf_d[feat_t]['pnexist'] += 1
                elif feat_t not in g_feat_d.keys():
                    conf_d[feat_t]['gnexist'] += 1
                elif g_feat_d[feat_t] != p_feat_d[feat_t]:
                    conf_d[feat_t]['nmatch'] += 1

tag_l = sorted(list(conf_d.keys()))
for feat_t in tag_l:
    all_t, nmatch, gnexist, pnexist = conf_d[feat_t]['all'], conf_d[feat_t]['nmatch'], conf_d[feat_t]['gnexist'], conf_d[feat_t]['pnexist']
    print('# {}'.format(feat_t))
    print('G/P\t0\t1')
    print(f'0\t{nmatch}\t{gnexist}')
    print(f'1\t{pnexist}\t{all_t}')
    print()