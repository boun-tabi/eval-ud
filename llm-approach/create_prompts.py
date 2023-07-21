import os, json, argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(THIS_DIR, '../data')
with open(os.path.join(data_dir, 'tr_feats_values.json'), 'r', encoding='utf-8') as f:
    tag_value_d = json.load(f)
with open(os.path.join(data_dir, 'tr_pos.json'), 'r', encoding='utf-8') as f:
    pos_d = json.load(f)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--treebank', type=str, required=True)
args = parser.parse_args()

with open(args.treebank, 'r', encoding='utf-8') as f:
    treebank_data = json.load(f)

number_d = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th',
            11: '11th', 12: '12th', 13: '13th', 14: '14th', 15: '15th', 16: '16th', 17: '17th', 18: '18th', 19: '19th',
            20: '20th', 21: '21st', 22: '22nd', 23: '23rd', 24: '24th', 25: '25th', 26: '26th', 27: '27th', 28: '28th',
            29: '29th', 30: '30th', 31: '31st', 32: '32nd', 33: '33rd', 34: '34th', 35: '35th', 36: '36th', 37: '37th'
            , 38: '38th', 39: '39th', 40: '40th', 41: '41st', 42: '42nd', 43: '43rd', 44: '44th', 45: '45th', 46: '46th',
            47: '47th', 48: '48th', 49: '49th', 50: '50th', 51: '51st', 52: '52nd', 53: '53rd', 54: '54th', 55: '55th'}
for i, example in enumerate(treebank_data):
    text = example['text']
    table = example['table']
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
    prompt_l = ['I am asking the surface text of a sentence in Turkish. It has {wc} words.'.format(wc=word_count)] + prompt_l
    prompt_l.append('What\'s the sentence?')
    print('Prompt:')
    print('\n'.join(prompt_l))
    print()
    print('Text:')
    print(text)
    print('-'*50)
    input()

