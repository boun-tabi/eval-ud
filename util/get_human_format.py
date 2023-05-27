import os, re, argparse

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument('--conllu', action="store", required=True)
args = parser.parse_args()

annotation_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'

with open(args.conllu, 'r', encoding='utf-8') as f:
    content = f.read()

annotations = re.findall(annotation_pattern, content, re.DOTALL)
anno_t = annotations[2]

preamble = 'The following is a Turkish sentence annotated with morphological features and part-of-speech tags. You are supposed to use the given linguistic information to create the original grammatical sentence in surface form. Lemmas should be expanded using the features.\n\n'
prompt = preamble

table = anno_t[2].split('\n')
for line in table:
    fields = line.split('\t')
    id_t, form_t, lemma_t, upos_t, xpos_t, feats_t, head_t, deprel_t, deps_t, misc_t = fields
    if lemma_t == '_':
        continue
    prompt += f"Lemma '{lemma_t}' has been annotated with the following morphological features '{feats_t}' and the part-of-speech tag '{upos_t}'.\n"

print(prompt)