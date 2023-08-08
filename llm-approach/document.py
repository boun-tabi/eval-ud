import os, json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(THIS_DIR, 'experiment_outputs')
with open(os.path.join(output_dir, 'experiment06_output-tr_boun_v2.11-openai.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

doc_l = []
for el in data:
    sent_id = el['sent_id']
    in_text = el['text']
    out_text = el['output']['content']
    doc_l.append((sent_id, in_text, out_text))

out_str = ''
for sent_id, in_text, out_text in doc_l:
    out_str += '- Sentence ID: {}\n'.format(sent_id)
    out_str += '- Original Text: {}\n'.format(in_text)
    out_str += '- LLM Output: {}\n'.format(out_text)
    out_str += '\n---\n\n'

with open(os.path.join(output_dir, 'experiment06_output-tr_boun_v2.11-openai.txt'), 'w', encoding='utf-8') as f:
    f.write(out_str)