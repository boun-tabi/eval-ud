def get_prompt(table, pos_d, feat_d, dep_d):
    lines = table.split('\n')
    ids = [line.split('\t')[0] for line in lines if '-' not in line.split('\t')[0]]
    dash_ids = [line.split('\t')[0] for line in lines if '-' in line.split('\t')[0]]
    token_count = len(ids) - len(dash_ids)
    token_order = 1
    in_split, first_part_passed = False, False
    prompt_l = []
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t, head_t, dep_t = fields[0], fields[2], fields[3], fields[5], fields[6], fields[7]
        if '-' in id_t:
            in_split = True
            prompt_l.append('{no} token has 2 parts.'.format(no=number_d[token_order]))
            first_part_passed = False
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        if in_split:
            if not first_part_passed:
                token_str_l = ['{no} token\'s first part\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
                first_part_passed = True
            else:
                token_str_l = ['{no} token\'s second part\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
                in_split = False
                first_part_passed = False
        else:
            token_str_l = ['{no} token\'s lemma is "{lemma}"'.format(no=number_d[token_order], lemma=lemma_t)]
        token_str_l.append('its part of speech is {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        for feat in feat_l:
            psor_on = False
            feat_name, feat_value = feat.split('=')
            if feat_name.endswith('[psor]'):
                feat_name = feat_name.replace('[psor]', '')
                psor_on = True
            if feat_name in feat_d:
                tag_shortdef = feat_d[feat_name]['shortdef']
            if feat_value in feat_d[feat_name]:
                feat_value = feat_d[feat_name][feat_value]['shortdef']
            if psor_on:
                token_str_l.append('its possessor\'s {fn} is {fv}'.format(fn=tag_shortdef, fv=feat_value))
            else:
                token_str_l.append('its {fn} is {fv}'.format(fn=tag_shortdef, fv=feat_value))
        if dep_t != '_':
            dep_name = dep_d[dep_t]['shortdef']
            if head_t == '0':
                token_str_l.append('it\'s the root token')
            else:
                token_str_l.append('it depends on the {head} token with the dependency relation of {dep}'.format(dep=dep_name, head=number_d[int(head_t)]))

        token_str_l[-1] = 'and ' + token_str_l[-1]
        prompt_l.append(', '.join(token_str_l) + '.')
        if not in_split:
            token_order += 1
    question = '\n'.join(prompt_l)
    return template2.format(example_surface=example1_surface, example_token=example1_token, example_input=example1_input, token_count=token_count, test_input=question)

# created on 2023-12-12
# need to update the example with dependencies
template2 = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech, morphological features and dependencies given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i". 

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

# created on 2023-12-12
# "a" {language} may need "an"
generic_template1 = """The following sentences detail linguistic features of a {language} sentence with lemmas, parts of speech, morphological features and dependencies given for each token.

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

example1_token = 7

example1_input = '''1st token's lemma is "meşrutiyet", its part of speech is proper noun, its case is genitive, its number is singular number, its person is third person, and it depends on the 2nd token with the dependency relation of possessive nominal modifier.
2nd token's lemma is "ilan", its part of speech is noun, its case is ablative, its number is singular number, its possessor's number is singular number, its person is third person, its possessor's person is third person, and it depends on the 3rd token with the dependency relation of oblique argument or adjunct.
3rd token's lemma is "önceki", its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
4th token's lemma is "siyasi", its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
5th token's lemma is "faaliyet", its part of speech is noun, its case is dative, its number is plural number, its person is third person, and it depends on the 6th token with the dependency relation of direct object.
6th token's lemma is "kat", its part of speech is verb, its aspect is perfect aspect, its evidentiality is first hand, its number is singular number, its person is third person, its whether the word can be or is negated is positive, affirmative, its tense is past tense, its voice is reflexive voice, and it's the root token.
7th token's lemma is ".", its part of speech is punctuation, and it depends on the 6th token with the dependency relation of punctuation.'''

example1_surface = "Meşrutiyetin ilanından önceki siyasi faaliyetlere katıldı."

# archived on 2023-12-12
template1 = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech and morphological features given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

"{example_surface}"

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

tr_noun_order = ['Person', 'Number', 'Person[psor]', 'Number[psor]', 'Case']
tr_verb_order = ['Voice', 'Mood','Polarity', 'Tense', 'Aspect', 'Person', 'Number']
number_d = {}
for num in range(1, 157):
    str_num = str(num)
    if str_num[-1] == '1' and str_num != '11':
        number_d[num] = '{}st'.format(num)
    elif str_num[-1] == '2' and str_num != '12':
        number_d[num] = '{}nd'.format(num)
    elif str_num[-1] == '3' and str_num != '13':
        number_d[num] = '{}rd'.format(num)
    else:
        number_d[num] = '{}th'.format(num)