import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run_dir', type=str, default=None, help='The run directory.')
parser.add_argument('-t8', '--treebank-2-8', type=str, required=True)
parser.add_argument('-t11', '--treebank-2-11', type=str, required=True)
args = parser.parse_args()

with open(args.treebank_2_8, 'r', encoding='utf-8') as f:
    treebank_2_8 = json.load(f)
tb_8 = {}
for sent in treebank_2_8:
    tb_8[sent['sent_id']] = sent['table']
with open(args.treebank_2_11, 'r', encoding='utf-8') as f:
    treebank_2_11 = json.load(f)
tb_11 = {}
for sent in treebank_2_11:
    tb_11[sent['sent_id']] = sent['table']

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, 'experiment_outputs')
if args.run_dir is None:
    run_l_path = os.path.join(THIS_DIR, 'run_l.json')
    if not os.path.exists(run_l_path):
        raise Exception('Please run the pipeline first.')
    run_l = json.load(open(run_l_path, 'r', encoding='utf-8'))
    latest_run = run_l[-1]
    v2_8_out, v2_11_out = latest_run['v2.8'], latest_run['v2.11']
    run_dir = latest_run['run_dir']
else:
    run_dir = args.run_dir
    v2_8_out = os.path.join(run_dir, 'v2.8_output.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output.json')
md_path = os.path.join(run_dir, 'md.json')
if not os.path.exists(md_path):
    raise Exception('Please run the pipeline first.')
md = json.load(open(md_path, 'r', encoding='utf-8'))

res_d = {}
with open(v2_8_out, 'r', encoding='utf-8') as f:
    v2_8_results = json.load(f)
llm_pattern = re.compile('The surface text of the sentence is "(.+?)"$')
for result in v2_8_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']['content']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1)
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text}
with open(v2_11_out, 'r', encoding='utf-8') as f:
    v2_11_results = json.load(f)
for result in v2_11_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']['content']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1)
    res_d[sent_id]['v2_11_text'] = output_text
ratio_acc_v2_8, ratio_acc_v2_11, all_count = 0, 0, 0
split_ratio_acc_v2_8, split_ratio_acc_v2_11, split_all_count = 0, 0, 0
non_split_ratio_acc_v2_8, non_split_ratio_acc_v2_11, non_split_all_count = 0, 0, 0
summary_d = {}
sent_ids = []
out_d = {'v2.8_path': v2_8_out, 'v2.11_path': v2_11_out, 'results': {}, 'sentence_count': len(v2_8_results)}
for sent_id in res_d:
    original_text = res_d[sent_id]['original_text']
    v2_8_text = res_d[sent_id]['v2_8_text']
    v2_11_text = res_d[sent_id]['v2_11_text']
    ratio_v2_8 = SequenceMatcher(None, original_text, v2_8_text).ratio()
    ratio_v2_11 = SequenceMatcher(None, original_text, v2_11_text).ratio()
    ratio_acc_v2_8 += ratio_v2_8
    ratio_acc_v2_11 += ratio_v2_11
    all_count += 1
    split_exists = False
    table_v2_8 = tb_8[sent_id]
    for row in table_v2_8.split('\n'):
        fields = row.split('\t')
        if '-' in fields[0]:
            split_exists = True
            break
    if not split_exists:
        table_v2_11 = tb_11[sent_id]
        for row in table_v2_11.split('\n'):
            fields = row.split('\t')
            if '-' in fields[0]:
                split_exists = True
                break
    if split_exists:
        split_ratio_acc_v2_8 += ratio_v2_8
        split_ratio_acc_v2_11 += ratio_v2_11
        split_all_count += 1
    else:
        non_split_ratio_acc_v2_8 += ratio_v2_8
        non_split_ratio_acc_v2_11 += ratio_v2_11
        non_split_all_count += 1
    out_d['results'][sent_id] = {'v2.8 ratio': ratio_v2_8, 'v2.11 ratio': ratio_v2_11, 'original text': original_text, 'v2.8 text': v2_8_text, 'v2.11 text': v2_11_text, 'split': split_exists}
out_d['average v2.8 ratio'] = ratio_acc_v2_8 / all_count
out_d['average v2.11 ratio'] = ratio_acc_v2_11 / all_count
out_d['all count'] = all_count
out_d['average split v2.8 ratio'] = split_ratio_acc_v2_8 / split_all_count
out_d['average split v2.11 ratio'] = split_ratio_acc_v2_11 / split_all_count
out_d['split count'] = split_all_count
out_d['average non-split v2.8 ratio'] = non_split_ratio_acc_v2_8 / non_split_all_count
out_d['average non-split v2.11 ratio'] = non_split_ratio_acc_v2_11 / non_split_all_count
out_d['non-split count'] = non_split_all_count

with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)
