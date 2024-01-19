import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
args = parser.parse_args()

run_dir = args.run_dir
if 'tb_output_modified.json' in os.listdir(run_dir):
    tb_out = os.path.join(run_dir, 'tb_output_modified.json')
else:
    tb_out = os.path.join(run_dir, 'tb_output.json')

res_d = {}
with open(tb_out, 'r', encoding='utf-8') as f:
    tb_results = json.load(f)
llm_pattern = re.compile('The surface form of the sentence is:?\s+"(.+?)"$')
llm_pattern2 = re.compile('\(?Note:.*\)?$')
quote_pattern = re.compile('^"(.+?)"$')
for result in tb_results:
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
    res_d[sent_id] = {'original_text': original_text, 'output_text': output_text.strip()}
ratio_acc, all_count = 0, 0
summary_d = {}
sent_ids = []
out_d = {'tb_path': tb_out, 'results': {}, 'sentence_count': len(tb_results)}
for sent_id in res_d:
    original_text = res_d[sent_id]['original_text']
    output_text = res_d[sent_id]['output_text']
    print('Original text: {}'.format(original_text))
    print('Output text: {}'.format(output_text))
    ratio_tb = SequenceMatcher(None, original_text, output_text).ratio()
    print('Similarity ratio: {}'.format(ratio_tb))
    ratio_acc += ratio_tb
    all_count += 1
    print()
    out_d['results'][sent_id] = {'tb ratio': ratio_tb, 'original text': original_text, 'output text': output_text}
out_d['average ratio'] = ratio_acc / all_count

keys = list(out_d.keys())
keys.sort()
out_d = {k: out_d[k] for k in keys}

with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)
