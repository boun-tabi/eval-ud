import os, json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
diff_path = os.path.join(THIS_DIR, 'different_annotations.json')
with open(diff_path, 'r') as f:
    diff = json.load(f)
diff_accumulation = 0
for sent_id, diff_int in diff.items():
    diff_accumulation += diff_int
print(diff_accumulation / len(diff))
# 474.80770412867537 on 8/8/2023 22:16