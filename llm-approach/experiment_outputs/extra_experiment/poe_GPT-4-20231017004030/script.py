import os, json, argparse, logging
from datetime import datetime

now = datetime.now().strftime('%Y%m%d%H%M%S')

logger = logging.getLogger(__name__)
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'extra-experiment.log'), format='%(asctime)s %(levelname)s %(name)s %(message)s')

logger.info('Started at {now}'.format(now=now))

template="""The following sentences detail linguistic features of an English sentence with lemmas, parts of speech and morphological features given for each token. The sentence has 11 tokens.

1st token's lemma is "read", its part of speech is verb, its mood is imperative, and its form of verb is finite verb.
2nd token's lemma is "the", its part of speech is determiner, its definiteness or state is definite, and its pronominal type is article.
3rd token's lemma is "entire", its part of speech is adjective, and its degree of comparison is positive, first degree.
4th token's lemma is "article", its part of speech is noun, and its number is singular.
5th token's lemma is ";", and its part of speech is punctuation.
6th token is split into 2 parts.
6th token's first part's lemma is "there", and its part of speech is pronoun.
6th token's second part's lemma is "be", its part of speech is verb, its mood is indicative, its number is singular, its person is third person, its tense is present tense, and its form of verb is finite verb.
7th token's lemma is "a", its part of speech is determiner, its definiteness or state is indefinite, and its pronominal type is article.
8th token's lemma is "punchline", its part of speech is noun, and its number is singular.
9th token's lemma is ",", and its part of speech is punctuation.
10th token's lemma is "too", and its part of speech is adverb.
11th token's lemma is ".", and its part of speech is punctuation.

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

"Read the entire article; there's a punchline, too."

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations.

{test_input}"""

script_path = os.path.abspath(__file__)
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()
THIS_DIR = os.path.dirname(script_path)

parser = argparse.ArgumentParser()
parser.add_argument('-tb', '--treebank', type=str)
parser.add_argument('-r', '--run-dir', type=str)
parser.add_argument('-s', '--sents', type=str)
parser.add_argument('-m', '--model', type=str)
parser.add_argument('-l', '--lang', type=str)
args = parser.parse_args()

lang = args.lang

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'tr-ud-docs')
with open(os.path.join(data_dir, 'feat-{}.json'.format(lang)), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'pos-{}.json'.format(lang)), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)

if args.run_dir:
    run_dir = args.run_dir
    print('Using run directory {run_dir}'.format(run_dir=run_dir))
    with open(os.path.join(run_dir, 'md.json'), 'r', encoding='utf-8') as f:
        md = json.load(f)
    model = md['model']
    tb = md['treebank']
    sent_ids = md['sent_ids']
    sentence_count = md['sentence_count']
else:
    output_dir = os.path.join(THIS_DIR, 'experiment_outputs')
    exp_dir = os.path.join(output_dir, 'extra_experiment')
    if args.model:
        model = args.model
    else:
        print('Please specify a model.')
        exit()
    run_dir = os.path.join(exp_dir, '{model}-{now}'.format(model=model, now=now))
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, 'script.py'), 'w', encoding='utf-8') as f:
        f.write(script_content)
    if args.treebank:
        tb = args.treebank
    else:
        print('Please specify a treebank.')
        exit()
    if args.sents:
        sents_path = args.sents
        with open(sents_path, 'r', encoding='utf-8') as f:
            sent_ids = json.load(f)
        sentence_count = len(sent_ids)
    else:
        print('Please specify a sentence list.')
        exit()
    with open(os.path.join(run_dir, 'md.json'), 'w', encoding='utf-8') as f:
        md = {'sentence_count': sentence_count, 'sent_ids': sent_ids, 'model': model, 'now': now, 'run_dir': run_dir, 'prompt': template, 'treebank': tb}
        json.dump(md, f, ensure_ascii=False, indent=2)

if model == 'openai_gpt-3.5-turbo':
    print('Using OpenAI API.')
    import openai
    with open(os.path.join(THIS_DIR, 'openai.json')) as f:
        openai_d = json.load(f)
    openai.api_key = openai_d['key']
elif model == 'replicate_llama-2-70b-chat':
    print('Using LLAMA API.')
    import replicate
    with open(os.path.join(THIS_DIR, 'replicate.json')) as f:
        token = json.load(f)['token']
    os.environ['REPLICATE_API_TOKEN'] = token
