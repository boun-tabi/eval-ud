import os, json, argparse
from difflib import SequenceMatcher

THIS_DIR = os.path.dirname(os.path.abspath(__file__)) # util
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True)
parser.add_argument('-s', type=str, required=True)
args = parser.parse_args()

first_path = args.f
with open(first_path, 'r', encoding='utf-8') as f:
    first_data = json.load(f)
f_d = {}
for el in first_data:
    f_d[el['sent_id']] = el['table']
second_path = args.s
with open(second_path, 'r', encoding='utf-8') as f:
    second_data = json.load(f)
s_d = {}
for el in second_data:
    s_d[el['sent_id']] = el['table']
sent_ids = list(set(f_d.keys()).union(set(s_d.keys())))
len_sent_ids = len(sent_ids)
change_d = {}
# similarity_type = 'exact matches among form, lemma, upos and feats strings ; 1 means identical, 0 means completely different ; splits included'
similarity_type = 'SequenceMatcher.ratio between form + lemma + upos + feats strings ; 1.0 means identical, 0.0 means completely different ; splits included'
# small_tag = 'exact_match-upos_feats-with_split'
small_tag = 'seq_ratio-upos_feats-with_split'
for i, sent_id in enumerate(sent_ids):
    # all_count, change_count = 0, 0
    all_count, ratio = 0, 0
    table1, table2 = f_d[sent_id], s_d[sent_id]
    rows1, rows2 = table1.split('\n'), table2.split('\n')
    id1, id2 = 0, 0
    prev_split1, prev_split2 = False, False
    prev_form1, prev_form2 = '', ''
    next_form1, next_form2 = '', ''
    nextnext_form1, nextnext_form2 = '', ''
    problematic = False
    while 1:
        try:
            row1, row2 = rows1[id1], rows2[id2]
        except:
            problematic = True
            print(sent_id)
            break
        fields1, fields2 = row1.split('\t'), row2.split('\t')
        id_t1, id_t2 = fields1[0], fields2[0]
        if '-' in id_t1:
            id1 += 1
            row1 = rows1[id1]
            fields1 = row1.split('\t')
            id_t1 = fields1[0]
            prev_split1 = True
        else:
            prev_split1 = False
        if '-' in id_t2:
            id2 += 1
            row2 = rows2[id2]
            fields2 = row2.split('\t')
            id_t2 = fields2[0]
            prev_split2 = True
        else:
            prev_split2 = False
        form1, lemma1, upos1, feats1 = fields1[1], fields1[2], fields1[3], fields1[5]
        str1 = '{} {} {} {}'.format(form1, lemma1, upos1, feats1)
        form2, lemma2, upos2, feats2 = fields2[1], fields2[2], fields2[3], fields2[5]
        str2 = '{} {} {} {}'.format(form2, lemma2, upos2, feats2)
        ratio += SequenceMatcher(None, str1, str2).ratio()
        all_count += 1
        # if form1 != form2:
        #     change_count += 1
        # if lemma1 != lemma2:
        #     change_count += 1
        # if upos1 != upos2:
        #     change_count += 1
        # feat_l1, feat_l2 = feats1.split('|'), feats2.split('|')
        # feat_d1, feat_d2 = {}, {}
        # if not (len(feat_l1) == 1 and feat_l1[0] == '_'):
        #     for feat in feat_l1:
        #         tag, val = feat.split('=')
        #         feat_d1[tag] = val
        # if not (len(feat_l2) == 1 and feat_l2[0] == '_'):
        #     for feat in feat_l2:
        #         tag, val = feat.split('=')
        #         feat_d2[tag] = val
        # feat_union = set(feat_d1.keys()).union(set(feat_d2.keys()))
        # for feat in feat_union:
        #     if feat not in feat_d1 or feat not in feat_d2:
        #         change_count += 1
        #     elif feat_d1[feat] != feat_d2[feat]:
        #         change_count += 1
        # all_count += 4 + len(feat_union)
        if not prev_split1:
            id2 += 1
        if not prev_split2:
            id1 += 1
        if id1 >= len(rows1) and id2 >= len(rows2):
            break
        prev_form1 = rows1[id1 - 2].split('\t')[1]
        if id1 < len(rows1):
            next_form1 = rows1[id1].split('\t')[1]
        if id1 + 1 < len(rows1):
            nextnext_form1 = rows1[id1 + 1].split('\t')[1]
        prev_form2 = rows2[id2 - 2].split('\t')[1]
        if id2 < len(rows2):
            next_form2 = rows2[id2].split('\t')[1]
        if id2 + 1 < len(rows2):
            nextnext_form2 = rows2[id2 + 1].split('\t')[1]
        if form1 + next_form1 == form2 and not prev_split1:
            id2 -= 1
        elif prev_form1 + form1 + next_form1 == form2 and not prev_split1:
            id2 -= 1
        elif form1 + next_form1 + nextnext_form1 == form2 and not prev_split1:
            id2 -= 1
        elif form2 + next_form2 == form1 and not prev_split2:
            id1 -= 1
        elif prev_form2 + form2 + next_form2 == form1 and not prev_split2:
            id1 -= 1
        elif form2 + next_form2 + nextnext_form2 == form1 and not prev_split2:
            id1 -= 1
    if problematic:
        continue
    # change_d[sent_id] = change_count / all_count
    change_d[sent_id] = ratio / all_count
    if i % 1000 == 0:
        print('Remaining: {} / {}'.format(len_sent_ids - i, len_sent_ids))
change_d = {'similarity_type': similarity_type, 'ratios': {k: v for k, v in sorted(change_d.items(), key=lambda item: item[1], reverse=True)}}
with open(os.path.join(THIS_DIR, 'different_annotations-{}.json'.format(small_tag)), 'w', encoding='utf-8') as f:
    json.dump(change_d, f, ensure_ascii=False, indent=4)