import os, json, argparse
from difflib import SequenceMatcher
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
    return parser.parse_args()

def main():
    args = get_args()

    run_dir = Path(args.run_dir)
    if 'tb_output-cleaned.json' in os.listdir(run_dir):
        tb_out = run_dir / 'tb_output-cleaned.json'
    else:
        tb_out = run_dir / 'tb_output.json'

    res_d = {}
    with open(tb_out, 'r', encoding='utf-8') as f:
        tb_results = json.load(f)
    for sent_id in tb_results.keys():
        original_text, output_text = tb_results[sent_id]['original_text'], tb_results[sent_id]['output_text']
        res_d[sent_id] = {'original_text': original_text, 'output_text': output_text.strip()}
    ratio_acc, all_count = 0, 0
    out_d = {'tb_path': str(tb_out), 'results': {}}
    for sent_id in res_d:
        if sent_id not in res_d or 'output_text' not in res_d[sent_id]:
            continue
        original_text = res_d[sent_id]['original_text']
        output_text = res_d[sent_id]['output_text']
        print('Original text: {}'.format(original_text))
        print('Output text: {}'.format(output_text))
        ratio = SequenceMatcher(None, original_text, output_text).ratio()
        print('Similarity ratio: {}'.format(ratio))
        ratio_acc += ratio
        all_count += 1
        print()
        out_d['results'][sent_id] = {'ratio': float('{:.3f}'.format(ratio)), 'original text': original_text, 'output text': output_text}
    out_d['average ratio'] = float('{:.3f}'.format(ratio_acc / all_count))

    out_d['sentence_count'] = all_count

    keys = list(out_d.keys())
    keys.sort()
    out_d = {k: out_d[k] for k in keys}

    with open(run_dir / 'summary.json', 'w', encoding='utf-8') as f:
        json.dump(out_d, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()