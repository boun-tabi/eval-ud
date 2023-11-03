import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--questions', type=str, required=True)
    args = parser.parse_args()

    filename = os.path.basename(args.questions)
    filename = os.path.splitext(filename)[0]

    with open(args.questions, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    template = questions['template']
    out_str = '# Template' + '\n\n' + template + '\n\n' + '-' * 50 + '\n\n'
    del questions['template']

    for sent_id in questions:
        sent = questions[sent_id]
        out_str += '# ' + sent_id + '\n'
        if 'v2_8_prompt' in sent:
            out_str += '\n## v2_8' + '\n\n'
            out_str += sent['v2_8_prompt'] + '\n'
        if 'v2_11_prompt' in sent:
            out_str += '\n## v2_11' + '\n\n'
            out_str += sent['v2_11_prompt'] + '\n'
        out_str += '\n' + '-' * 50 + '\n\n'
    
    with open(os.path.join(THIS_DIR, '{}_present.md'.format(filename)), 'w', encoding='utf-8') as f:
        f.write(out_str)
    
    print('Done!')

if __name__ == '__main__':
    main()