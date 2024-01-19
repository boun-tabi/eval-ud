
def get_token_prompt(template, table, token_id, pos_d, feat_d, dep_d=None):
    lines = table.split('\n')
    ids = [line.split('\t')[0] for line in lines if '-' not in line.split('\t')[0]]
    dash_ids = [line.split('\t')[0] for line in lines if '-' in line.split('\t')[0]]
    token_count = len(ids) - len(dash_ids)
    token_order = 1
    in_split, first_part_passed = False, False
    prompt_l = []
    for line in lines:
        fields = line.split('\t')
        id_t = fields[0]
        if id_t != token_id:
            continue
        lemma_t, pos_t, feats_t, head_t, dep_t = fields[2], fields[3], fields[5], fields[6], fields[7]
        if '-' in id_t:
            in_split = True
            prompt_l.append('The token has 2 parts.')
            first_part_passed = False
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        if in_split:
            if not first_part_passed:
                token_str_l = ['The token\'s first part\'s lemma is "{lemma}"'.format(lemma=lemma_t)]
                first_part_passed = True
            else:
                token_str_l = ['The token\'s second part\'s lemma is "{lemma}"'.format(lemma=lemma_t)]
                in_split = False
                first_part_passed = False
        else:
            token_str_l = ['The token\'s lemma is "{lemma}"'.format(lemma=lemma_t)]
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
                for line in lines:
                    fields = line.split('\t')
                    id_t = fields[0]
                    if id_t == head_t:
                        head_lemma_t = fields[2]
                        break
                token_str_l.append('it depends on the token of the form "{head}" with the dependency relation of {dep}'.format(dep=dep_name, head=head_lemma_t))

        token_str_l[-1] = 'and ' + token_str_l[-1]
        prompt_l.append(', '.join(token_str_l) + '.')
        if not in_split:
            token_order += 1
    question = '\n'.join(prompt_l)
    if dep_d:
        return template.format(example_surface=example_token_surface, example_input=example_token_input_with_dep, token_count=token_count, test_input=question)
    else:
        return template.format(example_surface=example_token_surface, example_input=example_token_input_without_dep, token_count=token_count, test_input=question)

# created on 2024-1-19
template_token_with_dep = '''The following sentences detail linguistic features of a Turkish word with lemmas, parts of speech, morphological features and dependencies.

{example_input}

Your task is to find the surface form of the word. For example, your answer for the previous parse should be: "{example_surface}".

Now, analyze the following test example and try to find the surface form of the word. Output only the surface form without any explanations or sentences in English.

{test_input}'''

# created on 2024-1-19
template_token_without_dep = '''The following sentences detail linguistic features of a Turkish word with lemmas, parts of speech and morphological features.

{example_input}

Your task is to find the surface form of the word. For example, your answer for the previous parse should be: "{example_surface}".

Now, analyze the following test example and try to find the surface form of the word. Output only the surface form without any explanations or sentences in English.

{test_input}'''

example_token_surface = 'gidip'
example_token_input_without_dep = '''The token's lemma is "git", its part of speech is verb, its polarity is positive, affirmative, and its form of verb or deverbative is converb.'''
example_token_input_with_dep = '''The token's lemma is "git", its part of speech is verb, its polarity is positive, affirmative, its form of verb or deverbative is converb, and it depends on the token of the form "kal" with the dependency relation of adverbial clause modifier.'''

tr_noun_order = ['Person', 'Number', 'Person[psor]', 'Number[psor]', 'Case']
tr_verb_order = ['Voice', 'Mood','Polarity', 'Tense', 'Aspect', 'Person', 'Number']
