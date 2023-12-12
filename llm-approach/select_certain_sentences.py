import os, json, argparse, random

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--sent-ids', type=str, required=True)
    parser.add_argument('-tb', '--treebank', type=str, required=True)
    parser.add_argument('-n', '--num_sentences', type=int, required=True)
    parser.add_argument('--note', type=str, default='')
    parser.add_argument('-s', '--seed', type=int, default=42)
    args = parser.parse_args()

    sent_ids_path = args.sent_ids
    treebank_path = args.treebank
    num_sentences = args.num_sentences
    seed = args.seed

    random.seed(seed)

    with open(sent_ids_path, 'r') as f:
        sent_ids = json.load(f)
    
    with open(treebank_path, 'r', encoding='utf-8') as f:
        treebank = json.load(f)
    
    possible_sent_ids = []
    for sent_id in sent_ids:
        table = treebank[sent_id]['table']

        has_conv, has_ptcp = False, False
        has_advcl, has_acl, has_ccomp = False, False, False
        for line in table.split('\n'):
            fields = line.split('\t')
            feats_t, deprel_t = fields[5], fields[7]
            feats_l = feats_t.split('|')
            for feat_t in feats_l:
                if feat_t == 'VerbForm=Conv':
                    has_conv = True
                elif feat_t == 'VerbForm=Part':
                    has_ptcp = True
            if deprel_t == 'advcl':
                has_advcl = True
            elif deprel_t == 'acl':
                has_acl = True
            elif deprel_t == 'ccomp':
                has_ccomp = True
        if (has_conv or has_ptcp) and (has_advcl or has_acl or has_ccomp):
            possible_sent_ids.append(sent_id)
    
    print('Number of possible sentences: {}'.format(len(possible_sent_ids)))

    selected_sent_ids = random.sample(sent_ids, num_sentences)
    random.shuffle(selected_sent_ids)

    if args.note:
        sel_path = os.path.join(THIS_DIR, 'selected_certain_sents_{}.json'.format(args.note))
        if os.path.exists(sel_path):
            raise ValueError('File already exists: {}'.format(sel_path))
        with open(sel_path, 'w') as f:
            json.dump(selected_sent_ids, f, indent=4, ensure_ascii=False)
    else:
        with open(os.path.join(THIS_DIR, 'selected_sents.json'), 'w') as f:
            json.dump(selected_sent_ids, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()