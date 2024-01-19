import json, argparse, os
from colorama import Fore, Style

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb8', '--treebank8', type=str, required=True)
    parser.add_argument('-tb11', '--treebank11', type=str, required=True)
    parser.add_argument('-f', '--filter', type=str, required=True)
    args = parser.parse_args()

    with open(args.treebank8, 'r') as f:
        treebank8 = json.load(f)
    with open(args.treebank11, 'r') as f:
        treebank11 = json.load(f)
    with open(args.filter, 'r') as f:
        filtered_ids = json.load(f)

    id_l = list(treebank11.keys())

    for sent_id_t in id_l:
        if sent_id_t not in filtered_ids:
            continue
        table8, table11 = treebank8[sent_id_t]['table'], treebank11[sent_id_t]['table']
        has_conv, has_ptcp = False, False
        has_advcl, has_acl, has_ccomp = False, False, False
        token_ids = []
        for line in table11.split('\n'):
            fields = line.split('\t')
            id_t, feats_t, deprel_t = fields[0], fields[5], fields[7]
            feats_l = feats_t.split('|')
            for feat_t in feats_l:
                if feat_t == 'VerbForm=Conv':
                    token_ids.append(id_t)
                    has_conv = True
                elif feat_t == 'VerbForm=Part':
                    token_ids.append(id_t)
                    has_ptcp = True
            if deprel_t == 'advcl':
                token_ids.append(id_t)
                has_advcl = True
            elif deprel_t == 'acl':
                token_ids.append(id_t)
                has_acl = True
            elif deprel_t == 'ccomp':
                token_ids.append(id_t)
                has_ccomp = True
        if (has_conv or has_ptcp) and (has_advcl or has_acl or has_ccomp):
            os.system('clear')
            print('Sentence ID: {}'.format(sent_id_t))
            lines8, lines11 = table8.split('\n'), table11.split('\n')
            print('Table 8:')
            for line in lines8:
                fields = line.split('\t')
                id_t = fields[0]
                if id_t in token_ids:
                    print(Fore.RED + line + Style.RESET_ALL)
                else:
                    print(line)
            print('Table 11:')
            for line in lines11:
                fields = line.split('\t')
                id_t = fields[0]
                if id_t in token_ids:
                    print(Fore.RED + line + Style.RESET_ALL)
                else:
                    print(line)
            print()
            input()

if __name__ == '__main__':
    main()