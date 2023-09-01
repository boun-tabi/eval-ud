import os, json, argparse, openai

now = '20230818101642'

template="""The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech and morphological features given for each word. The sentence has 6 words.

1st word's lemma is meşrutiyet, its part of speech is proper noun, its case is genitive, its number is singular number, and its person is third person.
2nd word's lemma is ilan, its part of speech is noun, its case is ablative, its number is singular number, its possessor's number is singular number, its person is third person, and its possessor's person is third person.
3rd word's lemma is önceki, and its part of speech is adjective.
4th word's lemma is siyasi, and its part of speech is adjective.
5th word's lemma is faaliyet, its part of speech is noun, its case is dative, its number is plural number, and its person is third person.
6th word's lemma is kat, its part of speech is verb, its aspect is perfect aspect, its evidentiality is firsthand, its number is singular number, its person is third person, its polarity is positive, its tense is past tense, and its voice is reflexive voice.

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be

Meşrutiyetin ilanından önceki siyasi faaliyetlere katıldı.

Now, analyze the following test example and try to find the surface form of the sentence. It has {word_count} words.

{test_input}"""

script_path = os.path.abspath(__file__)
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()
THIS_DIR = os.path.dirname(script_path)
with open(os.path.join(THIS_DIR, 'openai.json')) as f:
    openai_d = json.load(f)
openai.api_key = openai_d['key']

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'tr-ud-docs')
with open(os.path.join(data_dir, 'feat.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'pos.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)

output_dir = os.path.join(THIS_DIR, 'experiment_outputs')
exp6_dir = os.path.join(output_dir, 'experiment06')
run_dir = os.path.join(exp6_dir, now)
os.makedirs(run_dir, exist_ok=True)
with open(os.path.join(run_dir, 'script.py'), 'w', encoding='utf-8') as f:
    f.write(script_content)

parser = argparse.ArgumentParser()
parser.add_argument('-t8', '--treebank-2-8', type=str, required=True)
parser.add_argument('-t11', '--treebank-2-11', type=str, required=True)
parser.add_argument('-d', '--diff', type=str, required=True)
args = parser.parse_args()
t8 = args.treebank_2_8
v2_8 = '_'.join(os.path.dirname(t8).split('/')[-2:])
t11 = args.treebank_2_11
v2_11 = '_'.join(os.path.dirname(t11).split('/')[-2:])
diff_path = args.diff
with open(diff_path, 'r', encoding='utf-8') as f:
    diff = json.load(f)
ratios = diff['ratios']
class_path = os.path.join(run_dir, 'class_l.json')
with open(class_path, 'r', encoding='utf-8') as f:
    class_l = json.load(f)
sent_ids = []
for el in class_l:
    sent_ids.extend(el['sent_ids'])

with open(t8, 'r', encoding='utf-8') as f:
    t8_data = json.load(f)
with open(t11, 'r', encoding='utf-8') as f:
    t11_data = json.load(f)
table1_d, table2_d = {}, {}
for example in t8_data:
    sent_id, text, table = example['sent_id'], example['text'], example['table']
    table1_d[sent_id] = {'table': table, 'text': text}
for example in t11_data:
    sent_id, text, table = example['sent_id'], example['text'], example['table']
    table2_d[sent_id] = {'table': table, 'text': text}

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
for run in [v2_11]:
    if run == v2_8:
        continue
    output_l = []
    for i, sent_id in enumerate(sent_ids):
        if run == v2_8:
            text, table = table1_d[sent_id]['text'], table1_d[sent_id]['table']
        elif run == v2_11:
            text, table = table2_d[sent_id]['text'], table2_d[sent_id]['table']
        lines = table.split('\n')
        word_count = int(lines[-1].split('\t')[0])
        word_order = 1
        in_split, first_part_passed = False, False
        prompt_l = []
        for line in lines:
            fields = line.split('\t')
            id_t, lemma_t, pos_t, feats_t = fields[0], fields[2], fields[3], fields[5]
            if '-' in id_t:
                word_count -= 1
                in_split = True
                prompt_l.append('{no} word is split into 2 parts.'.format(no=number_d[word_order]))
                first_part_passed = False
                continue
            if pos_t == 'PUNCT':
                word_count -= 1
                continue
            feat_l = feats_t.split('|')
            if len(feat_l) == 1 and feat_l[0] == '_':
                feat_l = []
            if in_split:
                if not first_part_passed:
                    word_str_l = ['{no} word\'s first part\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
                    first_part_passed = True
                else:
                    word_str_l = ['{no} word\'s second part\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
                    in_split = False
                    first_part_passed = False
            else:
                word_str_l = ['{no} word\'s lemma is "{lemma}"'.format(no=number_d[word_order], lemma=lemma_t)]
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
                    print('not found: {fn}'.format(fn=feat_name))
                if psor_on:
                    word_str_l.append('its possessor\'s {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    word_str_l.append('its {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
            word_str_l[-1] = 'and ' + word_str_l[-1]
            prompt_l.append(', '.join(word_str_l) + '.')
            if not in_split:
                word_order += 1
        prompt = template.format(word_count=word_count, test_input='\n'.join(prompt_l))
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        output_l.append({'sent_id': sent_id, 'text': text, 'prompt': prompt, 'output': completion.choices[0].message})
        if run == v2_11:
            with open(v2_11_out, 'w', encoding='utf-8') as f:
                json.dump(output_l, f, ensure_ascii=False, indent=4)
    if run == v2_11:
        with open(v2_11_out, 'w', encoding='utf-8') as f:
            json.dump(output_l, f, ensure_ascii=False, indent=4)
