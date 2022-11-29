import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--stats', action="store", required=True)
args = parser.parse_args()

import xml.etree.ElementTree as ET

tree = ET.parse(args.stats)
root = tree.getroot()
total_token_count = int(root.find('size').find('total').find('tokens').text)
feats = root.find('feats').findall('feat')
feat_count = 0
for feat in feats:
    feat_count += int(feat.text)
print('Non-unique feats:', feat_count)
print('Total tokens:', total_token_count)
print('Feats per token:', feat_count / total_token_count)

# used to calculate feats per token in treebanks UD_English-ATIS (1.0251296885857883) & UD_Turkish-ATIS (2.4460817438692097)

'''
UD_English-ATIS/stats.xml:
Non-unique feats: 63434
Total tokens: 61879
Feats per token: 1.0251296885857883

UD_Turkish-ATIS/stats.xml:
Non-unique feats: 112214
Total tokens: 45875
Feats per token: 2.4460817438692097
'''
