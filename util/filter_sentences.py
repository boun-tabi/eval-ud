import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='Filter sentences')
    parser.add_argument('-t1', help='First treebank', required=True)
    parser.add_argument('-t2', help='Second treebank', required=True)
    args = parser.parse_args()

    with open(args.t1, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)

    with open(args.t2, 'r', encoding='utf-8') as f:
        t2_data = json.load(f)
    
    t1_sents = {}
    sent_ids = []
    for sent in t1_data:
        sent_id = sent['sent_id']
        t1_sents[sent_id] = {'text': sent['text'], 'table': sent['table']}
        sent_ids.append(sent_id)
    
    t2_sents = {}
    for sent in t2_data:
        t2_sents[sent['sent_id']] = {'text': sent['text'], 'table': sent['table']}
    
    print('Total sentences in t1:', len(t1_sents))
    for sent_id in sent_ids:
        table1, table2 = t1_sents[sent_id]['table'], t2_sents[sent_id]['table']
        if table1 == table2:
            sent_ids.remove(sent_id)
            continue
        text1 = t1_sents[sent_id]['text'].strip()
        last_char = text1[-1]
        if last_char not in ['.', '?', '!', '"', ')']:
            sent_ids.remove(sent_id)
    print('Total sentences in t1 after filtering:', len(sent_ids))

    with open(os.path.join(THIS_DIR, 'filtered_sent_ids.json'), 'w', encoding='utf-8') as f:
        json.dump(sent_ids, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()