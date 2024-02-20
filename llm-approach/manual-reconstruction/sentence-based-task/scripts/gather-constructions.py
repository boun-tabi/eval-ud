import argparse, csv, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sheet-dir', type=str, required=True)
    parser.add_argument('-t', '--type', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    sheet_dir = Path(args.sheet_dir)
    task_type = args.type
    md_path = sheet_dir / 'meta.json'
    with open(md_path, 'r', encoding='utf-8') as f:
        md = json.load(f)
    relevant_keys = [k for k, v in md.items() if v['type'] == task_type]
    people = {v['person'] for k, v in md.items() if k in relevant_keys}
    versions = {v['version'] for k, v in md.items() if k in relevant_keys}
    task_names = [v['task_name'] for k, v in md.items() if k in relevant_keys]

    constructions = {person: {version: [] for version in versions} for person in people}
    for sheet in sheet_dir.iterdir():
        if sheet.suffix == '.csv' and sheet.stem in task_names:
            with open(sheet, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(row)
                    input()


if __name__ == '__main__':
    main()