import argparse, os, re, sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

print(sys.argv)

parser = argparse.ArgumentParser()
parser.add_argument('--train', action="store", required=True)
parser.add_argument('--test', action="store", required=True)
args = parser.parse_args()

train_filepath = args.train
test_filepath = args.test
sentence_pattern = r'(.*?)\n\n'
with open(train_filepath, 'r', encoding='utf-8') as f:
    train_tb = f.read()
train_sentences = re.findall(sentence_pattern, train_tb, re.DOTALL)
with open(test_filepath, 'r', encoding='utf-8') as f:
    test_tb = f.read()
test_sentences = re.findall(sentence_pattern, test_tb, re.DOTALL)

train_feat_set = set()
for tr_sent in train_sentences:
    lines = [i for i in tr_sent.split('\n') if not i.startswith('#')]
    for j, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        feats_t = fields[5]
        train_feat_set.add(feats_t)
test_feat_set = set()
for test_sent in test_sentences:
    lines = [i for i in test_sent.split('\n') if not i.startswith('#')]
    for j, line in enumerate(lines):
        fields = line.split('\t')
        if len(fields) != 10:
            continue
        feats_t = fields[5]
        test_feat_set.add(feats_t)
extra_vocab_cnt = 0
for feat_t in train_feat_set:
    if feat_t not in test_feat_set:
        extra_vocab_cnt += 1
print(extra_vocab_cnt)