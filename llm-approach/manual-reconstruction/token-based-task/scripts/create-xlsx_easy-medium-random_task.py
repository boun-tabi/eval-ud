import argparse, json, random, xlsxwriter
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-td1', '--token-dir1', type=str, required=True)
    parser.add_argument('-td2', '--token-dir2', type=str, required=True)
    parser.add_argument('-td3', '--token-dir3', type=str, required=True)
    parser.add_argument('-a', '--all-tokens', type=str)
    return parser.parse_args()

def main():
    args = get_args()
    token_dir1, token_dir2, token_dir3 = Path(args.token_dir1), Path(args.token_dir2), Path(args.token_dir3)
    data_dir = token_dir1.parent

    if args.all_tokens:
        all_tokens = Path(args.all_tokens)
        with all_tokens.open('r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []
        v1_orders, v2_orders = list(range(1, 151)), list(range(1, 151))
        random.shuffle(v1_orders)
        random.shuffle(v2_orders)
        for token_dir in [token_dir1, token_dir2, token_dir3]:
            for token_file in token_dir.iterdir():
                is_dep = 'dep' in token_file.stem
                with token_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                for d in data:
                    d['v1']['order'] = v1_orders.pop()
                    d['v2']['order'] = v2_orders.pop()
                    d['difficulty'] = token_dir.name
                    d['is_dep'] = is_dep
                all_data.extend(data)

        random.shuffle(all_data)
        output_path = data_dir / 'all-tokens_easy-medium-random.json'
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)

    v1_xlsx = data_dir / 'v1-easy-medium-random.xlsx'
    v2_xlsx = data_dir / 'v2-easy-medium-random.xlsx'

    for file in [v1_xlsx, v2_xlsx]:
        workbook = xlsxwriter.Workbook(file)
        bold = workbook.add_format({'bold': True})
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'ID', bold)
        worksheet.write(0, 1, 'Form', bold)
        worksheet.write(0, 2, 'Lemma', bold)
        worksheet.write(0, 3, 'POS', bold)
        worksheet.write(0, 4, 'Features', bold)
        worksheet.write(0, 5, 'Head', bold)
        worksheet.write(0, 6, 'Deprel', bold)

        all_data.sort(key=lambda x: x['v1']['order'] if file == v1_xlsx else x['v2']['order'])
        for i, d in enumerate(all_data):
            if file == v1_xlsx:
                el = d['v1']
            else:
                el = d['v2']
            worksheet.write(i+1, 0, el['order'])
            worksheet.write(i+1, 1, '')
            worksheet.write(i+1, 2, el['lemma'])
            worksheet.write(i+1, 3, el['upos'])
            feats_str = '|'.join([feat for feat in el['feats'] if feat])
            worksheet.write(i+1, 4, feats_str)
            if 'is_dep' in d and d['is_dep']:
                worksheet.write(i+1, 5, el['head'])
                worksheet.write(i+1, 6, el['deprel'])
        
        worksheet.autofit()
        worksheet.set_column(1, 1, 30)
        
        workbook.close()

if __name__ == '__main__':
    main()
