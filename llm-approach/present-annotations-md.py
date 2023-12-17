import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sent-ids', type=str, required=True)
    parser.add_argument('-tb8', '--treebank-8', type=str, required=True)
    parser.add_argument('-tb11', '--treebank-11', type=str, required=True)
    args = parser.parse_args()

    filename = os.path.basename(args.sent_ids)
    filename = os.path.splitext(filename)[0]

    with open(args.sent_ids, 'r', encoding='utf-8') as f:
        sent_ids = json.load(f)
    
    with open(args.treebank_8, 'r', encoding='utf-8') as f:
        treebank_data_8 = json.load(f)
    
    with open(args.treebank_11, 'r', encoding='utf-8') as f:
        treebank_data_11 = json.load(f)

    md_table_str = ''

    for sent_id in sent_ids:
        md_table_str += '# ' + sent_id + '\n'
        md_table_str += '\n## v2_8' + '\n\n'
        md_table_str += '| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC |' + '\n'
        md_table_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |' + '\n'
        table = treebank_data_8[sent_id]['table']
        for row in table.split('\n'):
            fields = row.split('\t')
            fields[5] = fields[5].replace('|', '\|')
            md_table_str += '| ' + ' | '.join(fields) + ' |' + '\n'
        md_table_str += '\n'
        md_table_str += '\n## v2_11' + '\n\n'
        md_table_str += '| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC |' + '\n'
        md_table_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |' + '\n'
        table = treebank_data_11[sent_id]['table']
        for row in table.split('\n'):
            fields = row.split('\t')
            fields[5] = fields[5].replace('|', '\|')
            md_table_str += '| ' + ' | '.join(fields) + ' |' + '\n'
        md_table_str += '\n'
    md_table_str += '\n' + '-' * 50 + '\n\n'
    
    with open(os.path.join(THIS_DIR, '{}_present_annotations.md'.format(filename)), 'w', encoding='utf-8') as f:
        f.write(md_table_str)
    
    print('Done!')

if __name__ == '__main__':
    main()