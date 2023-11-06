import os, json, argparse, csv

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--questions', type=str, required=True)
    args = parser.parse_args()

    filename = os.path.basename(args.questions)
    filename = os.path.splitext(filename)[0]

    with open(args.questions, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    csv_l = []
    answer_l = []
    answer_sheet_l = []
    header = ['sent_id', 'id', 'tb']
    answer_header = ['sent_id', 'tb', 'text']
    answer_sheet_header = ['sent_id', 'tb', 'text', 'original text', 'v2.8 text', 'v2.11 text']
    for sent_id in questions:
        sent = questions[sent_id]
        for v in ['v2.8', 'v2.11']:
            v_underscore = v.replace('.', '_')
            if '{}_prompt'.format(v_underscore) in sent:
                prompt = sent['{}_prompt'.format(v_underscore)]
                key_l = list(prompt.keys())
                curr_id = 1
                while str(curr_id) in key_l:
                    d = {'sent_id': sent_id, 'id': curr_id, 'tb': v}
                    if '{}-{}'.format(curr_id, curr_id + 1) in key_l:
                        d_copy = d.copy()
                        d_copy['id'] = '{}-{}'.format(curr_id, curr_id + 1)
                        csv_l.append(d_copy)
                    row_d = prompt.get(str(curr_id))
                    for key in row_d:
                        if key not in header:
                            header.append(key)
                        d[key] = row_d[key]
                    csv_l.append(d)
                    curr_id += 1
                answer_l.append({'sent_id': sent_id, 'tb': v, 'text': ''})
                answer_sheet_l.append({'sent_id': sent_id, 'tb': v, 'text': '', 'original text': sent['original_text'], 'v2.8 text': sent['v2_8_text'], 'v2.11 text': sent['v2_11_text']})

    with open(os.path.join(THIS_DIR, '{}_answer.csv'.format(filename)), 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=answer_header)
        writer.writeheader()
        for d in answer_l:
            writer.writerow(d)

    with open(os.path.join(THIS_DIR, '{}.csv'.format(filename)), 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for d in csv_l:
            writer.writerow(d)
    
    with open(os.path.join(THIS_DIR, '{}_answer_sheet.csv'.format(filename)), 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=answer_sheet_header, delimiter='\t')
        writer.writeheader()
        for d in answer_sheet_l:
            writer.writerow(d)

if __name__ == '__main__':
    main()