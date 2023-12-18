import json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s1', '--sent-ids1', type=str, required=True, help='The first sentence ids.')
parser.add_argument('-s2', '--sent-ids2', type=str, required=True, help='The second sentence ids.')
args = parser.parse_args()

with open(args.sent_ids1, 'r', encoding='utf-8') as f:
    sent_ids1 = json.load(f)

with open(args.sent_ids2, 'r', encoding='utf-8') as f:
    sent_ids2 = json.load(f)

print('Number of sentences in 1:', len(sent_ids1))
print('Number of sentences in 2:', len(sent_ids2))
print('Number of sentences in 1 but not in 2:', len([sent_id for sent_id in sent_ids1 if sent_id not in sent_ids2]))
print('Number of sentences in 2 but not in 1:', len([sent_id for sent_id in sent_ids2 if sent_id not in sent_ids1]))
print('Number of sentences in both:', len([sent_id for sent_id in sent_ids1 if sent_id in sent_ids2]))