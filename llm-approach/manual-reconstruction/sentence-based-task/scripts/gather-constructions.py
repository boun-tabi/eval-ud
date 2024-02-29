import argparse, csv, json, re
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sheet-dir', type=str, required=True)
    parser.add_argument('-t', '--type', type=str, required=True)
    parser.add_argument('-o', '--order', type=str)
    return parser.parse_args()

def main():
    args = get_args()
    order = args.order
    sheet_dir = Path(args.sheet_dir)
    task_type = args.type
    md_path = sheet_dir / 'meta.json'
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    relevant_keys = [k for k, v in md.items() if v['type'] == task_type]
    people = {v['person'] for k, v in md.items() if k in relevant_keys}
    versions = {v['version'] for k, v in md.items() if k in relevant_keys if order is None or v['order'] == int(order)}
    task_names = [v['task_name'] for k, v in md.items() if k in relevant_keys]

    task_id_pattern = re.compile('^(\d+) - (.*) - .*$')

    constructions = {person: {version: {} for version in versions} for person in people}
    for sheet in sheet_dir.iterdir():
        if sheet.suffix != '.csv':
            continue
        sheet_name = sheet.stem
        task_id_match = task_id_pattern.match(sheet_name)
        if not task_id_match:
            continue
        task_number = task_id_match.group(1)
        if order:
            if not 'order' in md[task_number]:
                continue
            order_t = md[task_number]['order']
            if order_t != int(order):
                continue
        person, version = md[task_number]['person'], md[task_number]['version']
        sheet_name = task_id_match.group(2)
        if sheet_name in task_names:
            if order == '1':
                with open(sheet, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    to_add = False
                    new_versions = set()
                    for row in reader:
                        version_t = row['Version']
                        if version_t not in versions:
                            to_add = True
                        new_versions.add(version_t)
                    if to_add:
                        constructions = {person: {version: {} for version in new_versions} for person in people}
                        versions = new_versions
            with open(sheet, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sent_id, text = row['Sentence ID'], row['Text']
                    if order == '1':
                        version = row['Version']
                    constructions[person][version][sent_id] = text
    with open(sheet_dir / f'{args.type}-{args.order}.json', 'w', encoding='utf-8') as f:
        json.dump(constructions, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()