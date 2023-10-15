import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
args = parser.parse_args()

run_dir = args.run_dir
v2_8_out = os.path.join(run_dir, 'v2.8_output.json')
v2_11_out = os.path.join(run_dir, 'v2.11_output.json')

res_d = {}
with open(v2_8_out, 'r', encoding='utf-8') as f:
    v2_8_results = json.load(f)
llm_pattern = re.compile('The surface form of the sentence is:? "(.+?)"$')
for result in v2_8_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1)
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text.strip()}
with open(v2_11_out, 'r', encoding='utf-8') as f:
    v2_11_results = json.load(f)
for result in v2_11_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1)
    res_d[sent_id]['v2_11_text'] = output_text.strip()
ratio_acc_v2_8, ratio_acc_v2_11, all_count = 0, 0, 0
summary_d = {}
sent_ids = []
out_d = {'v2.8_path': v2_8_out, 'v2.11_path': v2_11_out, 'results': {}, 'sentence_count': len(v2_8_results)}
for sent_id in res_d:
    original_text = res_d[sent_id]['original_text']
    v2_8_text = res_d[sent_id]['v2_8_text']
    v2_11_text = res_d[sent_id]['v2_11_text']
    print('Original text: {}'.format(original_text))
    print('Version 2.8 text: {}'.format(v2_8_text))
    print('Version 2.11 text: {}'.format(v2_11_text))
    ratio_v2_8 = SequenceMatcher(None, original_text, v2_8_text).ratio()
    ratio_v2_11 = SequenceMatcher(None, original_text, v2_11_text).ratio()
    print('Similarity ratio (v2.8): {}'.format(ratio_v2_8))
    print('Similarity ratio (v2.11): {}'.format(ratio_v2_11))
    ratio_acc_v2_8 += ratio_v2_8
    ratio_acc_v2_11 += ratio_v2_11
    all_count += 1
    print()
    out_d['results'][sent_id] = {'v2.8 ratio': ratio_v2_8, 'v2.11 ratio': ratio_v2_11, 'original text': original_text, 'v2.8 text': v2_8_text, 'v2.11 text': v2_11_text}
out_d['average v2.8 ratio'] = ratio_acc_v2_8 / all_count
out_d['average v2.11 ratio'] = ratio_acc_v2_11 / all_count

with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)
