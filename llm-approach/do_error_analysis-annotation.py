import os, argparse, json

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    tr_boun_dir = os.path.join(THIS_DIR, '..', 'tr_boun')

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory of the run')
    args = parser.parse_args()

    dir = args.directory
    summary_path = os.path.join(dir, 'summary.json')
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    md_path = os.path.join(dir, 'md.json')
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    model = md['model']

    tb8_path, tb11_path = os.path.join(tr_boun_dir, 'v2.8', 'treebank.json'), os.path.join(tr_boun_dir, 'v2.11', 'treebank.json')
    with open(tb8_path, 'r', encoding='utf-8') as f:
        tb8_temp = json.load(f)
    tb8 = {}
    for el in tb8_temp:
        sent_id = el['sent_id']
        del el['sent_id']
        tb8[sent_id] = el
    with open(tb11_path, 'r', encoding='utf-8') as f:
        tb11 = json.load(f)
    tb11 = {}
    for el in tb11:
        sent_id = el['sent_id']
        del el['sent_id']
        tb11[sent_id].update(el)
    
    if 'results' not in summary:
        print('No results found in file')
        return
    results = summary['results']

    analysis_d = {'sentences': {}}
    for sent_id, value in results.items():
        ratio_v2_8, ratio_v2_11 = value['v2.8 ratio'], value['v2.11 ratio']
        original_text, text_v2_8, text_v2_11 = value['original text'], value['v2.8 text'], value['v2.11 text']
        diff = ratio_v2_11 - ratio_v2_8
        d = {'diff': diff, 'original_text': original_text, 'text_v2_8': text_v2_8, 'text_v2_11': text_v2_11}
        analysis_d['sentences'][sent_id] = d

    with open(os.path.join(THIS_DIR, 'error_analysis-{}-annotation.json'.format(model)), 'w', encoding='utf-8') as f:
        json.dump(analysis_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()