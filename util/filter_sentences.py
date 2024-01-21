import os, json, argparse
from pathlib import Path

def main():
    THIS_DIR = Path(__file__).parent

    parser = argparse.ArgumentParser(description='Filter sentences')
    parser.add_argument('-t1', help='First treebank', required=True)
    parser.add_argument('-t2', help='Second treebank', required=True)
    parser.add_argument('-s', '--same-texts', help='Same texts list')
    args = parser.parse_args()

    with open(args.t1, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)

    with open(args.t2, 'r', encoding='utf-8') as f:
        t2_data = json.load(f)

    sent_ids = [el for el in t1_data.keys()]
    print('Total sentences in t1:', len(sent_ids))

    for sent_id in sent_ids:
        sent1, sent2 = t1_data[sent_id], t2_data[sent_id]
        table1, table2 = sent1['table'], sent2['table']
        if table1 == table2:
            sent_ids.remove(sent_id)
            continue
        text1 = sent1['text'].strip()
        last_char = text1[-1]
        if last_char not in ['.', '?', '!', '"', ')']:
            sent_ids.remove(sent_id)

    if args.same_texts:
        with open(args.same_texts, 'r', encoding='utf-8') as f:
            same_texts = json.load(f)
        count_same = 0
        count_filtered = 0
        for text in same_texts:
            same_text_ids = same_texts[text]
            if type(same_text_ids[0]) == dict:
                train_count = len([el for el in same_text_ids if el['split'] == 'train'])
                dev_count = len([el for el in same_text_ids if el['split'] == 'dev'])
                test_count = len([el for el in same_text_ids if el['split'] == 'test'])
                count_same += train_count + dev_count + test_count
                count_filtered += 1
                if (train_count > 0 and dev_count > 0) or (train_count > 0 and test_count > 0) or (dev_count > 0 and test_count > 0):
                    print()
                    print('Text:', text)
                    if train_count > 0:
                        print('Train count:', train_count)
                    if dev_count > 0:
                        print('Dev count:', dev_count)
                    if test_count > 0:
                        print('Test count:', test_count)
                    print()
                same_text_ids = [el['sent_id'] for el in same_text_ids]
            present_sent_ids = []
            for sent_id in same_text_ids:
                if sent_id in sent_ids:
                    present_sent_ids.append(sent_id)
            if len(present_sent_ids) > 1:
                for sent_id in present_sent_ids:
                    sent_ids.remove(sent_id)
                sent_ids.append(present_sent_ids[0])
        print('Total same sentences:', count_same)
        print('Total filtered same sentences:', count_filtered)

    print('Total sentences in t1 after filtering:', len(sent_ids))

    with open(Path(args.t1).parent / 'filtered_sent_ids.json', 'w', encoding='utf-8') as f:
        json.dump(sent_ids, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()