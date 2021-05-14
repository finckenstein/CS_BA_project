#!/usr/bin/env python3
import sqlite3
import ast
import spacy
import csv
nlp = spacy.load('en_core_web_trf')


def write_to_csv(data):
    fields = ['Nouns', 'Occurrence']
    filename = "Nouns.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    conn = sqlite3.connect('../raw_recipes/recipes1.db')
    c = conn.cursor()

    c.execute("SELECT * FROM Recipes;")
    rows = c.fetchall()

    verb_list = []
    count_list = []
    for row in rows:
        list_dic = ast.literal_eval(row[7])
        for key in list_dic:
            step = nlp(list_dic[key])
            sentences = list(step.sents)
            for sentence in sentences:
                for token in sentence:
                    if token.pos_ == "NOUN":
                        verb = token.lemma_.lower()
                        if not (verb in verb_list):
                            verb_list.append(verb)
                            count_list.append(1)
                        elif verb in verb_list:
                            count_list[verb_list.index(verb)] += 1
    all_data = []
    entry = {}
    for curr_verb in verb_list:
        entry = {'Nouns': curr_verb, 'Occurrence': count_list[verb_list.index(curr_verb)]}
        all_data.append(entry)

    write_to_csv(all_data)
