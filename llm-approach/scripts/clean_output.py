from pathlib import Path
import argparse, json
from rapidfuzz import fuzz

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-file', type=str)
    return parser.parse_args()

def main():
    args = get_args()
    output_file = args.output_file
    output_path = Path(output_file)
    output_filename_without_extension = output_path.stem
    output_dir = output_path.parent

    with open(output_file, 'r', encoding='utf-8') as f:
        output = json.load(f)
    
    new_output_d = {}
    for el in output:
        sent_id, original_text, output_text = el['sent_id'], el['text'], el['output']
        if '\n\n' not in output_text:
            score = fuzz.ratio(original_text, output_text)
            if score < 50:
                output_text = None
            new_output_d[sent_id] = {'original_text': original_text, 'output_text': output_text}
        else:
            output_split = output_text.split('\n\n')
            max_score, max_split = 0, None
            for split_t in output_split:
                score = fuzz.ratio(original_text, split_t)
                if score > max_score:
                    max_score = score
                    max_split = split_t
            output_text = max_split
            if max_score < 50:
                output_text = None
            new_output_d[sent_id] = {'original_text': original_text, 'output_text': output_text}
    
    with open(output_dir / (output_filename_without_extension + '-cleaned.json'), 'w', encoding='utf-8') as f:
        json.dump(new_output_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()