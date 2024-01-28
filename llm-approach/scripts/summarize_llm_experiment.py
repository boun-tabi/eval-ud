import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
args = parser.parse_args()

run_dir = args.run_dir
if 'output-cleaned.json' in os.listdir(run_dir):
    out_path = os.path.join(run_dir, 'output-cleaned.json')
else:
    out_path = os.path.join(run_dir, 'output.json')

res_d = {}
with open(out_path, 'r', encoding='utf-8') as f:
    results = json.load(f)
llm_pattern = re.compile('The surface form of the sentence is:?\s+"(.+?)"$')
llm_pattern2 = re.compile('\(?Note:.*\)?$')
quote_pattern = re.compile('^"(.+?)"$')
for sent_id in results.keys():
    original_text, output_text = results[sent_id]['original_text'], results[sent_id]['output_text']
    if not output_text:
        continue
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
out_d = {'out_path': out_path, 'results': {}}
for sent_id in res_d:
    if sent_id not in res_d or 'output_text' not in res_d[sent_id]:
        continue
    original_text = res_d[sent_id]['original_text']
    output_text = res_d[sent_id]['output_text']
    print('Original text: {}'.format(original_text))
    print('Output text: {}'.format(output_text))
    ratio = SequenceMatcher(None, original_text, output_text).ratio()
    ratio = float('{:.3f}'.format(ratio))
    print('Similarity ratio: {}'.format(ratio))
    ratio_acc += ratio
    all_count += 1
    print()
    out_d['results'][sent_id] = {'ratio': ratio, 'original text': original_text, 'output text': output_text}
out_d['average ratio'] = float('{:.3f}'.format(ratio_acc / all_count))

out_d['sentence_count'] = all_count

keys = list(out_d.keys())
keys.sort()
out_d = {k: out_d[k] for k in keys}

with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(out_d, f, indent=4, ensure_ascii=False)
