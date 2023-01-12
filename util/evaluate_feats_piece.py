# python3 util/evaluate_feats_piece.py --gold gold.conllu --pred pred.conllu
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
# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}

pred_correct = 0
feat_count = 0
mispred_feat_d = dict()
feat_count_d = dict()
# g_line_count = 0
# p_line_count = 0
for i in range(len(gold_sents)):
    g_sent_id, g_text, g_lines_str = gold_sents[i]
    p_lines_str = pred_sents[i]

    g_lines = g_lines_str.split('\n')
    p_lines = p_lines_str.split('\n')
#     g_line_count += len(g_lines)
#     p_line_count += len(p_lines)
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
            if feat_t not in mispred_feat_d.keys():
                mispred_feat_d[feat_t] = {'all': 0, 'nmatch': 0, 'gnexist': 0, 'pnexist': 0}
            if feat_t in g_feat_d.keys() and feat_t in p_feat_d.keys() and g_feat_d[feat_t] == p_feat_d[feat_t]:
                pred_correct += 1
            else:
                if feat_t not in p_feat_d.keys():
                    mispred_feat_d[feat_t]['pnexist'] += 1
                elif feat_t not in g_feat_d.keys():
                    mispred_feat_d[feat_t]['gnexist'] += 1
                elif g_feat_d[feat_t] != p_feat_d[feat_t]:
                    mispred_feat_d[feat_t]['nmatch'] += 1
                mispred_feat_d[feat_t]['all'] += 1

mispred_d = dict()
mispred_path = os.path.join(THIS_DIR, 'feat_mispred.json')
if os.path.exists(mispred_path):
    with open(mispred_path, 'r', encoding='utf-8') as f:
        mispred_d = json.load(f)
else:
    mispred_d = dict()
mispred_d[args.gold] = dict()
for feat_t in feat_count_d.keys():
    mispred_d[args.gold][feat_t] = dict()
    mispred_d[args.gold][feat_t]['all'] = mispred_feat_d[feat_t]['all'] / feat_count_d[feat_t]
    mispred_d[args.gold][feat_t]['pnexist'] = mispred_feat_d[feat_t]['pnexist'] / feat_count_d[feat_t]
    mispred_d[args.gold][feat_t]['gnexist'] = mispred_feat_d[feat_t]['gnexist'] / feat_count_d[feat_t]
    mispred_d[args.gold][feat_t]['nmatch'] = mispred_feat_d[feat_t]['nmatch'] / feat_count_d[feat_t]
mispred_d[args.gold]['score'] = pred_correct / feat_count
with open(mispred_path, 'w', encoding='utf-8') as f:
    json.dump(mispred_d, f, ensure_ascii=False, indent=4)


# print(g_line_count, p_line_count)
print('Feature based score: {:.2f}'.format((pred_correct / feat_count)*100))
# print('Misprediction percentages:')
# for feat_t in feat_count_d.keys():
#     print('{f}: {p:.2f} in {c}'.format(f=feat_t, p=mispred_feat_d[feat_t] / feat_count_d[feat_t], c=feat_count_d[feat_t]))
