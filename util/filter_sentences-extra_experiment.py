import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='Filter sentences')
    parser.add_argument('-tb', '--treebank', help='Treebank', required=True)
    parser.add_argument('-n', '--note', type=str, default='')
    args = parser.parse_args()

    with open(args.treebank, 'r', encoding='utf-8') as f:
        tb_data = json.load(f)
    
    tb_sents = {}
    sent_ids = []
    for sent in tb_data:
        sent_id = sent['sent_id']
        tb_sents[sent_id] = {'text': sent['text'], 'table': sent['table']}
        sent_ids.append(sent_id)

    print('Total sentences in tb:', len(tb_sents))
    for sent_id in sent_ids:
        table = tb_sents[sent_id]['table']
        text = tb_sents[sent_id]['text'].strip()
        last_char = text[-1]
        if last_char not in ['.', '?', '!', '"', ')']:
            sent_ids.remove(sent_id)
    print('Total sentences in tb after filtering:', len(sent_ids))

    if args.note:
        with open(os.path.join(THIS_DIR, 'filtered_sent_ids_{}.json'.format(args.note)), 'w', encoding='utf-8') as f:
            json.dump(sent_ids, f, ensure_ascii=False, indent=4)
    else:
        with open(os.path.join(THIS_DIR, 'filtered_sent_ids.json'), 'w', encoding='utf-8') as f:
            json.dump(sent_ids, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()