
def get_example_prompt(table, pos_d, feat_d, dep_d=None):
    lines = table.split('\n')
    ids = [line.split('\t')[0] for line in lines if '-' not in line.split('\t')[0]]
    token_count = len(ids)
    prompt_l = []
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t, head_t, dep_t = fields[0], fields[2], fields[3], fields[5], fields[6], fields[7]
        if '-' in id_t:
            no1, no2 = id_t.split('-')
            prompt_l.append('{no} and {no2} tokens make up a single word.'.format(no=number_d[int(no1)], no2=number_d[int(no2)]))
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        token_str_l = ['{no} token\'s lemma is "{lemma}"'.format(no=number_d[int(id_t)], lemma=lemma_t)]
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
    question = '\n'.join(prompt_l)
    return token_count, question

def get_sentence_prompt(template, example_sentence_surface, example_sentence_token, example_sentence_input, language, table, pos_d, feat_d, dep_d=None):
    token_count, question = get_example_prompt(table, pos_d, feat_d, dep_d)
    return template.format(example_surface=example_sentence_surface, example_token=example_sentence_token, example_input=example_sentence_input, token_count=token_count, test_input=question, language=language)

# created on 2024-4-10
template_sentence_without_dep = """The following sentences detail linguistic features of a {language} sentence with lemmas, parts of speech, morphological features given for each token.

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order.

{test_input}

Answer in JSON, in the following format:

{{"original_form": <SENTENCE>}}"""

# created on 2024-1-19
template_sentence_with_dep = """The following sentences detail linguistic features of a {language} sentence with lemmas, parts of speech, morphological features and dependencies given for each token.

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}

Answer in JSON, in the following format:

{{"original_form": <SENTENCE>}}"""

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