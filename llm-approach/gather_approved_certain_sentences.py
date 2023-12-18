import csv, argparse, json, os

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)
args = parser.parse_args()

with open(args.input, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
sent_id_col = header.index('Sentence ID')
approved_col = header.index('OK?')
approved_sent_ids = []
for row in rows:
    if row[approved_col] == 'yes':
        approved_sent_ids.append(row[sent_id_col])

print(approved_sent_ids)
print(len(approved_sent_ids))

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

output_path = os.path.join(THIS_DIR, 'approved_sent_ids-conv-ptcp-advcl-acl-ccomp.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(approved_sent_ids, f, indent=2)
