#!/usr/bin/env python3
import spacy
nlp = spacy.load("en_core_web_trf")


if __name__ == "__main__":
    string = "In a large bowl, microwave black beans for 1 minute, or until softened."
    step = nlp(string)
    sentences = list(step.sents)
    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)