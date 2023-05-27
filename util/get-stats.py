import argparse, json, os

parser = argparse.ArgumentParser()
parser.add_argument('--stats', action="store", required=True)
args = parser.parse_args()

import xml.etree.ElementTree as ET

treebank_d = dict()

print(args.stats)
tree = ET.parse(args.stats)
root = tree.getroot()
treebank_d['token_count'] = int(root.find('size').find('total').find('tokens').text)
treebank_d['lemmas'] = root.find('lemmas').attrib
treebank_d['forms'] = root.find('forms').attrib
treebank_d['fusions'] = root.find('fusions').attrib

treebank_d['tags'] = dict()
tags = root.find('tags').findall('tag')
for tag in tags:
    treebank_d['tags'][tag.get('name')] = tag.text

treebank_d['feats'] = dict()
feats = root.find('feats').findall('feat')
for feat in feats:
    # treebank_d['feats']['='.join([feat.get('name'), feat.get('value')])] = {'upos': feat.get('upos'), 'count': feat.text}
    treebank_d['feats']['='.join([feat.get('name'), feat.get('value')])] = feat.text

treebank_d['deps'] = dict()
deps = root.find('deps').findall('dep')
for dep in deps:
    treebank_d['deps'][dep.get('name')] = dep.text

print(treebank_d)

with open(os.path.join(os.path.dirname(args.stats), 'stats.json'), 'w', encoding='utf-8') as f:
    json.dump(treebank_d, f, ensure_ascii=False, indent=4)
