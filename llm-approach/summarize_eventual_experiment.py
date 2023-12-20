import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
args = parser.parse_args()

run_dir = args.run_dir
if 'v2.8_output_modified.json' in os.listdir(run_dir) and 'v2.11_output_modified.json' in os.listdir(run_dir):
    v2_8_out = os.path.join(run_dir, 'v2.8_output_modified.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output_modified.json')
else:
    v2_8_out = os.path.join(run_dir, 'v2.8_output.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output.json')

res_d = {}
with open(v2_8_out, 'r', encoding='utf-8') as f:
    v2_8_results = json.load(f)
llm_pattern = re.compile('The surface form of the sentence is:?\s+"(.+?)"$')
llm_pattern2 = re.compile('\(?Note:.*\)?$')
quote_pattern = re.compile('^"(.+?)"$')
for result in v2_8_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1).strip()
    llm_match2 = llm_pattern2.search(output_text)
    if llm_match2:
        output_text = output_text[:llm_match2.start()].strip()
    quote_match = quote_pattern.search(output_text)
    if quote_match:
        output_text = quote_match.group(1).strip()
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text.strip()}
with open(v2_11_out, 'r', encoding='utf-8') as f:
    v2_11_results = json.load(f)
for result in v2_11_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1).strip()
    llm_match2 = llm_pattern2.search(output_text)
    if llm_match2:
        output_text = output_text[:llm_match2.start()].strip()
    quote_match = quote_pattern.search(output_text)
    if quote_match:
        output_text = quote_match.group(1).strip()
    if sent_id not in res_d:
        res_d[sent_id] = {'original_text': original_text}
    res_d[sent_id]['v2_11_text'] = output_text.strip()
ratio_acc_v2_8, ratio_acc_v2_11, all_count = 0, 0, 0
summary_d = {}
sent_ids = []
out_d = {'v2.8_path': v2_8_out, 'v2.11_path': v2_11_out, 'results': {}}
for sent_id in res_d:
    if sent_id not in res_d or 'v2_8_text' not in res_d[sent_id] or 'v2_11_text' not in res_d[sent_id]:
        continue
    original_text = res_d[sent_id]['original_text']
    v2_8_text = res_d[sent_id]['v2_8_text']
    v2_11_text = res_d[sent_id]['v2_11_text']
    print('Original text: {}'.format(original_text))
    print('Version 2.8 text: {}'.format(v2_8_text))
    print('Version 2.11 text: {}'.format(v2_11_text))
    ratio_v2_8 = SequenceMatcher(None, original_text, v2_8_text).ratio()
    ratio_v2_8 = float('{:.3f}'.format(ratio_v2_8))
    ratio_v2_11 = SequenceMatcher(None, original_text, v2_11_text).ratio()
    ratio_v2_11 = float('{:.3f}'.format(ratio_v2_11))
    print('Similarity ratio (v2.8): {}'.format(ratio_v2_8))
    print('Similarity ratio (v2.11): {}'.format(ratio_v2_11))
    ratio_acc_v2_8 += ratio_v2_8
    ratio_acc_v2_11 += ratio_v2_11
    all_count += 1
    print()
    out_d['results'][sent_id] = {'v2.8 ratio': ratio_v2_8, 'v2.11 ratio': ratio_v2_11, 'original text': original_text, 'v2.8 text': v2_8_text, 'v2.11 text': v2_11_text}
out_d['average v2.8 ratio'] = float('{:.3f}'.format(ratio_acc_v2_8 / all_count))
out_d['average v2.11 ratio'] = float('{:.3f}'.format(ratio_acc_v2_11 / all_count))

out_d['sentence_count'] = all_count

keys = list(out_d.keys())
keys.sort()
out_d = {k: out_d[k] for k in keys}

with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)
