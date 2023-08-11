import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True)
args = parser.parse_args()

with open(args.file, 'r', encoding='utf-8') as f:
    data = json.load(f)
ratios = [v for k, v in data['ratios'].items()]

counts = []
print('Average ratio: {}'.format(sum(ratios) / len(ratios)))
perc_l = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
for i in range(len(perc_l)-1):
    print('Sentences with ratio between {} and {}: {}'.format(perc_l[i], perc_l[i+1], len([v for v in ratios if v >= perc_l[i] and v < perc_l[i+1]])))
    d = {'lower': perc_l[i], 'upper': perc_l[i+1], 'count': len([v for v in ratios if v >= perc_l[i] and v < perc_l[i+1]])}
    counts.append(d)