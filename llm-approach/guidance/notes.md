## OpenAI

### 'pattern' keyword

I've gotten the error below on Jun 9 2023. `pattern` cannot be used with OpenAI models currently.

> OpenAI API does not support Guidance pattern controls!

### Generation example without 'pattern'

We can see from [the example](https://github.com/microsoft/guidance/#guidance-acceleration-notebook) that we can use 'gen' without any parameters, only a name. I have used the model `text-davinci-003` with the following prompt:

```text
The following is an annotation of a Turkish sentence in CoNLL-U format.
1       {{gen '1'}}     1936    NUM     Year    Case=Nom|Number=Sing|Person=3   2       nmod:poss       _       _
2-3     {{gen '2-3'}}   _       _       _       _       _       _       _       SpaceAfter=No
2       {{gen '2'}}     yıl     NOUN    _       Case=Loc|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=3  0       root_       _
3       {{gen '3'}}     null    AUX     Zero    Number=Plur|Person=1|Polarity=Pos|Tense=Pres    2       cop     _       _
4       {{gen '4'}}     .       PUNCT   Stop    _       2       punct   _       SpacesAfter=\n
```

The output is as follows:

```text
The following is an annotation of a Turkish sentence in CoNLL-U format.
1       Bu      bu      DET     _       Definite=Def|PronType=Dem       2       det     _       _
2       gün     gün     NOUN    _       Number=Sing     4       nsubj   _       _
3       hava    hava    NOUN    _       Number=Sing     4       compound        _       _
4       çok     çok     ADV     _       _       0       root    _       _
5       sıcak   sıcak   ADJ     _       Degree=Pos      4       advmod  _       _       1936    NUM     Year    Case=Nom|Number=Sing|Person=3       2       nmod:poss       _      _
2-3     gün hava        gün hava        NOUN    _       Number=Sing     4       compound        _       _       _       _  __       _       _       _       SpaceAfter=No
2       gün     gün     NOUN    _       Number=Sing     4       nsubj   _       _       1936    NUM     Year    Case=Nom|Number=Sing|Person=3       2       nmod:poss       _      _       yıl     NOUN    _       Case=Loc|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=3      0       root    _       _
3       hava    hava    NOUN    _       Number=Sing     4       compound        _       _       _       _       _       _  __       _       SpaceAfter=No   null    AUX     Zero    Number=Plur|Person=1|Polarity=Pos|Tense=Pres    2       cop     _  _
4       çok     çok     ADV     _       _       0       root    _       _       sıcak   ADJ     _       Degree=Pos      4  advmod   _       _       .       PUNCT   Stop    _      2       punct   _       SpacesAfter=\n
```

It generated more than what I asked for.
