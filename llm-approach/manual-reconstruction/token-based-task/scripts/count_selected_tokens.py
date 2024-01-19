import json, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tokens', type=str, required=True)
    args = parser.parse_args()

    with open(args.tokens, 'r') as f:
        tokens = json.load(f)
    
    count8, count11 = 0, 0
    for key in tokens:
        count8 += len(tokens[key]['v2.8'])
        count11 += len(tokens[key]['v2.11'])
    
    print('Total token count 8: {}'.format(count8))
    print('Total token count 11: {}'.format(count11))

if __name__ == '__main__':
    main()