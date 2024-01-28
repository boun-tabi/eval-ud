from pathlib import Path
import argparse, random, json

def get_args():
    parser = argparse.ArgumentParser(description='Randomize annotations')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to input file')
    parser.add_argument('-d', '--docs', type=str, required=True,
                        help='Path to directory containing UD documents')
    parser.add_argument('-o', '--output', type=str, default='randomized-treebank.json',
                        help='Path to output file')
    parser.add_argument('-s', '--seed', type=int, default=42,
                        help='Random seed')
    args = parser.parse_args()
    return args

def get_feat_len_dist(tb_data):
    len_d = {i: 0 for i in range(15)}
    sent_ids = list(tb_data.keys())
    for sent_id in sent_ids:
        table = tb_data[sent_id]['table']
        for row in table.split('\n'):
            fields = row.split('\t')
            feats = fields[5]
            if feats == '_':
                curr_len = 0
            else:
                feat_count = feats.count('|')
                curr_len = feat_count
            if curr_len not in len_d.keys():
                len_d[curr_len] = 0
            len_d[curr_len] += 1
    for len_t in list(len_d.keys()):
        if len_d[len_t] == 0:
            del len_d[len_t]
    dist_d = {}
    len_sum = 0
    for len_t, count_t in len_d.items():
        len_sum += count_t
        dist_d[len_sum] = len_t
    highest_key = len_sum
    return dist_d, highest_key

def get_feat_len(dist_d, highest_key):
    random_number = random.randint(0, highest_key)
    for key, len_t in dist_d.items():
        if random_number < key:
            return len_t

def main():
    args = get_args()
    random.seed(args.seed)

    # UD data
    pos_path, feats_path, dep_path = Path(args.docs, 'pos-tr.json'), Path(args.docs, 'feat-tr.json'), Path(args.docs, 'dep-tr.json')
    with open(pos_path, 'r') as f:
        pos_data = json.load(f)
        pos_list = list(pos_data.keys())
    with open(feats_path, 'r') as f:
        feats_data = json.load(f)
        tag_list = list(feats_data.keys())
        feat_d = { tag: [val for val in
                list(feats_data[tag].keys()) if val != 'shortdef' and val != 'content']
            for tag in tag_list
        }
    with open(dep_path, 'r') as f:
        dep_data = json.load(f)
        dep_list = list(dep_data.keys())

    # treebank data
    with open(args.input, 'r') as f:
        tb_data = json.load(f)
    dist_d, highest_key = get_feat_len_dist(tb_data)

    sent_ids = list(tb_data.keys())
    new_tb_data = {sent_id: {'text': tb_data[sent_id]['text'], 'table': None} for sent_id in sent_ids}
    for sent_id in sent_ids:
        text, table = tb_data[sent_id]['text'], tb_data[sent_id]['table']
        new_table_l = []
        for row in table.split('\n'):
            fields = row.split('\t')
            id_t = fields[0]
            if '-' in id_t:
                new_table_l.append(row)
                continue
            pos_t, feats_t, dep_t = fields[3], fields[5], fields[7]
            new_pos_t, new_feats_t, new_dep_t = None, None, None
            while not new_pos_t or new_pos_t == pos_t:
                new_pos_t = random.choice(pos_list)
            sel_len = get_feat_len(dist_d, highest_key)
            if sel_len == 0:
                new_feats_t = '_'
            else:
                new_feat_tag_s = set()
                while len(new_feat_tag_s) != sel_len:
                    new_feat_tag_s.add(random.choice(tag_list))
                new_feat_tag_l = sorted(list(new_feat_tag_s))
                new_feat_d = {tag: random.choice(feat_d[tag]) for tag in new_feat_tag_l}
                new_feats_t = '|'.join([tag_t + '=' + val_t for tag_t, val_t in new_feat_d.items()])
            while not new_dep_t or new_dep_t == dep_t:
                new_dep_t = random.choice(dep_list)
            fields[3] = new_pos_t
            fields[5] = new_feats_t
            fields[7] = new_dep_t
            new_row = '\t'.join(fields)
            new_table_l.append(new_row)
        new_table = '\n'.join(new_table_l)
        new_tb_data[sent_id]['table'] = new_table
        print('Passed', sent_id)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(new_tb_data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()