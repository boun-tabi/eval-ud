import os, json, argparse, time, experiment04_prompts
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

template="""The following sentences detail linguistic parts of a Turkish sentence with lemmas, parts of speech and morphological features given for each word. The sentence has 5 words.

1st word's lemma is adeta, and its part of speech is adverb.
2nd word's lemma is kendi, its part of speech is pronoun, its case is ablative, its number is singular number, its possessor's number is singular number, its person is first person, and its possessor's person is first person.
3rd word's lemma is geç, its part of speech is verb, its aspect is perfect aspect, its polarity is positive, its tense is past tense, and its verb form is participle.
4th word's lemma is bir, and its part of speech is determiner.
5th word has 2 parts.
5th word's first part's lemma is hal, its part of speech is noun, its case is locative, its number is singular number, and its person is third person.
5th word's second part's lemma is null, its part of speech is auxiliary verb, its number is singular number, its person is first person, its polarity is positive, and its tense is present tense.

Your task is to find the surface text of the sentence. For example, your answer for the previous parse should be

Adeta kendimden geçmiş bir haldeyim.

Now, analyze the following test example and try to find the surface text of the sentence. It has {word_count} words.

{test_input}
"""


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(THIS_DIR, 'openai.json')) as f:
    openai_d = json.load(f)
chat_llm = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo', openai_api_key=openai_d['key'])
llm_chain = LLMChain(
        llm=chat_llm,
        prompt=PromptTemplate.from_template(template)
    )

data_dir = os.path.join(THIS_DIR, '../data')
with open(os.path.join(data_dir, 'tr_feats_values.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'tr_pos.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)

output_dir = os.path.join(THIS_DIR, 'experiment_outputs')

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
args = parser.parse_args()
treebank = args.treebank
version = '_'.join(os.path.dirname(treebank).split('/')[-2:])

with open(args.treebank, 'r', encoding='utf-8') as f:
    treebank_data = json.load(f)

number_d = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th',
            11: '11th', 12: '12th', 13: '13th', 14: '14th', 15: '15th', 16: '16th', 17: '17th', 18: '18th', 19: '19th',
            20: '20th', 21: '21st', 22: '22nd', 23: '23rd', 24: '24th', 25: '25th', 26: '26th', 27: '27th', 28: '28th',
            29: '29th', 30: '30th', 31: '31st', 32: '32nd', 33: '33rd', 34: '34th', 35: '35th', 36: '36th', 37: '37th'
            , 38: '38th', 39: '39th', 40: '40th', 41: '41st', 42: '42nd', 43: '43rd', 44: '44th', 45: '45th', 46: '46th',
            47: '47th', 48: '48th', 49: '49th', 50: '50th', 51: '51st', 52: '52nd', 53: '53rd', 54: '54th', 55: '55th'}
asked_count = 0
output_l = []
for i, example in enumerate(treebank_data[30:]):
    sent_id, text, table = example['sent_id'], example['text'], example['table']
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
            prompt_l.append('{no} word has 2 parts.'.format(no=number_d[word_order]))
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
                word_str_l = ['{no} word\'s first part\'s lemma is {lemma}'.format(no=number_d[word_order], lemma=lemma_t)]
                first_part_passed = True
            else:
                word_str_l = ['{no} word\'s second part\'s lemma is {lemma}'.format(no=number_d[word_order], lemma=lemma_t)]
                in_split = False
                first_part_passed = False
        else:
            word_str_l = ['{no} word\'s lemma is {lemma}'.format(no=number_d[word_order], lemma=lemma_t)]
        word_str_l.append('its part of speech is {pos}'.format(pos=pos_d[pos_t]))
        for feat in feat_l:
            psor_on = False
            feat_name, feat_value = feat.split('=')
            if feat_name.endswith('[psor]'):
                feat_name = feat_name.replace('[psor]', '')
                psor_on = True
            if feat_name in tag_value_d:
                feat_phrase = tag_value_d[feat_name]['phrase']
            if feat_value in tag_value_d[feat_name]['values']:
                feat_value = tag_value_d[feat_name]['values'][feat_value]
            if psor_on:
                word_str_l.append('its possessor\'s {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
            else:
                word_str_l.append('its {fn} is {fv}'.format(fn=feat_phrase, fv=feat_value))
        word_str_l[-1] = 'and ' + word_str_l[-1]
        prompt_l.append(', '.join(word_str_l) + '.')
        if not in_split:
            word_order += 1
    if word_count < 5:
        continue
    prompt = template.format(word_count=word_count, test_input='\n'.join(prompt_l))
    output = llm_chain({'word_count': word_count, 'test_input': '\n'.join(prompt_l)})
    output_l.append({'sent_id': sent_id, 'text': text, 'prompt': prompt, 'output': output})
    with open(os.path.join(output_dir, 'experiment06_output-{}.json'.format(version)), 'w', encoding='utf-8') as f:
        json.dump(output_l, f, ensure_ascii=False, indent=4)
    asked_count += 1
    if asked_count >= 10:
        break

with open(os.path.join(output_dir, 'experiment06_output-{}.json'.format(version)), 'w', encoding='utf-8') as f:
    json.dump(output_l, f, ensure_ascii=False, indent=4)
