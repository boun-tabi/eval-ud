import json, argparse, random
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str, required=True)
    parser.add_argument('-n', '--num_sentences', type=int, required=True)
    parser.add_argument('-s', '--seed', type=int, default=42)
    parser.add_argument('-o', '--output-dir', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()

    tb_path = Path(args.treebank)
    num_sentences = args.num_sentences
    seed = args.seed

    random.seed(seed)

    with open(tb_path, 'r') as f:
        tb = json.load(f)
    sent_ids = list(tb.keys())
    selected_sent_ids = random.sample(sent_ids, num_sentences)
    random.shuffle(selected_sent_ids)

    output_dir = Path(args.output_dir)

    with open(output_dir / 'selected_sents.json', 'w') as f:
        json.dump(selected_sent_ids, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()