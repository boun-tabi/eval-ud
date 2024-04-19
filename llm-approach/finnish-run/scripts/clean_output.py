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
    output_dir = output_path.parent

    with open(output_file, 'r', encoding='utf-8') as f:
        output = json.load(f)

    note_pattern = re.compile(r'\(Note: .+\)$')
    par_pattern = re.compile(r'(\(.+\))$')
    json_md_pattern = re.compile(r'^```json\n(.+)\n```$', re.DOTALL)
    json_pattern = re.compile(r'^{"original_form": "(.+)"}$')
    new_output_d = {}
    for el in output:
        sent_id, original_text, output_text = el['sent_id'], el['text'], el['output']
        json_md_search = json_md_pattern.search(output_text)
        if json_md_search:
            found_group = json_md_search.group(1)
            try:
                output_text = json.loads(found_group)['original_form']
            except:
                temp_text = found_group
                for _ in range(3):
                    temp_idx = temp_text.find('"')
                    temp_text = temp_text[temp_idx + 1:]
                temp_idx = temp_text.rfind('"')
                output_text = temp_text[:temp_idx]
        else:
            for nl in ['\n\n', '\n']:
                found_json = False
                if nl in output_text:
                    output_split = output_text.split(nl)
                    max_score, max_split = 0, None
                    for split_t in output_split:
                        json_search = json_pattern.search(split_t)
                        if json_search:
                            output_text = json_search.group(1)
                            found_json = True
                            break
                        split_t = split_t.strip()
                        score = fuzz.ratio(original_text, split_t)
                        if score > max_score:
                            max_score = score
                            max_split = split_t
                    if found_json:
                        break
                    output_text = max_split
                    break
            if not found_json:
                output_text = note_pattern.sub('', output_text).strip()
                par_search = par_pattern.search(output_text)
                if par_search:
                    text_t = par_search.group(1)
                    if fuzz.ratio(original_text, text_t) < 50:
                        output_text = par_pattern.sub('', output_text).strip()
        if original_text[0] != '"' and original_text[-1] != '"' and output_text[0] == '"' and output_text[-1] == '"':
            output_text = output_text[1:-1]
        new_output_d[sent_id] = {'original_text': original_text, 'output_text': output_text}

    with open(output_dir / (output_path.stem + '-cleaned.json'), 'w', encoding='utf-8') as f:
        json.dump(new_output_d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()