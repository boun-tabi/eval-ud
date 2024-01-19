def get_md_line_prompt(token_id, line, include_deprel=False, head_token=None):
    if include_deprel and head_token:
        output_str = f'| {token_id} | LEMMA | POS | FEATS | HEAD | DEPREL |' + '\n'
        output_str += '| --- | --- | --- | --- | --- | --- |' + '\n'
    else:
        output_str = f'| {token_id} | LEMMA | POS | FEATS |' + '\n'
        output_str += '| --- | --- | --- | --- |' + '\n'
    fields = line.split('\t')
    lemma_t, pos_t, feats_t = fields[2], fields[3], fields[5]
    if include_deprel and head_token:
        dep_t = fields[7]
    feats_t = feats_t.replace('|', '\|')
    if include_deprel and head_token:
        output_str += f'|  | {lemma_t} | {pos_t} | {feats_t} | {head_token} | {dep_t} |' + '\n'
    else:
        output_str += f'|  | {lemma_t} | {pos_t} | {feats_t} |' + '\n'
    return output_str

def get_md_table_prompt(sent_id, table):
    lines = table.split('\n')
    output_str = f'| {sent_id} | LEMMA | POS | FEATS | HEAD | DEP |' + '\n'
    output_str += '| --- | --- | --- | --- | --- | --- |' + '\n'
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t, head_t, dep_t = fields[0], fields[2], fields[3], fields[5], fields[6], fields[7]
        feats_t = feats_t.replace('|', '\|')
        output_str += f'| {id_t} | {lemma_t} | {pos_t} | {feats_t} | {head_t} | {dep_t} |' + '\n'
    return output_str

def get_prev_md_prompt(table, pos_d, feat_d, dep_d):
    lines = table.split('\n')
    prompt_l = []
    split_count = 0
    just_left = False
    for line in lines:
        fields = line.split('\t')
        id_t, lemma_t, pos_t, feats_t, head_t, dep_t = fields[0], fields[2], fields[3], fields[5], fields[6], fields[7]
        if split_count > 0:
            prompt_l.append('\t- ' + id_t)
            split_count -= 1
            if split_count == 0:
                just_left = True
        else:
            prompt_l.append('- ' + id_t)
        if '-' in id_t:
            split_count = 2
            continue
        feat_l = feats_t.split('|')
        if len(feat_l) == 1 and feat_l[0] == '_':
            feat_l = []
        if split_count or just_left:
            prompt_l.append('\t\t- lemma: _{lemma}_'.format(lemma=lemma_t))
            prompt_l.append('\t\t- part of speech: {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        else:
            prompt_l.append('\t- lemma: _{lemma}_'.format(lemma=lemma_t))
            prompt_l.append('\t- part of speech: {pos}'.format(pos=pos_d[pos_t]['shortdef']))
        if pos_t in ['NOUN', 'VERB']:
            sorted_feat_l = []
            feat_copy = feat_l.copy()
            if pos_t == 'NOUN':
                order_l = tr_noun_order
            elif pos_t == 'VERB':
                order_l = tr_verb_order
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
            if feat_name in feat_d:
                feat_phrase = feat_d[feat_name]['shortdef']
                if feat_value in feat_d[feat_name]:
                    feat_value = feat_d[feat_name][feat_value]['shortdef']
            else:
                feat_phrase = feat_name
            if psor_on:
                if split_count or just_left:
                    prompt_l.append('\t\t- possessor\'s {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    prompt_l.append('\t- possessor\'s {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
            else:
                if split_count or just_left:
                    prompt_l.append('\t\t- {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
                else:
                    prompt_l.append('\t- {fn}: {fv}'.format(fn=feat_phrase, fv=feat_value))
        if dep_t != '_':
            dep_name = dep_d[dep_t]['shortdef']
            if head_t == '0':
                if split_count or just_left:
                    prompt_l.append('\t\t- root token')
                else:
                    prompt_l.append('\t- root token')
            else:
                if split_count or just_left:
                    prompt_l.append('\t\t- dependency relation "{dep}" to the {head} token'.format(dep=dep_name, head=number_d[int(head_t)]))
                else:
                    prompt_l.append('\t- dependency relation "{dep}" to the {head} token'.format(dep=dep_name, head=number_d[int(head_t)]))
        just_left = False
    prompt = '\n'.join(prompt_l)
    return prompt

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
    return template.format(example_surface=example_token_surface, example_input=example_token_input, token_count=token_count, test_input=question)

# created on 2024-1-19
template_token_with_dep = '''The following sentences detail linguistic features of a Turkish word with lemmas, parts of speech, morphological features and dependencies. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

{example_input}

Your task is to find the surface form of the word. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the word. Output only the surface form without any explanations or sentences in English.

{test_input}'''

# created on 2024-1-19
template_token_without_dep = '''The following sentences detail linguistic features of a Turkish word with lemmas, parts of speech and morphological features. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

{example_input}

Your task is to find the surface form of the word. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the word. Output only the surface form without any explanations or sentences in English.

{test_input}'''

example_token_surface = 'yapıyor'
example_token_input = ''''''

def get_sentence_prompt(template, table, pos_d, feat_d, dep_d=None):
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
    return template.format(example_surface=example_sentence_surface, example_token=example_sentence_token, example_input=example_sentence_input, token_count=token_count, test_input=question)

# created on 2023-12-12
template_sentence_with_dep = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech, morphological features and dependencies given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i". 

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

example_sentence_token = 7

example_sentence_input = '''1st token's lemma is "meşrutiyet", its part of speech is proper noun, its case is genitive, its number is singular number, its person is third person, and it depends on the 2nd token with the dependency relation of possessive nominal modifier.
2nd token's lemma is "ilan", its part of speech is noun, its case is ablative, its number is singular number, its possessor's number is singular number, its person is third person, its possessor's person is third person, and it depends on the 3rd token with the dependency relation of oblique argument or adjunct.
3rd token's lemma is "önceki", its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
4th token's lemma is "siyasi", its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
5th token's lemma is "faaliyet", its part of speech is noun, its case is dative, its number is plural number, its person is third person, and it depends on the 6th token with the dependency relation of direct object.
6th token's lemma is "kat", its part of speech is verb, its aspect is perfect aspect, its evidentiality is first hand, its number is singular number, its person is third person, its whether the word can be or is negated is positive, affirmative, its tense is past tense, its voice is reflexive voice, and it's the root token.
7th token's lemma is ".", its part of speech is punctuation, and it depends on the 6th token with the dependency relation of punctuation.'''

example_sentence_surface = "Meşrutiyetin ilanından önceki siyasi faaliyetlere katıldı."

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