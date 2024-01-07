import argparse, csv, json

def get_args():
    parser = argparse.ArgumentParser(description='Get selected tokens from the LLM approach')
    parser.add_argument('--input', type=str, required=True, help='Input file')
    parser.add_argument('--output', type=str, required=True, help='Output file')
    args = parser.parse_args()
    return args

def main():
    args = get_args()

    word_count = 0
    with open(args.input, 'r', encoding='utf-8') as csv_reader:
        reader = csv.reader(csv_reader, delimiter=',')
        sent_id_index = 0
        words_index = 3
        selected_tokens = {}
        for row in reader:
            if row[0] == 'Sentence ID':
                continue
            sent_id = row[sent_id_index]
            words = row[words_index]
            if words == "":
                continue
            word_l = words.split(', ')
            word_count += len(word_l)
            selected_tokens[sent_id] = word_l
    
    print('Number of selected tokens:', word_count)
        
    with open(args.output, 'w', encoding='utf-8') as json_writer:
        json.dump(selected_tokens, json_writer, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
