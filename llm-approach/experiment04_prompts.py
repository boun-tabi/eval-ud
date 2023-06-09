example_input=""""# sent_id = ins_833
# text = HIDDEN
1 HIDDEN 1936 NUM Year Case=Nom|Number=Sing|Person=3 2 nmod:poss _ _
2-3 HIDDEN _ _ _ _ _ _ _ SpaceAfter=No
2 HIDDEN yıl NOUN _ Case=Loc|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=3 0 root _ _
3 HIDDEN null AUX Zero Number=Plur|Person=1|Polarity=Pos|Tense=Pres 2 cop _ _
4 HIDDEN . PUNCT Stop _ 2 punct _ SpacesAfter=\\n"""

example_output="""# sent_id = ins_833
# text = 1936 yılındayız.
1	1936	1936	NUM	Year	Case=Nom|Number=Sing|Person=3	2	nmod:poss	_	_
2-3	yılındayız	_	_	_	_	_	_	_	SpaceAfter=No
2	yılında	yıl	NOUN	_	Case=Loc|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=3	0	root	_	_
3	yız	null	AUX	Zero	Number=Plur|Person=1|Polarity=Pos|Tense=Pres	2	cop	_	_
4	.	.	PUNCT	Stop	_	2	punct	_	SpacesAfter=\n
"""

test_input = """# sent_id = bio_1265
# text = HIDDEN
1 HIDDEN adeta ADV _ _ 2 advmod _ _
2 HIDDEN kendi PRON Reflex Case=Abl|Number=Sing|Number[psor]=Sing|Person=1|Person[psor]=1 5 acl _ _
3 HIDDEN geç VERB Ptcp Aspect=Perf|Polarity=Pos|Tense=Past|VerbForm=Part 2 compound _ _
4 HIDDEN bir DET Indef _ 5 det _ _
5-6 HIDDEN _ _ _ _ _ _ _ SpaceAfter=No
5 HIDDEN hâl NOUN _ Case=Loc|Number=Sing|Person=3 0 root _ _
6 HIDDEN null AUX Zero Number=Sing|Person=1|Polarity=Pos|Tense=Pres 5 cop _ _
7 HIDDEN . PUNCT Stop _ 5 punct _ SpacesAfter=\\n"""

template="""The following is a parse of a Turkish sentence with the surface forms hidden. The format is called CONLL-U.

{example_input}

Your task is to recover the hidden surface forms and write your answer in CONLL-U format. For example, your answer for the previous parse should be

{example_output}

Now, analyze the following test example and try to recover the hidden surface forms and write your answer in CONLL-U format.

{test_input}
"""