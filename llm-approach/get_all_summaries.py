import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', type=str, help='directory to search for experiments', required=True)
args = parser.parse_args()

folders = os.listdir(args.dir)
summaries = []
for folder in folders:
    files = os.listdir(os.path.join(args.dir, folder))
    for file in files:
        if file == 'summary.json':
            summaries.append({'model': folder, 'path': os.path.join(args.dir, folder, file)})

for summary in summaries:
    with open(summary['path'], 'r', encoding='utf8') as f:
        content = json.load(f)
    print('Model:', summary['model'])
    v2_8_ratio, v2_11_ratio = content['average v2.8 ratio'] * 100, content['average v2.11 ratio'] * 100
    print('Average v2.8 accuracy: {:.2f}'.format(v2_8_ratio))
    print('Average v2.11 accuracy: {:.2f}'.format(v2_11_ratio))
    print()