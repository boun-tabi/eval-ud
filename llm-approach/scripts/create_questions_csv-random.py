import os, json, re, argparse
from difflib import SequenceMatcher

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run-dir', type=str, required=True, help='The run directory.')
parser.add_argument('-s', '--sent-ids', type=str, required=True, help='The sentence ids.')
args = parser.parse_args()

with open(args.sent_ids, 'r', encoding='utf-8') as f:
    sent_ids = json.load(f)

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
noun_order = ['Person', 'Number', 'Person[psor]', 'Number[psor]', 'Case']
verb_order = ['Voice', 'Mood','Polarity', 'Tense', 'Aspect', 'Person', 'Number']

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

util_dir = os.path.join(THIS_DIR, '../util')
data_dir = os.path.join(util_dir, 'tr-ud-docs')
with open(os.path.join(data_dir, 'feat.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'pos.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)

def get_prompt(table):
    lines = table.split('\n')
    annotation_d = {}
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t = fields[0], fields[2], fields[3], fields[5]
        annotation_d[id_t] = {}
        if '-' in id_t:
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        annotation_d[id_t]['lemma'] = lemma_t
        annotation_d[id_t]['pos'] = pos_d[pos_t]['shortdef']
        if pos_t in ['NOUN', 'VERB']:
            sorted_feat_l = []
            feat_copy = feat_l.copy()
            if pos_t == 'NOUN':
                order_l = noun_order
            elif pos_t == 'VERB':
                order_l = verb_order
            for feat_name in order_l:
                for feat in feat_l:
                    tag, _ = feat.split('=')
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
                feat_phrase = feat_name
            if psor_on:
                annotation_d[id_t]['possessor\'s ' + feat_phrase] = feat_value
            else:
                annotation_d[id_t][feat_phrase] = feat_value
    return annotation_d

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
run_dir = args.run_dir
model = run_dir.split('/')[-1]
if 'v2.8_output_modified.json' in os.listdir(run_dir) and 'v2.11_output_modified.json' in os.listdir(run_dir):
    v2_8_out = os.path.join(run_dir, 'v2.8_output_modified.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output_modified.json')
else:
    v2_8_out = os.path.join(run_dir, 'v2.8_output.json')
    v2_11_out = os.path.join(run_dir, 'v2.11_output.json')

md_path = os.path.join(run_dir, 'md.json')
with open(md_path, 'r', encoding='utf-8') as f:
    md = json.load(f)
v2_8_path = md['v2.8']
with open(v2_8_path, 'r', encoding='utf-8') as f:
    v2_8_tb = json.load(f)
v2_11_path = md['v2.11']
with open(v2_11_path, 'r', encoding='utf-8') as f:
    v2_11_tb = json.load(f)

res_d = {}
with open(v2_8_out, 'r', encoding='utf-8') as f:
    v2_8_results = json.load(f)
llm_pattern = re.compile('The surface form of the sentence is:?\s+"(.+?)"$')
llm_pattern2 = re.compile('\(?Note:.*\)?$')
quote_pattern = re.compile('^"(.+?)"$')
for result in v2_8_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1).strip()
    llm_match2 = llm_pattern2.search(output_text)
    if llm_match2:
        output_text = output_text[:llm_match2.start()].strip()
    quote_match = quote_pattern.search(output_text)
    if quote_match:
        output_text = quote_match.group(1).strip()
    table = v2_8_tb[sent_id]['table']
    prompt = get_prompt(table)
    res_d[sent_id] = {'original_text': original_text, 'v2_8_text': output_text.strip(), 'v2_8_prompt': prompt}
with open(v2_11_out, 'r', encoding='utf-8') as f:
    v2_11_results = json.load(f)
for result in v2_11_results:
    sent_id = result['sent_id']
    original_text, output_text = result['text'], result['output']
    llm_match = llm_pattern.search(output_text)
    if llm_match:
        output_text = llm_match.group(1).strip()
    llm_match2 = llm_pattern2.search(output_text)
    if llm_match2:
        output_text = output_text[:llm_match2.start()].strip()
    quote_match = quote_pattern.search(output_text)
    if quote_match:
        output_text = quote_match.group(1).strip()
    res_d[sent_id]['v2_11_text'] = output_text.strip()
    table = v2_11_tb[sent_id]['table']    
    prompt = get_prompt(table)
    res_d[sent_id]['v2_11_prompt'] = prompt

questions = {'template': template}
for i, sent_id in enumerate(sent_ids):
    original_text = res_d[sent_id]['original_text']
    v2_8_text = res_d[sent_id]['v2_8_text']
    v2_11_text = res_d[sent_id]['v2_11_text']
    ratio_v2_8 = SequenceMatcher(None, original_text, v2_8_text).ratio()
    ratio_v2_11 = SequenceMatcher(None, original_text, v2_11_text).ratio()
    d = {'original_text': original_text}
    d['v2_8_text'] = v2_8_text
    d['v2_11_text'] = v2_11_text
    d['v2_8_prompt'] = res_d[sent_id]['v2_8_prompt']
    d['v2_11_prompt'] = res_d[sent_id]['v2_11_prompt']
    questions[sent_id] = d

print('Number of sentences: {}'.format(len(questions) - 1))
count_questions = 0
for q in questions:
    if 'v2_8_prompt' in questions[q]:
        count_questions += 1
    if 'v2_11_prompt' in questions[q]:
        count_questions += 1
print('Number of questions: {}'.format(count_questions))
with open(os.path.join(THIS_DIR, 'created_questions_csv-random-{}.json'.format(model)), 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=4, ensure_ascii=False)
