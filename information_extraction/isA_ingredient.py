#!/usr/bin/env python3
import spacy
import neuralcoref
nlp = spacy.load("en_core_web_md")


if __name__ == "__main__":
    string = "1) Mash bananas in a large bowl until smooth."
    step = nlp(string)
    sentences = list(step.sents)
    for sentence in sentences:
        for token in sentence:
            print(token.text, token.pos_, token.dep_)
            
    neuralcoref.add_to_pipe(nlp)
    # doc1 = nlp("")
    # print(doc1._.coref_clusters)

    for ent in step.ents:
        print(ent._.coref_cluster)
