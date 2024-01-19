import argparse, json, os, random

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tokens', required=True, help='Path to the file containing the tokens')
    return parser.parse_args()

def main():
    args = get_args()

    with open(args.tokens, 'r') as f:
        tokens = json.load(f)
    
    normal_l, dep_l = [], []

    token_l = []
    for sent_id in tokens.keys():
        t8, t11 = tokens[sent_id]['v2.8'], tokens[sent_id]['v2.11']
        for t8_t, t11_t in zip(t8, t11):
            token_l.append({'sent_id': sent_id, 'id8': t8_t, 'id11': t11_t})
    random.shuffle(token_l)
    for i, token in enumerate(token_l):
        if i % 2 == 0:
            normal_l.append(token)
        else:
            dep_l.append(token)
    print('Normal:', len(normal_l))
    print('Dep:', len(dep_l))

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'divided-sents-token-task.json'), 'w') as f:
        json.dump({'normal': normal_l, 'dep': dep_l}, f, indent=4)

if __name__ == '__main__':
    main()