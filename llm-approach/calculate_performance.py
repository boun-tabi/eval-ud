import os, json, argparse
from difflib import SequenceMatcher

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, 'experiment_outputs')
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--experiment', type=str, required=True)
args = parser.parse_args()

with open(args.experiment, 'r', encoding='utf-8') as f:
    results = json.load(f)
text_l = []
ratio_acc, all_count = 0, 0
for result in results:
    original_text, output_text = result['text'], result['output']['content']
    print('Original text: {}'.format(original_text))
    print('Output text: {}'.format(output_text))
    ratio = SequenceMatcher(None, original_text, output_text).ratio()
    print('Similarity ratio: {}'.format(ratio))
    ratio_acc += ratio
    all_count += 1
    print()
print('Average similarity ratio: {}'.format(ratio_acc / all_count))

# Average similarity ratios
## 1
# - 0.6580315517304394 for v2.8
# - 0.6570594332974276 for v2.11
## 2
# - 0.8678245704165665 for v2.8
# - 0.9005500356464718 for v2.11
## 3
# - 0.8376212923623395 for v2.8
# - 0.8546488939079127 for v2.11