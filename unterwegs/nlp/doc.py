import spacy

from spacy.lang.en.stop_words import STOP_WORDS
from unterwegs.utils.db import rn


nlp = spacy.load("en_core_web_md")


def bow(text):
    d = nlp(text.replace('\n', ' '))
    bag = {}

    for tk in d:
        lexeme = d.vocab[tk.text]
        if not lexeme.is_stop and lexeme.is_alpha:
            if tk.text not in bag:
                bag[tk.text] = 0
            bag[tk.text] += 1

    for nc in d.noun_chunks:
        if nc.text not in bag:
            bag[nc.text] = 0
        bag[nc.text] += 1

    return bag


