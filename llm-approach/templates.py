# created on 2023-12-12
# need to update the example with dependencies
template2 = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech, morphological features and dependencies given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i". 

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

# created on 2023-12-12
# "a" {language} may need "an"
generic_template1 = """The following sentences detail linguistic features of a {language} sentence with lemmas, parts of speech, morphological features and dependencies given for each token.

The sentence has {example_token} tokens.

{example}

Your task is to find the surface form of the sentence. For example, your answer for the previous parse should be:

{example_surface}

Now, analyze the following test example and try to find the surface form of the sentence. It has {token_count} tokens. Please include all the tokens in your answer in order. Output only the surface form without any explanations or sentences in English.

{test_input}"""

# archived on 2023-12-12
template1 = """The following sentences detail linguistic features of a Turkish sentence with lemmas, parts of speech and morphological features given for each token. Lemma "y" represents the overt copula in Turkish and surfaces as "i".

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