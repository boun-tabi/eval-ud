from pathlib import Path
import argparse, json, re
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

    note_pattern = re.compile(r'\(Note: .+\)$')
    par_pattern = re.compile(r'(\(.+\))$')

    new_output_d = {}
    for el in output:
        sent_id, original_text, output_text = el['sent_id'], el['text'], el['output']
        for nl in ['\n\n', '\n']:
            if nl in output_text:
                output_split = output_text.split(nl)
                max_score, max_split = 0, None
                for split_t in output_split:
                    split_t = split_t.strip()
                    score = fuzz.ratio(original_text, split_t)
                    if score > max_score:
                        max_score = score
                        max_split = split_t
                output_text = max_split
                break
        output_text = note_pattern.sub('', output_text).strip()
        par_search = par_pattern.search(output_text)
        if par_search:
            text_t = par_search.group(1)
            if fuzz.ratio(original_text, text_t) < 50:
                output_text = par_pattern.sub('', output_text).strip()
        new_output_d[sent_id] = {'original_text': original_text, 'output_text': output_text}

    with open(output_dir / (output_filename_without_extension + '-cleaned.json'), 'w', encoding='utf-8') as f:
        json.dump(new_output_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()