import os, json
from difflib import SequenceMatcher
from datetime import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, 'experiment_outputs')
run_l_path = os.path.join(THIS_DIR, 'run_l.json')
if not os.path.exists(run_l_path):
    raise Exception('Please run the pipeline first.')
run_l = json.load(open(run_l_path, 'r', encoding='utf-8'))
latest_run = run_l[-1]
v2_8_out, v2_11_out = latest_run['v2.8'], latest_run['v2.11']
run_dir = latest_run['run_dir']

res_d = {}
with open(v2_8_out, 'r', encoding='utf-8') as f:
    v2_8_results = json.load(f)
for result in v2_8_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']['content']
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text}
with open(v2_11_out, 'r', encoding='utf-8') as f:
    v2_11_results = json.load(f)
for result in v2_11_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']['content']
    res_d[sent_id]['v2_11_text'] = output_text
ratio_acc_v2_8, ratio_acc_v2_11, all_count = 0, 0, 0
summary_d = {}
sent_ids = []
out_d = {'v2.8_path': v2_8_out, 'v2.11_path': v2_11_out, 'results': {}}
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
with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)

# Average similarity ratios
## 1
# - 0.6580315517304394 for v2.8
# - 0.6570594332974276 for v2.11
## 2
# - 0.8678245704165665 for v2.8
# - 0.9005500356464718 for v2.11
## 3
# - 0.8376212923623395 for v2.8
# - 0.8546488939079127 for v2.11