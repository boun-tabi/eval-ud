import os, json, re, argparse
from difflib import SequenceMatcher
from templates import template2, tr_noun_order, tr_verb_order

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
parser.add_argument('-s', '--sent-ids', type=str, required=True, help='The sentence ids.')
parser.add_argument('-l', '--language', type=str, required=True, help='The language.')
args = parser.parse_args()

lang = args.language

with open(args.sent_ids, 'r', encoding='utf-8') as f:
    sent_ids = json.load(f)

template = template2

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'ud-docs')
with open(os.path.join(data_dir, f'feat-{lang}.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, f'pos-{lang}.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)
with open(os.path.join(data_dir, f'dep-{lang}.json'), 'r', encoding='utf-8') as f:
    dep_d = json.load(f)

def get_prompt(table):
    lines = table.split('\n')
    prompt_l = []
    split_count = 0
    just_left = False
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t = fields[0], fields[2], fields[3], fields[5]
        if split_count > 0:
            prompt_l.append('\t- ' + id_t)
            split_count -= 1
            if split_count == 0:
                just_left = True
        else:
            prompt_l.append('- ' + id_t)
        if '-' in id_t:
            split_count = 2
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        if split_count or just_left:
            prompt_l.append('\t\t- lemma: _{lemma}_'.format(lemma=lemma_t))
            prompt_l.append('\t\t- part of speech: {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        else:
            prompt_l.append('\t- lemma: _{lemma}_'.format(lemma=lemma_t))
            prompt_l.append('\t- part of speech: {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        if pos_t in ['NOUN', 'VERB']:
            sorted_feat_l = []
            feat_copy = feat_l.copy()
            if pos_t == 'NOUN':
                order_l = tr_noun_order
            elif pos_t == 'VERB':
                order_l = tr_verb_order
            for feat_name in order_l:
                for feat in feat_l:
                    tag, val = feat.split('=')
                    if tag == feat_name:
                        sorted_feat_l.append(feat)
                        feat_copy.remove(feat)
            sorted_feat_l.extend(feat_copy)
            feat_l = sorted_feat_l
        for feat in feat_l:
            psor_on = False
            feat_name, feat_value = feat.split('=')
            if feat_name.endswith('[psor]'):
                feat_name = feat_name.replace('[psor]', '')
                psor_on = True
            if feat_name in tag_value_d:
                feat_phrase = tag_value_d[feat_name]['shortdef']
                if feat_value in tag_value_d[feat_name]:
                    feat_value = tag_value_d[feat_name][feat_value]['shortdef']
            else:
                feat_phrase = feat_name
            if psor_on:
                if split_count or just_left:
                    prompt_l.append('\t\t- possessor\'s {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    prompt_l.append('\t- possessor\'s {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
            else:
                if split_count or just_left:
                    prompt_l.append('\t\t- {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    prompt_l.append('\t- {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
        just_left = False
    prompt = '\n'.join(prompt_l)
    return prompt

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
run_dir = args.run_dir
model = run_dir.split('/')[-1]
if 'v2.8_output_modified.json' in os.listdir(run_dir) and 'v2.11_output_modified.json' in os.listdir(run_dir):
    v2_8_out = os.path.join(run_dir, 'v2.8_output_modified.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output_modified.json')
else:
    v2_8_out = os.path.join(run_dir, 'v2.8_output.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output.json')

md_path = os.path.join(run_dir, 'md.json')
with open(md_path, 'r', encoding='utf-8') as f:
    md = json.load(f)
v2_8_path = md['v2.8']
with open(v2_8_path, 'r', encoding='utf-8') as f:
    v2_8_tb = json.load(f)
v2_11_path = md['v2.11']
with open(v2_11_path, 'r', encoding='utf-8') as f:
    v2_11_tb = json.load(f)

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
    table = v2_8_tb[sent_id]['table']
    prompt = get_prompt(table)
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text.strip(), 'v2_8_prompt': prompt, 'v2_8_table': table}
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
    res_d[sent_id]['v2_11_text'] = output_text.strip()
    table = v2_11_tb[sent_id]['table']
    prompt = get_prompt(table)
    res_d[sent_id]['v2_11_prompt'] = prompt
    res_d[sent_id]['v2_11_table'] = table

questions = {'template': template}
for i, sent_id in enumerate(sent_ids):
    original_text = res_d[sent_id]['original_text']
    v2_8_text = res_d[sent_id]['v2_8_text']
    v2_8_table = res_d[sent_id]['v2_8_table']
    v2_11_text = res_d[sent_id]['v2_11_text']
    v2_11_table = res_d[sent_id]['v2_11_table']
    ratio_v2_8 = SequenceMatcher(None, original_text, v2_8_text).ratio()
    ratio_v2_11 = SequenceMatcher(None, original_text, v2_11_text).ratio()
    d = {'original_text': original_text}
    d['v2_8_text'] = v2_8_text
    d['v2_8_table'] = v2_8_table
    d['v2_11_text'] = v2_11_text
    d['v2_11_table'] = v2_11_table
    d['v2_8_prompt'] = res_d[sent_id]['v2_8_prompt']
    d['v2_11_prompt'] = res_d[sent_id]['v2_11_prompt']
    questions[sent_id] = d

print('Number of sentences:', len(questions) - 1)
question_count = 0
for q in questions:
    if 'v2_8_prompt' in questions[q]:
        question_count += 1
    if 'v2_11_prompt' in questions[q]:
        question_count += 1
print('question count:', question_count)
with open(os.path.join(THIS_DIR, 'created_questions_md-random-{}.json'.format(model)), 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=4, ensure_ascii=False)