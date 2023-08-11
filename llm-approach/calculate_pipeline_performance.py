import os, json
from difflib import SequenceMatcher

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, 'experiment_outputs')
run_l_path = os.path.join(THIS_DIR, 'run_l.json')
if not os.path.exists(run_l_path):
    raise Exception('Please run the pipeline first.')
run_l = json.load(open(run_l_path, 'r', encoding='utf-8'))
latest_run = run_l[-1]
v1_out, v2_out = latest_run['version1'], latest_run['version2']

with open(v1_out, 'r', encoding='utf-8') as f:
    v1_results = json.load(f)
with open(v2_out, 'r', encoding='utf-8') as f:
    v2_results = json.load(f)
print('Version 1')
ratio_acc, all_count = 0, 0
for result in v1_results:
    original_text, output_text = result['text'], result['output']['content']
    print('Original text: {}'.format(original_text))
    print('Output text: {}'.format(output_text))
    ratio = SequenceMatcher(None, original_text, output_text).ratio()
    print('Similarity ratio: {}'.format(ratio))
    ratio_acc += ratio
    all_count += 1
    print()
print('Average similarity ratio: {}'.format(ratio_acc / all_count))
print()
print('Version 2')
ratio_acc, all_count = 0, 0
for result in v2_results:
    original_text, output_text = result['text'], result['output']['content']
    print('Original text: {}'.format(original_text))
    print('Output text: {}'.format(output_text))
    ratio = SequenceMatcher(None, original_text, output_text).ratio()
    print('Similarity ratio: {}'.format(ratio))
    ratio_acc += ratio
    all_count += 1
    print()

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