import json, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tokens', type=str, required=True)
    args = parser.parse_args()

    with open(args.tokens, 'r') as f:
        tokens = json.load(f)
    
    count = 0
    for key in tokens:
        count += len(tokens[key]['v2.8'])
    
    print('Total token count: {}'.format(count))

if __name__ == '__main__':
    main()