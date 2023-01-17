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

feat_d = dict()
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
            # if p_tag_t not in feat_d.keys():
            #     feat_d[p_tag_t] = dict()
            # if p_val_t not in feat_d[p_tag_t].keys():
            #     feat_d[p_tag_t][p_val_t] = dict()
            # if p_val_t not in feat_d[p_tag_t][p_val_t].keys():
            #     feat_d[p_tag_t][p_val_t][p_val_t] = 0
        all_feats_s = set(list(g_feat_d.keys()) + list(p_feat_d.keys()))

        for feat_t in all_feats_s:
            if feat_t not in feat_d.keys():
                feat_d[feat_t] = dict()
            if feat_t not in g_feat_d.keys():
                gold_t = '_'
            else:
                gold_t = g_feat_d[feat_t]
            if gold_t not in feat_d[feat_t].keys():
                feat_d[feat_t][gold_t] = dict()
            # if gold_t not in feat_d[feat_t][gold_t].keys():
            #     feat_d[feat_t][gold_t][gold_t] = 0
            if feat_t not in p_feat_d.keys():
                pred_t = '_'
            else:
                pred_t = p_feat_d[feat_t]
            if pred_t not in feat_d[feat_t][gold_t].keys():
                feat_d[feat_t][gold_t][pred_t] = 0
            feat_d[feat_t][gold_t][pred_t] += 1

feat_l = list(feat_d.keys())
for feat_t in sorted(feat_l):
    print('# ' + feat_t)
    all_vals = set()
    val_l = list(feat_d[feat_t].keys())
    all_vals = all_vals.union(set(val_l))
    for gold_t in val_l:
        val_val_l = list(feat_d[feat_t][gold_t].keys())
        all_vals = all_vals.union(set(val_val_l))
    all_val_l = sorted(list(all_vals))
    board = [[0 for i in range(len(all_val_l)+1)] for j in range(len(all_val_l)+1)]
    board[0][1:] = all_val_l
    for i in range(len(all_val_l)):
        board[i + 1][0] = all_val_l[i]
    for i in range(len(board)):
        for j in range(len(board[i])):
            if i == 0 or j == 0:
                continue
            if board[i][j] == 0:
                if board[i][0] not in feat_d[feat_t].keys():
                    board[i][j] = 0
                elif board[0][j] not in feat_d[feat_t][board[i][0]].keys():
                    board[i][j] = 0
                else:
                    board[i][j] = feat_d[feat_t][board[i][0]][board[0][j]]

    # pprint
    board[0][0] = 'G/P'
    for i, row in enumerate(board):
        for j, el in enumerate(row):
            print(el, end='')
            if j != len(row) - 1:
                print('\t', end='')
        print()
    print()
    # print(',' if i != len(board) - 1 else '', end='')
    # print('-' * 50)