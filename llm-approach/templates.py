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

example1_input = '''1st token's lemma is meşrutiyet, its part of speech is proper noun, its case is genitive, its number is singular number, its person is third person, and it depends on the 2nd token with the dependency relation of possessive nominal modifier.
2nd token's lemma is ilan, its part of speech is noun, its case is ablative, its number is singular number, its possessor's number is singular number, its person is third person, its possessor's person is third person, and it depends on the 3rd token with the dependency relation of oblique argument or adjunct.
3rd token's lemma is önceki, its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
4th token's lemma is siyasi, its part of speech is adjective, and it depends on the 5th token with the dependency relation of adjectival modifier.
5th token's lemma is faaliyet, its part of speech is noun, its case is dative, its number is plural number, its person is third person, and it depends on the 6th token with the dependency relation of direct object.
6th token's lemma is kat, its part of speech is verb, its aspect is perfect aspect, its evidentiality is first hand, its number is singular number, its person is third person, its whether the word can be or is negated is positive, affirmative, its tense is past tense, its voice is reflexive voice, and it's the root token.
7th token's lemma is ., its part of speech is punctuation, and it depends on the 6th token with the dependency relation of punctuation.'''

example1_surface = "Meşrutiyetin ilanından önceki siyasi faaliyetlere katıldı."

# archived on 2023-12-12
template1 = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech and morphological features given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

The sentence has {example_token} tokens.

{example_input}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

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