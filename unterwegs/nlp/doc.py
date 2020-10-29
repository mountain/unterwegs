import collections
import spacy


nlp = spacy.load("en_core_web_md")


def bow(text):
    bag = collections.OrderedDict()
    d = nlp(text.replace('\n', ' ').strip())

    for tk in d:
        lexeme = d.vocab[tk.text]
        if lexeme.is_alpha and not lexeme.is_stop:
            txt = tk.text.strip()
            if len(txt) > 2:
                if txt not in bag:
                    bag[txt] = 0
                bag[txt] += 1

    for nc in d.noun_chunks:
        chunk = nc.text.strip()
        if len(chunk.split(' ')) > 1:
            if chunk not in bag:
                bag[chunk] = 0
            bag[chunk] += 1

    return bag


