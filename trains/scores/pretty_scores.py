import json
with open('scores.json', 'r') as f:
    scores = json.load(f)
with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=4, sort_keys=True)