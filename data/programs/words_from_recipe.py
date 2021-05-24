#!/usr/bin/env python3
import sqlite3
import ast
import spacy
import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('../database_query'))))
import database_query as db
nlp = spacy.load('en_core_web_trf')


def write_to_csv(w_type, data, file):
    fields = [w_type, 'Occurrence']
    filename = file
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def extract_words_and_occurrence_of_preparation(word_type, index, filename):
    recipe_rows = db.sql_fetch_recipe_db("", "../../")
    word_list = []
    count_list = []

    for row in recipe_rows:
        list_dic = ast.literal_eval(row[index])
        for key in list_dic:
            step = nlp(list_dic[key])
            sentences = list(step.sents)
            for sentence in sentences:
                for token in sentence:
                    if token.pos_ == word_type:
                        word = token.lemma_.lower()
                        if word not in word_list:
                            word_list.append(word)
                            count_list.append(1)
                        elif word in word_list:
                            count_list[word_list.index(word)] += 1
    all_data = []
    for word in word_list:
        entry = {word_type: word, 'Occurrence': count_list[word_list.index(word)]}
        all_data.append(entry)

    write_to_csv(word_type, all_data, filename)


def extract_words_and_occurrence_of_ingredients(word_type, index, filename):
    recipe_rows = db.sql_fetch_recipe_db("", "../../")
    word_list = []
    count_list = []

    for row in recipe_rows:
        list_dic = ast.literal_eval(row[index])
        for key in list_dic:
            print("key: " + str(key))
            print("ingredient list: " + str(list_dic[key]))
            for ingredient_elem in list_dic[key]:
                spacy_ingredient_elem = nlp(ingredient_elem)
                for token in spacy_ingredient_elem:
                    if token.pos_ == word_type:
                        word = token.lemma_.lower()
                        if word not in word_list:
                            word_list.append(word)
                            count_list.append(1)
                        elif word in word_list:
                            count_list[word_list.index(word)] += 1
    all_data = []
    for word in word_list:
        entry = {word_type: word, 'Occurrence': count_list[word_list.index(word)]}
        all_data.append(entry)

    write_to_csv(word_type, all_data, filename)
