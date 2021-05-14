#!/usr/bin/env python3
import sqlite3
import ast
import spacy
import csv
nlp = spacy.load('en_core_web_trf')

UTIL = 0
DEFINE = 1
AMBIGUOUS_V = 2
PREPARATION_V = 3
UTIL_TITLE = 4
LOCATION = 5
UTIL_INGREDIENT = 6
RECIPE = 7
NEGATION_RECIPE = 8
NEGATION_INGREDIENT = 9
SUBJECT = 10

URL = 0
TITLE = 1
RATING = 2
SERVING = 3
TIME = 4
CATEGORY = 5
INGREDIENTS = 6
PREPARATION = 7
NUTRITION = 8

util_rows = []


def string_to_dictionary(prep_str):
    return ast.literal_eval(prep_str)


def sql_fetch_recipe_db():
    recipe_connection = sqlite3.connect('../data/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    recipe_cursor.execute("SELECT * FROM Recipes WHERE URL=='https://tasty.co/recipe/vegan-crumble-muffins';")
    return recipe_cursor.fetchall()


def sql_fetch_util_db():
    utils_connection = sqlite3.connect('../data/utils.db')
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Utils;")
    return utils_cursor.fetchall()


def is_util_found(keywords_list, recipe_str):
    print("[is_util_found] ", keywords_list, recipe_str)
    for word in keywords_list:
        if word in recipe_str.lower():
            return True
    return False


def handle_conjunction_in_definition(def_list_keyword, recipe_ingre):
    if is_util_found(def_list_keyword, recipe_ingre):
        return True
    for keyword in def_list_keyword:
        if "&" in keyword:
            conjunction_keywords = keyword.split(" & ")
            print(conjunction_keywords)
            count = 0
            for curr_keyword in conjunction_keywords:
                if curr_keyword in recipe_ingre:
                    print(curr_keyword + " appeared in recipe")
                    count += 1
            print(count, len(conjunction_keywords))
            if count == len(conjunction_keywords):
                return True
        print("ANOTHER ITERATION")
    return False


def find_dobj(step_str, verb):
    found_verb = False
    object_str = ""
    print("[find_dobj] " + step_str, verb)
    sentences = list(nlp(step_str).sents)
    for token in sentences[0]:
        if token.text.lower() == verb.lower():
            print("SETTING found_verb TO TRUE")
            found_verb = True
        elif token.dep_ == "dobj" or token.dep_ == "pobj" and found_verb:
            object_str += token.lemma_.lower() + ", "
    return object_str


def check_definition(curr_def, current_util, recipe_step, recipe_title, recipe_ingre, verb):
    print(curr_def)
    if curr_def == "recipe":
        def_list_keyword = current_util[RECIPE].split(" | ")
        print(def_list_keyword)
        return is_util_found(def_list_keyword, recipe_step)
    elif curr_def == "negation_recipe":
        def_list_keyword = current_util[NEGATION_RECIPE].split(" | ")
        return not is_util_found(def_list_keyword, recipe_step)
    elif curr_def == "negation_ingredient":
        def_list_keyword = current_util[NEGATION_INGREDIENT].split(" | ")
        print(current_util[UTIL])
        return not handle_conjunction_in_definition(def_list_keyword, recipe_ingre)
    elif curr_def == "title":
        def_list_keyword = current_util[UTIL_TITLE].split(" | ")
        return is_util_found(def_list_keyword, recipe_title)
    elif curr_def == "location":
        def_list_keyword = current_util[LOCATION].split(" | ")
        return is_util_found(def_list_keyword, recipe_step)
    elif curr_def == "ingredient":
        def_list_keyword = current_util[UTIL_INGREDIENT].split(" | ")
        return handle_conjunction_in_definition(def_list_keyword, recipe_ingre)
    elif curr_def == "subject":
        def_list_keyword = current_util[SUBJECT].split(" | ")
        subject = find_dobj(recipe_step, verb)
        print("RETURNED FROM [find_dobj]: " + subject)
        if subject is None:
            return False
        else:
            return is_util_found(def_list_keyword, subject)

    return False


def is_util_suitable(recipe_ingredient, recipe_step, recipe_title, curr_util, keyword):
    definition_list = curr_util[DEFINE].split(" | ")
    assert (len(definition_list) != 0)
    for current_definition in definition_list:
        print(current_definition)
        if "&" in current_definition:
            conjunction_definition_list = current_definition.split(" & ")
            count = 0
            for conjunction_definition in conjunction_definition_list:
                if check_definition(conjunction_definition, curr_util, recipe_step,
                                    recipe_title, recipe_ingredient, keyword):
                    count += 1
            print(count, len(conjunction_definition_list))
            if count == len(conjunction_definition_list):
                return True
        else:
            if check_definition(current_definition, curr_util, recipe_step, recipe_title, recipe_ingredient, keyword):
                return True

    return False


def find_utils(recipe, dictionary, util_list):
    count = 0
    preparation = ""
    for key in dictionary:
        preparation += str(key) + ") "
        print(key, dictionary[key])
        step = nlp(dictionary[key])
        sentences = list(step.sents)
        for sentence in sentences:
            for token in sentence:
                if token.pos_ == "PUNCT":
                    preparation = preparation[:-1]
                preparation += str(token.text) + " "
                if token.pos_ == "VERB":
                    verb = token.lemma_.lower()
                    print("VERB: " + verb)
                    for util in util_rows:
                        if util[AMBIGUOUS_V] is not None:
                            for keyword in util[AMBIGUOUS_V].split(", "):
                                if keyword == verb:
                                    print("KEYWORD " + keyword)
                                    is_suitable = is_util_suitable(recipe[INGREDIENTS], dictionary[key],
                                                        recipe[TITLE], util, verb)
                                    if is_suitable and not (util[UTIL] in util_list):
                                        preparation = preparation[:-1]
                                        preparation += "(" + str(count) + ") "
                                        count += 1
                                        print(util[UTIL] + " is suitable and will be added\n")
                                        util_list.append(util[UTIL])
                                    elif is_suitable and (util[UTIL] in util_list):
                                        preparation = preparation[:-1]
                                        preparation += "(" + str(util_list.index(util[UTIL])) + ") "
                                    # else:
                                        print(util[UTIL] + " is not suitable and will not be added\n")

                        if util[PREPARATION_V] is not None:
                            for keyword in util[PREPARATION_V].split(", "):
                                if keyword == verb and not (util[UTIL] in util_list):
                                    print(util[UTIL] + " is suitable and will be added\n")
                                    preparation = preparation[:-1]
                                    preparation += "(" + str(count) + ") "
                                    count += 1
                                    util_list.append(util[UTIL])
                                elif keyword == verb and (util[UTIL] in util_list):
                                    preparation = preparation[:-1]
                                    preparation += "(" + str(util_list.index(util[UTIL])) + ") "
    return preparation


def write_to_csv(data):
    fields = ['URL', 'Preparation', 'Utils']
    filename = "found_utils.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    recipe_rows = sql_fetch_recipe_db()
    util_rows = sql_fetch_util_db()

    utils = []
    edited_recipe = ""
    all_data = []
    dic = {}

    for row in recipe_rows:
        edited_recipe = find_utils(row, string_to_dictionary(row[PREPARATION]), utils)
        dic = {'URL': row[URL], 'Preparation': edited_recipe, 'Utils': utils}
        all_data.append(dic)
        utils = []
        edited_recipe = ""

    print(all_data)
    # write_to_csv(all_data)
