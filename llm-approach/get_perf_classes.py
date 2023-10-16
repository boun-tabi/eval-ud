import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-sum', '--summary', required=True)
parser.add_argument('-sim', '--similarity', required=True)
parser.add_argument('-c', '--classes', required=True, type=int)
args = parser.parse_args()

summary_file = args.summary
similarity_file = args.similarity
classes = args.classes

with open(summary_file, 'r', encoding='utf-8') as f:
    summary_data = json.load(f)

results = summary_data['results']

with open(similarity_file, 'r', encoding='utf-8') as f:
    similarity_data = json.load(f)

ratios = similarity_data['ratios']

step_size = 1 / classes
counter = 0
class_perf_d = dict()
while counter <= 1:
    class_perf_d[counter] = []
    counter += step_size

for sent_id, result in results.items():
    if sent_id not in ratios:
        # print(f'No similarity score for sentence {sent_id}')
        continue
    ratio = ratios[sent_id]
    v2_8, v2_11 = result['v2.8 ratio'], result['v2.11 ratio']
    diff = v2_11 - v2_8
    keys = list(class_perf_d.keys())
    for i, key in enumerate(keys):
        if ratio > key and ((i + 1 < len(keys) and ratio <= keys[i + 1]) or i + 1 == len(keys)):
            class_perf_d[key].append(diff)
            break

for key, value in class_perf_d.items():
    if len(value) == 0:
        continue
    mean_t = sum(value) / len(value)
    print(f'{key:.1f} - {mean_t:.2f}')