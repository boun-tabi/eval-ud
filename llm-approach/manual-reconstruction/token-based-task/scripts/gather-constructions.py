import argparse, csv, json, re
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sheet-dir', type=str, required=True)
    parser.add_argument('-d', '--data', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-ld', '--last-data', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    return parser.parse_args()

lower_d = {
    'I': 'ı',
    'İ': 'i',
    'Ğ': 'ğ',
    'Ü': 'ü',
    'Ş': 'ş',
    'Ö': 'ö',
    'Ç': 'ç'
}

def lower(s):
    for k, v in lower_d.items():
        s = s.replace(k, v)
    return s.lower()

def get_form(sent_id, token_id, version, tbs):
    if version == 'v1':
        table = tbs['v1'][sent_id]['table']
    elif version == 'v2':
        table = tbs['v2'][sent_id]['table']
    for line in table.split('\n'):
        fields = line.split('\t')
        if fields[0] == str(token_id):
            form = fields[1]
            break
    return lower(form)

def main():
    args = get_args()
    v1, v2 = Path(args.version1), Path(args.version2)
    with v1.open('r', encoding='utf-8') as f:
        v1_data = json.load(f)
    with v2.open('r', encoding='utf-8') as f:
        v2_data = json.load(f)
    tbs = {'v1': v1_data, 'v2': v2_data}
    sheet_dir = Path(args.sheet_dir)

    data_path = Path(args.data)
    with data_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    sent_l = {type_t: data[type_t] for type_t in ['dep', 'normal']}

    meta_path = sheet_dir / 'meta.json'
    with meta_path.open('r', encoding='utf-8') as f:
        meta = json.load(f)
    relevant_keys = [k for k, v in meta.items() if 7 <= int(k) <= 14]
    task_names = [v['task_name'] for k, v in meta.items() if k in relevant_keys]

    task_id_pattern = re.compile('^(\d+) - (.*) - .*$')

    constructions = {type_t: [] for type_t in ['easy', 'medium', 'random', 'difficult']}
    for sheet in sheet_dir.iterdir():
        if sheet.suffix != '.csv':
            continue
        sheet_name = sheet.stem
        task_id_match = task_id_pattern.match(sheet_name)
        if not task_id_match:
            continue
        task_number = task_id_match.group(1)
        task_id = int(task_number)
        if task_id < 11:
            type_t = 'normal'
        else:
            type_t = 'dep'
        person, version = meta[task_number]['person'], meta[task_number]['version']
        sheet_name = task_id_match.group(2)
        if sheet_name in task_names:
            with sheet.open(encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    keys = row.keys()
                    form_keys = [k for k in keys if 'Surface Form' in k]
                    form_values = [row[k].strip() for k in form_keys if row[k].strip()]
                    if version == 'v2.8':
                        real_token_id = sent_l[type_t][i]['id8']
                    elif version == 'v2.11':
                        real_token_id = sent_l[type_t][i]['id11']
                    sent_id = sent_l[type_t][i]['sent_id']
                    constructions['difficult'].append({'sent_id': sent_id, 'token_id': real_token_id, 'forms': form_values, 'annotator': person, 'version': 'v1' if version == 'v2.8' else 'v2' if version == 'v2.11' else version, 'type': type_t})

    llm_dir = Path(args.llm_dir)
    difficult_dirs = [d for d in llm_dir.iterdir() if d.is_dir() and 'poe_GPT-4-2024-02-25_' in d.name]
    for d in difficult_dirs:
        md_file = d / 'md.json'
        with md_file.open(encoding='utf-8') as f:
            md = json.load(f)
        if md['dep']:
            v1_output_file, v2_output_file = d / 'v2.8_output_dep.json', d / 'v2.11_output_dep.json'
        else:
            v1_output_file, v2_output_file = d / 'v2.8_output.json', d / 'v2.11_output.json'
        with v1_output_file.open(encoding='utf-8') as f:
            v1_output = json.load(f)
        for el in v1_output:
            sent_id, token_id, output = el['sent_id'], el['token_id'], el['output']
            constructions['difficult'].append({'sent_id': sent_id, 'token_id': token_id, 'forms': [output], 'annotator': 'GPT-4', 'version': 'v1', 'type': 'dep'})
        with v2_output_file.open(encoding='utf-8') as f:
            v2_output = json.load(f)
        for el in v2_output:
            sent_id, token_id, output = el['sent_id'], el['token_id'], el['output']
            constructions['difficult'].append({'sent_id': sent_id, 'token_id': token_id, 'forms': [output], 'annotator': 'GPT-4', 'version': 'v2', 'type': 'dep'})

    relevant_keys = [k for k in meta.keys() if 15 <= int(k) <= 18]
    task_names = [v['task_name'] for k, v in meta.items() if k in relevant_keys]
    people = [v['person'] for k, v in meta.items() if k in relevant_keys]
    versions = [v['version'] for k, v in meta.items() if k in relevant_keys]
    last_manual_d = {p: {v: [] for v in versions} for p in people}
    for sheet in sheet_dir.iterdir():
        if sheet.suffix != '.csv':
            continue
        sheet_name = sheet.stem
        task_id_match = task_id_pattern.match(sheet_name)
        if not task_id_match:
            continue
        task_number = task_id_match.group(1)
        task_id = int(task_number)
        person, version = meta[task_number]['person'], meta[task_number]['version']
        sheet_name = task_id_match.group(2)
        if sheet_name in task_names or sheet_name.replace('.xlsx', '') in task_names:
            with sheet.open(encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    keys = row.keys()
                    form_keys = [k for k in keys if k == 'Form']
                    form_values = [row[k].strip() for k in form_keys if row[k].strip()]
                    reconstruction = form_values[0]
                    last_manual_d[person][version].append(reconstruction)
    
    last_data_path = Path(args.last_data)
    with last_data_path.open('r', encoding='utf-8') as f:
        last_data = json.load(f)
    easy_l, medium_l, random_l = [], [], []
    for el in last_data:
        sent_id, v1, v2, difficulty, is_dep = el['sent_id'], el['v1'], el['v2'], el['difficulty'], el['is_dep']
        v1_order, v2_order = v1['order'], v2['order']
        v1_id, v2_id = v1['id'], v2['id']
        if difficulty == 'easy':
            easy_l.append((sent_id, v1_id))
            easy_l.append((sent_id, v2_id))
        elif difficulty == 'medium':
            medium_l.append((sent_id, v1_id))
            medium_l.append((sent_id, v2_id))
        elif difficulty == 'random':
            random_l.append((sent_id, v1_id))
            random_l.append((sent_id, v2_id))
        for person in people:
            for version in versions:
                if version == 'v2.8':
                    reconstruction = last_manual_d[person][version][v1_order-1]
                elif version == 'v2.11':
                    if len(last_manual_d[person][version]) == 0:
                        continue
                    reconstruction = last_manual_d[person][version][v2_order-1]
                constructions[difficulty].append({'sent_id': sent_id, 'forms': [reconstruction], 'annotator': person, 'version': 'v1' if version == 'v2.8' else 'v2' if version == 'v2.11' else version, 'type': 'dep' if is_dep else 'normal', 'token_id': v1_id if version == 'v2.8' else v2_id})
    
    other_dirs = [d for d in llm_dir.iterdir() if d.is_dir() and 'poe_GPT-4-2024-04-23_' in d.name]
    for d in other_dirs:
        v1_output_file, v2_output_file = d / 'v2.8_output.json', d / 'v2.11_output.json'
        with v1_output_file.open(encoding='utf-8') as f:
            v1_output = json.load(f)
        for el in v1_output:
            sent_id, token_id, output = el['sent_id'], el['token_id'], el['output']
            for type_t in ['easy', 'medium', 'random']:
                if (sent_id, token_id) in locals()[f'{type_t}_l']:
                    constructions[type_t].append({'sent_id': sent_id, 'token_id': token_id, 'forms': [output], 'annotator': 'GPT-4', 'version': 'v1', 'type': 'dep'})
        with v2_output_file.open(encoding='utf-8') as f:
            v2_output = json.load(f)
        for el in v2_output:
            sent_id, token_id, output = el['sent_id'], el['token_id'], el['output']
            for type_t in ['easy', 'medium', 'random']:
                if (sent_id, token_id) in locals()[f'{type_t}_l']:
                    constructions[type_t].append({'sent_id': sent_id, 'token_id': token_id, 'forms': [output], 'annotator': 'GPT-4', 'version': 'v2', 'type': 'dep'})

    for type_t in ['easy', 'medium', 'random', 'difficult']:
        d = {}
        for el in constructions[type_t]:
            sent_id = el['sent_id']
            if sent_id not in d:
                d[sent_id] = {}
            version = el['version']
            if version not in d[sent_id]:
                d[sent_id][version] = {}
            token_id = el['token_id']
            form = get_form(sent_id, token_id, version, tbs)
            if token_id not in d[sent_id][version]:
                has_dep = el['type']
                d[sent_id][version][token_id] = {'form': form, 'annotators': {}, 'type': 'dep' if has_dep == 'dep' else 'normal'}
            annotator = el['annotator']
            d[sent_id][version][token_id]['annotators'][annotator] = lower(el['forms'][0])
        constructions[type_t] = d

    constructions_file = sheet_dir / 'constructions.json'
    with constructions_file.open('w', encoding='utf-8') as f:
        json.dump(constructions, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()