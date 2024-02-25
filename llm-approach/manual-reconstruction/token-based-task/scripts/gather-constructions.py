import argparse, csv, json, re
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sheet-dir', type=str, required=True)
    parser.add_argument('-d', '--data', type=str, required=True)
    parser.add_argument('-t', '--type', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    sheet_dir = Path(args.sheet_dir)
    task_type = args.type

    data_path = Path(args.data)
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if task_type == 'token with dep':
        sent_l = data['dep']
    else:
        sent_l = data['normal']
    sent_ids = {sent['sent_id'] for sent in sent_l}

    md_path = sheet_dir / 'meta.json'
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    relevant_keys = [k for k, v in md.items() if v['type'] == task_type]
    people = {v['person'] for k, v in md.items() if k in relevant_keys}
    versions = {v['version'] for k, v in md.items() if k in relevant_keys}
    task_names = [v['task_name'] for k, v in md.items() if k in relevant_keys]

    task_id_pattern = re.compile('^(\d+) - (.*) - .*$')

    constructions = {person: {version: {sent_id: {} for sent_id in sent_ids} for version in versions} for person in people}
    for sheet in sheet_dir.iterdir():
        if sheet.suffix != '.csv':
            continue
        sheet_name = sheet.stem
        task_id_match = task_id_pattern.match(sheet_name)
        if not task_id_match:
            continue
        task_number = task_id_match.group(1)
        person, version = md[task_number]['person'], md[task_number]['version']
        sheet_name = task_id_match.group(2)
        if sheet_name in task_names:
            with open(sheet, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    surface_form = row['Surface Form']
                    if version == 'v2.8':
                        real_token_id = sent_l[i]['id8']
                    elif version == 'v2.11':
                        real_token_id = sent_l[i]['id11']
                    sent_id = sent_l[i]['sent_id']
                    constructions[person][version][sent_id][real_token_id] = surface_form
    with open(sheet_dir / f'{args.type}.json', 'w', encoding='utf-8') as f:
        json.dump(constructions, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()