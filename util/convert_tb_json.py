import argparse, os, re, json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('--treebank', action="store", required=True)
args = parser.parse_args()

tb_type_l = ['dev', 'test', 'train']

tb_folderpath = args.treebank
tb_files = [os.path.join(tb_folderpath, i) for i in os.listdir(tb_folderpath) if i.endswith('.conllu')]
sentence_pattern = r'# sent_id = (.*?)\n# text = (.*?)\n(.*?)\n\n'
tb_d = dict()
for file in tb_files:
    with open(file, 'r', encoding='utf-8') as f:
        tb = f.read()
    sentences = re.findall(sentence_pattern, tb, re.DOTALL)

    for sentence in sentences:
        sent_id, text, annotation = sentence
        if sent_id in tb_d.keys():
            print('Duplicate sent_id:', sent_id)
        tb_d[sent_id] = {'text': text, 'annotation': annotation}

with open(os.path.join(tb_folderpath, 'tb.json'), 'w', encoding='utf-8') as f:
    json.dump(tb_d, f, ensure_ascii=False)
