import argparse, json, os
from colorama import Fore, Style

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t8', '--treebank8', required=True, help='Path to treebank v2.8')
    parser.add_argument('-t11', '--treebank11', required=True, help='Path to treebank v2.11')
    parser.add_argument('-s', '--sent_ids', required=True, help='Path to the file containing the sentence ids')
    # parser.add_argument('-o', '--output', required=True, help='Path to the output file')
    return parser.parse_args()

def main():
    args = get_args()

    with open(args.treebank8, 'r') as f:
        treebank8 = json.load(f)
    
    with open(args.treebank11, 'r') as f:
        treebank11 = json.load(f)
    
    with open(args.sent_ids, 'r') as f:
        tokens = json.load(f)
    
    # selections = {}
    
    for sent_id in tokens:
        table8, table11 = treebank8[sent_id]['table'], treebank11[sent_id]['table']
        token_ids = tokens[sent_id]
        os.system('clear')
        print('Sentence ID: {}'.format(sent_id))
        print('Tokens: {}'.format(token_ids))
        lines8, lines11 = table8.split('\n'), table11.split('\n')
        if len(lines8) != len(lines11):
            print(sent_id)
        print('Table 8:')
        for line in table8.split('\n'):
            fields = line.split('\t')
            id_t = fields[0]
            if id_t in token_ids:
                print(Fore.RED + line + Style.RESET_ALL)
            else:
                print(line)
        print('Table 11:')
        for line in table11.split('\n'):
            fields = line.split('\t')
            id_t = fields[0]
            if id_t in token_ids:
                print(Fore.RED + line + Style.RESET_ALL)
            else:
                print(line)
        print()
        input()
        # selections[sent_id] = {}
        # for token_id in token_ids:
        #     while 1:
        #         version = input('Which version for token {}? (8/11) '.format(token_id))
        #         if version == '8':
        #             selections[sent_id][token_id] = 'v2.8'
        #         elif version == '11':
        #             selections[sent_id][token_id] = 'v2.11'
        #         elif version == 'b':
        #             selections[sent_id][token_id] = 'both'
        #         else:
        #             print('Invalid input. Try again.')
        #             continue

        #         break

    # with open(args.output, 'w') as f:
    #     json.dump(selections, f, indent=4)

if __name__ == '__main__':
    main()
