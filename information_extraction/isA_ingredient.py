#!/usr/bin/env python3
import spacy
nlp = spacy.load("en_core_web_trf")


if __name__ == "__main__":
    string = "Melt butter in a cast-iron skillet over medium-high heat."
    step = nlp(string)
    sentences = list(step.sents)
    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)