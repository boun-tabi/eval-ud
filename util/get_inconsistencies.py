import argparse, os, re, json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--treebank', action="store", required=True)
args = parser.parse_args()

treebank_folderpath = args.treebank
conllus = [os.path.join(treebank_folderpath, i) for i in os.listdir(treebank_folderpath) if i.endswith('.conllu')]

sent_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'
sents = list()
for conllu in conllus:
    with open(conllu, 'r', encoding='utf-8') as f:
        tb = f.read()
    sents += re.findall(sent_pattern, tb, re.DOTALL)

# CoNLL-U fields: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
field_d = {"id": 0, "form": 1, "lemma": 2, "upos": 3, "xpos": 4,
           "feats": 5, "head": 6, "deprel": 7, "deps": 8, "misc": 9}

annotation_d = dict()
for i in range(len(sents)):
    sent_id, text, lines_str = sents[i]

    lines = lines_str.split('\n')
    for j in range(len(lines)):
        fields = lines[j].split('\t')
        id_t = fields[field_d['id']]
        if '-' in id_t:
            continue
        form = fields[field_d['form']]
        upos = fields[field_d['upos']]
        xpos = fields[field_d['xpos']]
        feats = fields[field_d['feats']]
        if form not in annotation_d.keys():
            annotation_d[form] = {'upos': dict(), 'xpos': dict(), 'feats': dict()}
        if upos not in annotation_d[form]['upos'].keys():
            annotation_d[form]['upos'][upos] = {'count': 0, 'sent_ids': list()}
        annotation_d[form]['upos'][upos]['count'] += 1
        annotation_d[form]['upos'][upos]['sent_ids'].append(sent_id)
        if xpos not in annotation_d[form]['xpos'].keys():
            annotation_d[form]['xpos'][xpos] = {'count': 0, 'sent_ids': list()}
        annotation_d[form]['xpos'][xpos]['count'] += 1
        annotation_d[form]['xpos'][xpos]['sent_ids'].append(sent_id)
        if feats not in annotation_d[form]['feats'].keys():
            annotation_d[form]['feats'][feats] = {'count': 0, 'sent_ids': list()}
        annotation_d[form]['feats'][feats]['count'] += 1
        annotation_d[form]['feats'][feats]['sent_ids'].append(sent_id)

# with open('annotation_d.json', 'w', encoding='utf-8') as f:
#     json.dump(annotation_d, f, ensure_ascii=False, indent=2)

for form in annotation_d.keys():
    annotation = annotation_d[form]
    if len(annotation['upos'].keys()) > 1:
        print(form, 'upos:', annotation['upos'])
    if len(annotation['xpos'].keys()) > 1:
        print(form, 'xpos:', annotation['xpos'])
    if len(annotation['feats'].keys()) > 1:
        print(form, 'feats:', annotation['feats'])
