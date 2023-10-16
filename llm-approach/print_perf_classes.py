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

similarities = []
files = os.listdir(THIS_DIR)
for file in files:
    if file.startswith('different_annotations'):
        similarities.append(os.path.join(THIS_DIR, file))

for summary in summaries:
    for similarity in similarities:
        os.system('echo Model: ' + summary['model'])
        filename = similarity.split('/')[-1]
        os.system('echo Similarity: ' + filename)
        os.system(f'python3 {os.path.join(THIS_DIR, "get_perf_classes.py")} -sum {summary["path"]} -sim {similarity} -c 10')
        os.system('echo')