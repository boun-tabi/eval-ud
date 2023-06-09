import guidance, os, torch, argparse, json

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True, help='treebank file path')
args = parser.parse_args()

with open(args.treebank, 'r') as f:
    treebank = json.load(f)

first_table = treebank[0]['table']

# HOME_DIR = os.path.expanduser("~")
# llama_path = os.path.join(HOME_DIR, 'llama-weights', 'hf_weights') # couldn't generate for 40 mins
# llama_path = os.path.join(HOME_DIR, 'alpaca-replicated')

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

api_key = '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'
organization = 'org-5J2NmxwdP71FGU0iVV5Jd4SW'

model = 'text-davinci-003'
guidance.llm = guidance.llms.OpenAI(model, api_key=api_key, organization=organization)
print('Model:', model)

table_input = ''
table_l = first_table.split('\n')
for i, row in enumerate(table_l):
    fields = row.split('\t')
    id_t, form, lemma = fields[0], fields[1], fields[2]
    fields[1] = '{{gen ' + '\'' + id_t + '\'}}'
    table_l[i] = '\t'.join(fields)

input = """The following is an annotation of a Turkish sentence in CoNLL-U format.
{first_table}
""".format(first_table='\n'.join(table_l))
print('Input:\n', input)

program = guidance(input)
out = program()
print(out)
