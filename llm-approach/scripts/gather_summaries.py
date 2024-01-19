import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, 'experiment_outputs')

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--experiment', type=str, required=True)
args = parser.parse_args()

exp_dir = os.path.join(OUTPUT_DIR, args.experiment)
runs = [d for d in os.listdir(exp_dir) if os.path.isdir(os.path.join(exp_dir, d))]
for run in runs:
    run_dir = os.path.join(exp_dir, run)
    summary_path = os.path.join(run_dir, 'summary.json')
    if not os.path.exists(summary_path):
        continue
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    print('Run: {}'.format(run))
    sentence_count = summary['sentence_count']
    class_count = summary['class_count']
    v2_8_ratio = summary['average v2.8 ratio']
    v2_11_ratio = summary['average v2.11 ratio']
    print('Sentence count: {}'.format(sentence_count))
    print('Class count: {}'.format(class_count))
    print('Average v2.8 ratio: {}'.format(v2_8_ratio))
    print('Average v2.11 ratio: {}'.format(v2_11_ratio))
    print()