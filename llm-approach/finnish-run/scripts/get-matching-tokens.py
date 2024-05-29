import json

tokens1 = ['I', 'am', 'going', 'there', '.']
tokens2 = ['Hey', 'yo', 'I', 'am', 'going', 'not', 'there', '.']

def get_matches(tokens1, tokens2):
    idx1, idx2 = 0, 0
    match_count = 0
    matches = []
    while True:
        if idx1 >= len(tokens1) or idx2 >= len(tokens2):
            break
        if tokens1[idx1] == tokens2[idx2]:
            match_count += 1
            matches.append({
                'token': tokens1[idx1],
                'idx1': idx1,
                'idx2': idx2
            })
            idx1 += 1
            idx2 += 1
        else:
            idx2 += 1
    return match_count, matches

match_count, matches = get_matches(tokens1, tokens2)
print(match_count)
print(json.dumps(matches, indent=2))
