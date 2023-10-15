import os, json, argparse, random

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--sent-ids', type=str, required=True)
    parser.add_argument('-n', '--num_sentences', type=int, required=True)
    parser.add_argument('-s', '--seed', type=int, default=42)
    args = parser.parse_args()

    sent_ids_path = args.sent_ids
    num_sentences = args.num_sentences
    seed = args.seed

    random.seed(seed)

    with open(sent_ids_path, 'r') as f:
        sent_ids = json.load(f)
    
    selected_sent_ids = random.sample(sent_ids, num_sentences)
    random.shuffle(selected_sent_ids)

    with open(os.path.join(THIS_DIR, 'selected_sents.json'), 'w') as f:
        json.dump(selected_sent_ids, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()