import json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str, default='treebank.json')
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    tb_path = Path(args.treebank)
    print('Treebank path:', tb_path)
    tb_dir = tb_path.parent

    with open(tb_path, 'r') as f:
        data = json.load(f)
    
    split_key_exists = False
    first_sent_id = list(data.keys())[0]
    if 'split' in data[first_sent_id].keys():
        split_key_exists = True

    text_d = {}
    for sent_id in data.keys():
        text = data[sent_id]['text']
        if text not in text_d.keys():
            text_d[text] = []
        if split_key_exists:
            text_d[text].append({'sent_id': sent_id, 'split': data[sent_id]['split']})
        else:
            text_d[text].append(sent_id)

    texts = list(text_d.keys())
    for text in texts:
        if len(text_d[text]) > 1:
            print(text, text_d[text])
        else:
            del text_d[text]

    print('Done')

    with open(tb_dir / 'same_text_list.json', 'w', encoding='utf-8') as f:
        json.dump(text_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()