#!/usr/bin/env python3
import spacy
nlp = spacy.load("en_core_web_trf")


if __name__ == "__main__":
    string = "Preheat the oven to 450˚F (230°C). Line a baking sheet with parchment paper and grease with nonstick spray."
    step = nlp(string)
    sentences = list(step.sents)
    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)