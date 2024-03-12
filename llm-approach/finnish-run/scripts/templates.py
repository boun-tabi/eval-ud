
def get_sentence_prompt(template, language, table, pos_d, feat_d, dep_d=None):
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
        if dep_d and dep_t != '_':
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
    return template.format(example_surface=example_sentence_surface, example_token=example_sentence_token, example_input=example_sentence_input, token_count=token_count, test_input=question, language=language)

# created on 2024-1-19
template_sentence_with_dep = """The following sentences detail linguistic features of a {language} sentence with lemmas, parts of speech, morphological features and dependencies given for each token.

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

example_sentence_token = 9

example_sentence_input = '''1st token's lemma is "yleis#väri", its part of speech is noun, its case is nominative, its number is singular number, and it depends on the 3rd token with the dependency relation of nominal copular subject.
2nd token's lemma is "olla", its part of speech is auxiliary verb, its mood is indicative, its number is singular number, its person is third person, its tense is present tense, its form of verb or deverbative is finite verb, its voice is active voice, and it depends on the 3rd token with the dependency relation of copula.
3rd token's lemma is "ruskea", its part of speech is adjective, its case is nominative, its degree of comparison is positive, first degree, its number is singular number, and it's the root token.
4th token's lemma is ",", its part of speech is punctuation, and it depends on the 5th token with the dependency relation of punctuation.
5th token's lemma is "siipi", its part of speech is noun, its case is inessive, its number is plural number, and it depends on the 3rd token with the dependency relation of coordinated element.
6th token's lemma is "olla", its part of speech is auxiliary verb, its mood is indicative, its number is singular number, its person is third person, its tense is present tense, its form of verb or deverbative is finite verb, its voice is active voice, and it depends on the 5th token with the dependency relation of copula.
7th token's lemma is "valkea", its part of speech is adjective, its case is nominative, its degree of comparison is positive, first degree, its number is plural number, and it depends on the 8th token with the dependency relation of adjectival modifier.
8th token's lemma is "juova", its part of speech is noun, its case is nominative, its number is plural number, and it depends on the 5th token with the dependency relation of nominal copular subject.
9th token's lemma is ".", its part of speech is punctuation, and it depends on the 3rd token with the dependency relation of punctuation.'''

example_sentence_surface = "Yleisväri on ruskea, siivissä on valkeat juovat."

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