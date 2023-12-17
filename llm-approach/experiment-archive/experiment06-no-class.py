import os, json, argparse, random, logging
from datetime import datetime

now = datetime.now().strftime('%Y%m%d%H%M%S')

logger = logging.getLogger(__name__)
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'experiment06.log'), format='%(asctime)s %(levelname)s %(name)s %(message)s')

logger.info('Started at {now}'.format(now=now))

template="""The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech and morphological features given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

The sentence has 7 tokens.

1st token's lemma is "meşrutiyet", its part of speech is proper noun, its case is genitive, its number is singular number, and its person is third person.
2nd token's lemma is "ilan", its part of speech is noun, its person is third person, its number is singular number, its possessor's person is third person, its possessor's number is singular number, and its case is ablative.
3rd token's lemma is "önceki", and its part of speech is adjective.
4th token's lemma is "siyasi", and its part of speech is adjective.
5th token's lemma is "faaliyet", its part of speech is noun, its person is third person, its number is plural number, and its case is dative.
6th token's lemma is "kat", its part of speech is verb, its voice is reflexive voice, its polarity is positive, its tense is past tense, its aspect is perfect aspect, its person is third person, its number is singular number, and its evidentiality is first hand.
7th token's lemma is ".", and its part of speech is punctuation.

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

"Meşrutiyetin ilanından önceki siyasi faaliyetlere katıldı."

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

script_path = os.path.abspath(__file__)
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()
THIS_DIR = os.path.dirname(script_path)

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'tr-ud-docs')
with open(os.path.join(data_dir, 'feat.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'pos.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)
sent_ids = []

parser = argparse.ArgumentParser()
parser.add_argument('-t8', '--treebank-2-8', type=str, required=True)
parser.add_argument('-t11', '--treebank-2-11', type=str, required=True)
parser.add_argument('-r', '--run-dir', type=str)
parser.add_argument('-s', '--sentence-count', type=int)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('-m', '--model', type=str, default='openai')
parser.add_argument('-f', '--filter', type=str)
args = parser.parse_args()

random.seed(args.seed)

model = args.model
if model == 'openai':
    print('Using OpenAI API.')
    import openai
    with open(os.path.join(THIS_DIR, 'openai.json')) as f:
        openai_d = json.load(f)
    openai.api_key = openai_d['key']
elif model == 'llama-replicate':
    print('Using LLAMA API.')
    import replicate
    with open(os.path.join(THIS_DIR, 'replicate.json')) as f:
        token = json.load(f)['token']
    os.environ['REPLICATE_API_TOKEN'] = token
elif model == 'llama-hf':
    from transformers import AutoTokenizer
    import transformers
    import torch

    model = "meta-llama/Llama-2-7b-chat-hf"

    tokenizer = AutoTokenizer.from_pretrained(model)
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        torch_dtype=torch.float16,
        device_map="auto",
    )

t8 = args.treebank_2_8
v2_8 = '_'.join(os.path.dirname(t8).split('/')[-2:])
t11 = args.treebank_2_11
v2_11 = '_'.join(os.path.dirname(t11).split('/')[-2:])

to_filter = False
if args.filter:
    to_filter = True
    with open(args.filter, 'r', encoding='utf-8') as f:
        filtered_sent_ids = json.load(f)

with open(t8, 'r', encoding='utf-8') as f:
    t8_data = json.load(f)
with open(t11, 'r', encoding='utf-8') as f:
    t11_data = json.load(f)
table1_d, table2_d = {}, {}
for example in t8_data:
    sent_id, text, table = example['sent_id'], example['text'], example['table']
    if to_filter and sent_id in filtered_sent_ids:
        table1_d[sent_id] = {'table': table, 'text': text}
    elif not to_filter:
        table1_d[sent_id] = {'table': table, 'text': text}
if to_filter:
    all_sent_ids = list(filtered_sent_ids)
else:
    all_sent_ids = list(table1_d.keys())
for example in t11_data:
    sent_id, text, table = example['sent_id'], example['text'], example['table']
    if to_filter and sent_id in filtered_sent_ids:
        table2_d[sent_id] = {'table': table, 'text': text}
    elif not to_filter:
        table2_d[sent_id] = {'table': table, 'text': text}

output_dir = os.path.join(THIS_DIR, 'experiment_outputs')
exp6_dir = os.path.join(output_dir, 'experiment06-no-class')
if args.run_dir is not None:
    print('Using run directory {run_dir}'.format(run_dir=args.run_dir))
    run_dir = os.path.join(exp6_dir, args.run_dir)
    with open(os.path.join(run_dir, 'md.json'), 'r', encoding='utf-8') as f:
        md = json.load(f)
    sentence_count = md['sentence_count']
    sent_ids = md['sent_ids']
else:
    run_dir = os.path.join(exp6_dir, now)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, 'script.py'), 'w', encoding='utf-8') as f:
        f.write(script_content)
    if args.sentence_count is None:
        print('Please specify the number of sentences to ask.')
        exit()
    sentence_count = args.sentence_count
    sent_ids = random.sample(all_sent_ids, sentence_count)
    with open(os.path.join(run_dir, 'md.json'), 'w', encoding='utf-8') as f:
        md = {'sentence_count': args.sentence_count, 'sent_ids': sent_ids, 'model': model, 'seed': args.seed, 'now': now, 'run_dir': run_dir, 'prompt': template}
        json.dump(md, f, ensure_ascii=False, indent=2)

number_d = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th',
            11: '11th', 12: '12th', 13: '13th', 14: '14th', 15: '15th', 16: '16th', 17: '17th', 18: '18th', 19: '19th',
            20: '20th', 21: '21st', 22: '22nd', 23: '23rd', 24: '24th', 25: '25th', 26: '26th', 27: '27th', 28: '28th',
            29: '29th', 30: '30th', 31: '31st', 32: '32nd', 33: '33rd', 34: '34th', 35: '35th', 36: '36th', 37: '37th'
            , 38: '38th', 39: '39th', 40: '40th', 41: '41st', 42: '42nd', 43: '43rd', 44: '44th', 45: '45th', 46: '46th',
            47: '47th', 48: '48th', 49: '49th', 50: '50th', 51: '51st', 52: '52nd', 53: '53rd', 54: '54th', 55: '55th',
            56: '56th', 57: '57th', 58: '58th', 59: '59th', 60: '60th', 61: '61st', 62: '62nd', 63: '63rd', 64: '64th',
            65: '65th', 66: '66th', 67: '67th', 68: '68th', 69: '69th', 70: '70th', 71: '71st', 72: '72nd', 73: '73rd',
            74: '74th', 75: '75th', 76: '76th', 77: '77th', 78: '78th', 79: '79th', 80: '80th', 81: '81st', 82: '82nd',
            83: '83rd', 84: '84th', 85: '85th', 86: '86th', 87: '87th', 88: '88th', 89: '89th', 90: '90th', 91: '91st',
            92: '92nd', 93: '93rd', 94: '94th', 95: '95th', 96: '96th', 97: '97th', 98: '98th', 99: '99th', 100: '100th',
            101: '101st', 102: '102nd', 103: '103rd', 104: '104th', 105: '105th', 106: '106th', 107: '107th', 108: '108th',
            109: '109th', 110: '110th', 111: '111th', 112: '112th', 113: '113th', 114: '114th', 115: '115th', 116: '116th',
            117: '117th', 118: '118th', 119: '119th', 120: '120th', 121: '121st', 122: '122nd', 123: '123rd', 124: '124th',
            125: '125th', 126: '126th', 127: '127th', 128: '128th', 129: '129th', 130: '130th', 131: '131st', 132: '132nd',
            133: '133rd', 134: '134th', 135: '135th', 136: '136th', 137: '137th', 138: '138th', 139: '139th', 140: '140th',
            141: '141st', 142: '142nd', 143: '143rd', 144: '144th', 145: '145th', 146: '146th', 147: '147th', 148: '148th',
            149: '149th', 150: '150th', 151: '151st', 152: '152nd', 153: '153rd', 154: '154th', 155: '155th', 156: '156th'}
v2_8_out, v2_11_out = os.path.join(run_dir, 'v2.8_output.json'), os.path.join(run_dir, 'v2.11_output.json')
if os.path.exists(v2_8_out):
    with open(v2_8_out, 'r', encoding='utf-8') as f:
        v2_8_output = json.load(f)
else:
    v2_8_output = []
v2_8_done_sent_ids = [el['sent_id'] for el in v2_8_output]
if os.path.exists(v2_11_out):
    with open(v2_11_out, 'r', encoding='utf-8') as f:
        v2_11_output = json.load(f)
else:
    v2_11_output = []
v2_11_done_sent_ids = [el['sent_id'] for el in v2_11_output]
noun_order = ['Person', 'Number', 'Person[psor]', 'Number[psor]', 'Case']
verb_order = ['Voice', 'Mood','Polarity', 'Tense', 'Aspect', 'Person', 'Number']
for run in [v2_8, v2_11]:
    print(run)
    asked_count = 0
    if run == v2_8:
        output_l = v2_8_output
    elif run == v2_11:
        output_l = v2_11_output
    for i, sent_id in enumerate(sent_ids):
        if run == v2_8 and sent_id in v2_8_done_sent_ids:
            continue
        elif run == v2_11 and sent_id in v2_11_done_sent_ids:
            continue
        if run == v2_8:
            text, table = table1_d[sent_id]['text'], table1_d[sent_id]['table']
        elif run == v2_11:
            text, table = table2_d[sent_id]['text'], table2_d[sent_id]['table']
        lines = table.split('\n')
        token_count = int(lines[-1].split('\t')[0])
        word_order = 1
        in_split, first_part_passed = False, False
        prompt_l = []
        for line in lines:
            fields = line.split('\t')
            id_t, lemma_t, pos_t, feats_t = fields[0], fields[2], fields[3], fields[5]
            if '-' in id_t:
                in_split = True
                prompt_l.append('{no} token is split into 2 parts.'.format(no=number_d[word_order]))
                first_part_passed = False
                continue
            feat_l = feats_t.split('|')
            if len(feat_l) == 1 and feat_l[0] == '_':
                feat_l = []
            if in_split:
                if not first_part_passed:
                    word_str_l = ['{no} token\'s first part\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
                    first_part_passed = True
                else:
                    word_str_l = ['{no} token\'s second part\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
                    in_split = False
                    first_part_passed = False
            else:
                word_str_l = ['{no} token\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
            word_str_l.append('its part of speech is {pos}'.format(pos=pos_d[pos_t]['shortdef']))
            if pos_t in ['NOUN', 'VERB']:
                sorted_feat_l = []
                feat_copy = feat_l.copy()
                if pos_t == 'NOUN':
                    order_l = noun_order
                elif pos_t == 'VERB':
                    order_l = verb_order
                for feat_name in order_l:
                    for feat in feat_l:
                        tag, val = feat.split('=')
                        if tag == feat_name:
                            sorted_feat_l.append(feat)
                            feat_copy.remove(feat)
                sorted_feat_l.extend(feat_copy)
                feat_l = sorted_feat_l
            for feat in feat_l:
                psor_on = False
                feat_name, feat_value = feat.split('=')
                if feat_name.endswith('[psor]'):
                    feat_name = feat_name.replace('[psor]', '')
                    psor_on = True
                if feat_name in tag_value_d:
                    feat_phrase = tag_value_d[feat_name]['shortdef']
                    if feat_value in tag_value_d[feat_name]:
                        feat_value = tag_value_d[feat_name][feat_value]['shortdef']
                    else:
                        print('not found: {fn}={fv}'.format(fn=feat_name, fv=feat_value))
                else:
                    feat_phrase = feat_name
                    print('not found: {fn}'.format(fn=feat_name))
                if psor_on:
                    word_str_l.append('its possessor\'s {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    word_str_l.append('its {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
            word_str_l[-1] = 'and ' + word_str_l[-1]
            prompt_l.append(', '.join(word_str_l) + '.')
            if not in_split:
                word_order += 1
        prompt = template.format(token_count=token_count, test_input='\n'.join(prompt_l))
        d = {'sent_id': sent_id, 'text': text, 'prompt': prompt}
        if model == 'openai':
            completion = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            d['output'] = completion.choices[0].message
        elif model == 'llama-replicate':
            output = replicate.run('meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3', input={'prompt': prompt})
            d['output'] = ''.join(list(output))
        elif model == 'llama-hf':
            sequences = pipeline(
                prompt,
                do_sample=True,
                top_k=10,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id,
                max_length=200,
            )
            for seq in sequences:
                print(seq['generated_text'])
                print()
        else:
            print('Unknown model: {model}'.format(model=model))
            d['output'] = ''
        output_l.append(d)
        asked_count += 1
        if run == v2_8:
            with open(v2_8_out, 'w', encoding='utf-8') as f:
                json.dump(output_l, f, ensure_ascii=False, indent=4)
        elif run == v2_11:
            with open(v2_11_out, 'w', encoding='utf-8') as f:
                json.dump(output_l, f, ensure_ascii=False, indent=4)
    if run == v2_8:
        with open(v2_8_out, 'w', encoding='utf-8') as f:
            json.dump(output_l, f, ensure_ascii=False, indent=4)
    elif run == v2_11:
        with open(v2_11_out, 'w', encoding='utf-8') as f:
            json.dump(output_l, f, ensure_ascii=False, indent=4)
    print('Asked {count} questions.'.format(count=asked_count))
    print(len(output_l))

run_l_path = os.path.join(THIS_DIR, 'run_l.json')
if os.path.exists(run_l_path):
    with open(run_l_path, 'r', encoding='utf-8') as f:
        run_l = json.load(f)
else:
    run_l = []
run_l.append({'v2.8': v2_8_out, 'v2.11': v2_11_out, 'now': now, 'prompt': template, 'run_dir': run_dir, 'sentence_count': sentence_count, 'sent_ids': sent_ids, 'seed': args.seed, 'model': model})
with open(os.path.join(THIS_DIR, 'run_l.json'), 'w', encoding='utf-8') as f:
    json.dump(run_l, f, ensure_ascii=False, indent=4)