elif model == 'meta-llama_Llama-2-7b-chat-hf':
    from transformers import AutoTokenizer
    import transformers
    import torch

    tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf')
    pipeline = transformers.pipeline(
        "text-generation",
        model='meta-llama/Llama-2-7b-chat-hf',
        torch_dtype=torch.float16,
        device_map="auto",
    )
elif model.startswith('perplexity'):
    with open(os.path.join(THIS_DIR, 'perplexity.json')) as f:
        perplexity_d = json.load(f)
    import requests
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer {token}".format(token=perplexity_d['token'])
    }
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": "How many stars are there in our galaxy?"
            }
        ]
    }
    if model == 'perplexity_mistral-7b-instruct':
        payload['model'] = 'mistral-7b-instruct'
    elif model == 'perplexity_llama-2-70b-chat':
        payload['model'] = 'llama-2-70b-chat'
elif model.startswith('poe'):
    with open(os.path.join(THIS_DIR, 'poe.json')) as f:
        poe_d = json.load(f)
    token = poe_d['token']
    from fastapi_poe.types import ProtocolMessage
    from fastapi_poe.client import get_bot_response
    import asyncio
    async def get_response(prompt, bot_name, api_key):
        message = ProtocolMessage(role='user', content=prompt)
        output = ''
        async for partial in get_bot_response(messages=[message], bot_name=bot_name, api_key=api_key):
            output += partial.text
        return output

with open(tb, 'r', encoding='utf-8') as f:
    tb_data = json.load(f)
table_d = {}
for example in tb_data:
    sent_id, text, table = example['sent_id'], example['text'], example['table']
    table_d[sent_id] = {'table': table, 'text': text}

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
tb_out = os.path.join(run_dir, 'tb_output.json')
if os.path.exists(tb_out):
    with open(tb_out, 'r', encoding='utf-8') as f:
        tb_output = json.load(f)
else:
    tb_output = []
tb_done_sent_ids = [el['sent_id'] for el in tb_output]
run_done = True
asked_count = 0
output_l = tb_output
for i, sent_id in enumerate(sent_ids):
    output = ''
    if sent_id in tb_done_sent_ids:
        continue
    text, table = table_d[sent_id]['text'], table_d[sent_id]['table']
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
    if model == 'openai_gpt-3.5-turbo':
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        d['output'] = completion.choices[0].message['content']
    elif model == 'replicate_llama-2-70b-chat':
        output = replicate.run('meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3', input={'prompt': prompt})
        d['output'] = ''.join(list(output))
    elif model == 'meta-llama_Llama-2-7b-chat-hf':
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
    elif model.startswith('perplexity'):
        payload['messages'][1]['content'] = prompt
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if 'choices' not in data:
            continue
        d['output'] = data['choices'][0]['message']['content']
    elif model.startswith('poe'):
        try:
            if model == 'poe_GPT-3.5-Turbo':
                output = asyncio.run(get_response(prompt, 'GPT-3.5-Turbo', token))
            elif model == 'poe_GPT-4':
                output = asyncio.run(get_response(prompt, 'GPT-4', token))
            elif model == 'poe_Claude-instant-100k':
                output = asyncio.run(get_response(prompt, 'Claude-instant-100k', token))
            elif model == 'poe_Claude-2-100k':
                output = asyncio.run(get_response(prompt, 'Claude-2-100k', token))
            elif model == 'poe_Llama-2-70b':
                output = asyncio.run(get_response(prompt, 'Llama-2-70b', token))
        except:
            continue
        d['output'] = output
    else:
        print('Unknown model: {model}'.format(model=model))
        d['output'] = ''
    if d['output'] == '':
        continue
    output_l.append(d)
    asked_count += 1
    with open(tb_out, 'w', encoding='utf-8') as f:
        json.dump(output_l, f, ensure_ascii=False, indent=4)
with open(tb_out, 'w', encoding='utf-8') as f:
    json.dump(output_l, f, ensure_ascii=False, indent=4)
print('Asked {count} questions.'.format(count=asked_count))
output_l_len = len(output_l)
print('Output length: {len}'.format(len=output_l_len))
if output_l_len != sentence_count:
    run_done = False
    print('Not all sentences are done.')
else:
    print('All sentences are done.')
if run_done:
    print('All done.')
else:
    print('Not all done.')
    os.system('python3 {script_path} -r {run_dir} -l {lang}'.format(script_path=script_path, run_dir=run_dir, lang=lang))
logger.info('Ended at {now}'.format(now=datetime.now().strftime('%Y%m%d%H%M%S')))

