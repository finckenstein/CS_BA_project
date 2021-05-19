#!/usr/bin/env python3
import ast
import spacy
import csv
from database_query import Indexes
from database_query import sql_fetch_recipe_db
from database_query import sql_fetch_util_db
from conceptNet_api import concept_found_concept_net


def string_to_dictionary(prep_str):
    return ast.literal_eval(prep_str)


def write_to_csv(data):
    fields = ['URL', 'Preparation', 'Utils']
    filename = "found_utils.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def check_title(tool, recipe_title):
    for curr_tool_title in tool[Indexes.T_TITLE].split(" | "):
        if str(curr_tool_title) in str(recipe_title):
            return True
    return False


def match_definition_to_recipe(tool, index, subjects_in_step):
    for subject in tool[index].split(" | "):
        if "&" in subject:
            counter = 0
            conj_concept_list = subject.split(" & ")
            for conj_subject in conj_concept_list:
                for key in subjects_in_step:
                    for subject_target in subjects_in_step[key]:
                        if subject_target == conj_subject:
                            counter += 1
            if counter < len(conj_concept_list)-1:
                print("[match_definition_to_recipe] RETURN TRUE")
                return True
        else:
            for key in subjects_in_step:
                for subject_target in subjects_in_step[key]:
                    if subject_target == subject:
                        print("[match_definition_to_recipe] RETURN TRUE")
                        return True
    print("[match_definition_to_recipe] RETURN FALSE BECAUSE "+str(tool[index].split(" | "))+" NOT IN "+
          str(subjects_in_step))
    return False


def match_definition_to_ingredient(tool, index, ingredient_list):
    print("[match_definition_to_ingredient] ingredient list: " + str(ingredient_list))
    print("[match_definition_to_ingredient] tool: " + str(tool[Indexes.T_TOOL]))
    for keyword in tool[index].split(" | "):
        print("keyword from tool " + str(keyword))
        if "&" in keyword:
            conj_counter = 0
            conj_keyword_list = keyword.split(" & ")
            for conj_keyword in conj_keyword_list:
                for ingredient in ingredient_list:
                    if ingredient == conj_keyword:
                        print("[match_definition_to_ingredient] increase counter because " + str(ingredient) +
                              " is equal to " + str(conj_keyword))
                        conj_counter += 1
            if conj_counter == len(conj_keyword_list):
                return True
        else:
            for ingredient in ingredient_list:
                if ingredient == keyword:
                    print("[match_definition_to_ingredient] RETURN TRUE because " + str(ingredient) + " is equal to " +
                          str(keyword))
                    return True
    print("[match_definition_to_ingredient] RETURN FALSE")
    return False


def match_definition_to_concept_net(tool, index, subjects_to_match, just_sentence):
    for concept in tool[index].split(" | "):
        if "&" in concept:
            conj_concept_list = concept.split(" & ")
            for conj_concept in conj_concept_list:
                if not concept_found_concept_net(conj_concept, subjects_to_match, just_sentence):
                    continue
            return True
        else:
            if concept_found_concept_net(concept, subjects_to_match, just_sentence):
                return True
    return False


class FindImpliedTools:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')
        self.cur_kitchenware = None
        self.kitchenware = {'grill': [], 'barbecue': [], 'bbq': [], 'air fryer': [], 'skillet': [], 'pan': [],
                            'pot': [], 'saucepan': [], 'small bowl': [], 'medium bowl': [], 'large bowl': [],
                            'casserole': [], 'baking sheet': [], 'mixer': [], 'blender': [], 'baking dish': [],
                            'foil dish': []}

        self.entire_tool_kb = sql_fetch_util_db()
        recipe_rows = sql_fetch_recipe_db()

        self.edited_recipe = ""
        self.tools = []
        self.subjects_in_step = {}
        self.verbs_in_step = []
        self.verbs_in_ingredient = []
        self.nouns_in_ingredient = []
        all_data = []

        for row in recipe_rows:
            self.parse_ingredients(row[Indexes.R_INGREDIENTS])
            self.parse_recipe(row)
            dic = {'URL': row[Indexes.R_URL], 'Preparation': self.edited_recipe, 'Utils': self.tools}
            all_data.append(dic)

            self.verbs_in_ingredient = []
            self.nouns_in_ingredient = []
            self.tools = []
            self.edited_recipe = ""

        print(all_data)
        # write_to_csv(all_data)

    def parse_ingredients(self, ingredient_str):
        ingredient_list = string_to_dictionary(ingredient_str)
        for key in ingredient_list:
            for ingredient_elem in ingredient_list[key]:
                index = 0
                ingredient_elem_spacy = self.nlp(ingredient_elem)
                for token in ingredient_elem_spacy:
                    if token.pos_ == "NOUN":
                        if token.dep_ == "compound":
                            self.nouns_in_ingredient.append(
                                token.lemma_.lower() + " " + ingredient_elem_spacy[index + 1].
                                lemma_.lower())
                        elif not token.lemma_.lower() in self.nouns_in_ingredient:
                            self.nouns_in_ingredient.append(token.lemma_.lower())
                    elif token.pos_ == "VERB" and not token.lemma_.lower() in self.verbs_in_ingredient:
                        self.verbs_in_ingredient.append(token.lemma_.lower())
                    index += 1
        print("VERBS: " + str(self.verbs_in_ingredient))
        print("NOUNS: " + str(self.nouns_in_ingredient))

    def parse_recipe(self, recipe):
        dictionary = string_to_dictionary(recipe[Indexes.R_PREPARATION])
        for key in dictionary:
            self.edited_recipe += str(key) + ") "
            step = self.nlp(dictionary[key])
            sentences = list(step.sents)

            self.find_verbs_and_nouns_in_step(sentences)

            print(key, dictionary[key])
            print("NOUNS IN THIS STEP: " + str(self.subjects_in_step))
            print("VERBS IN THIS STEP: " + str(self.verbs_in_step))
            num_sentence = 0
            for sentence in sentences:
                self.find_kitchenware(num_sentence)
                print("[parse_preparation] current kitchenware: " + str(self.cur_kitchenware))
                for token in sentence:
                    if token.pos_ == "PUNCT":
                        self.edited_recipe = self.edited_recipe[:-1]
                    self.edited_recipe += str(token.text) + " "
                    if token.pos_ == "VERB" or token.pos_ == "PRON":
                        if token.dep_ == "amod":
                            continue
                        verb = token.lemma_.lower()
                        print("VERB: " + verb)
                        self.find_tool_that_corresponds_to_verb(recipe, verb, num_sentence)
                num_sentence += 1

            self.subjects_in_step = {}
            self.verbs_in_step = []

    def find_verbs_and_nouns_in_step(self, step):
        num_sentences = 0
        for sentence in step:
            self.find_verbs_and_nouns_in_sentence(num_sentences, sentence)
            num_sentences += 1

    def find_verbs_and_nouns_in_sentence(self, num_sentences, sentence):
        i = 0
        self.subjects_in_step[num_sentences] = []
        while i < len(sentence):
            print("[find_verbs_and_nouns_in_sentence]"+str(sentence[i].lemma_.lower()))
            if (sentence[i].pos_ == "VERB" or sentence[i].pos_ == "PRON") and not sentence[i].lemma_.lower() in self.verbs_in_step:
                self.verbs_in_step.append(sentence[i].lemma_.lower())
            if sentence[i].pos_ == "NOUN":
                if sentence[i].dep_ == "compound" and not str(sentence[i].lemma_.lower() + " " + sentence[i + 1].lemma_.lower()) in self.subjects_in_step:
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower() + " " + sentence[i + 1].lemma_.lower())
                elif sentence[i].dep_ == "nsubj" or sentence[i].dep_ == "dobj" or sentence[i].dep_ == "pobj" and not sentence[i].lemma_.lower() in self.subjects_in_step:
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower())
            elif sentence[i].lemma_.lower() == "small" or sentence[i].lemma_.lower() == "medium" or sentence[i].lemma_.lower() == "large":
                if i+1 < len(sentence)-1 and "bowl" in sentence[i + 1].text.lower():
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower() + " " + sentence[i + 1].lemma_.lower())
                    i += 1
                elif i+2 < len(sentence)-1 and "bowl" in sentence[i + 2].text.lower():
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower() + " " + sentence[i + 2].lemma_.lower())
                    i += 2
                elif i+3 < len(sentence)-1 and "bowl" in sentence[i + 3].text.lower():
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower() + " " + sentence[i + 3].lemma_.lower())
                    i += 3
            i += 1

    def find_kitchenware(self, num_sentences):
        for noun in self.subjects_in_step[num_sentences]:
            for kitchenware in self.kitchenware:
                if noun == kitchenware:
                    self.cur_kitchenware = noun
                    break

    def find_tool_that_corresponds_to_verb(self, recipe, verb, sentence_in_step):
        for tool in self.entire_tool_kb:
            kitchenware_is_appropriate = self.is_kitchenware_appropriate(tool)

            if (tool[Indexes.T_DIRECT_VERB] is not None
                    and verb in tool[Indexes.T_DIRECT_VERB].split(", ")
                    and kitchenware_is_appropriate):
                print("[find_tool] added " + tool[Indexes.T_TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            if (tool[Indexes.T_AMBIGUOUS_VERB] is not None
                    and verb in tool[Indexes.T_AMBIGUOUS_VERB].split(", ")
                    and kitchenware_is_appropriate
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[Indexes.T_TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            if (tool[Indexes.T_IMPLIED] is not None
                    and verb in tool[Indexes.T_IMPLIED].split(", ")
                    and kitchenware_is_appropriate
                    and self.is_implied_tool_applicable(tool)
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[Indexes.T_TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

    def append_tool_to_list(self, tool):
        if not (tool[Indexes.T_TOOL] in self.tools):
            self.tools.append(tool[Indexes.T_TOOL])
        self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += "(" + str(self.tools.index(tool[Indexes.T_TOOL])) + ") "

    def is_implied_tool_applicable(self, tool):
        print("[is_implied_tool_applicable] verbs: " + str(self.verbs_in_step))

        if tool[Indexes.T_AMBIGUOUS_VERB] is not None:
            for verb in tool[Indexes.T_AMBIGUOUS_VERB].split(", "):
                if verb in self.verbs_in_step:
                    print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " in " + str(self.verbs_in_step))
                    return False
        if tool[Indexes.T_DIRECT_VERB] is not None:
            for verb in tool[Indexes.T_DIRECT_VERB].split(", "):
                if verb in self.verbs_in_step:
                    print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " in " + str(self.verbs_in_step))
                    return False
        print("[is_implied_tool_applicable]RETURN TRUE")
        return True

    def is_kitchenware_appropriate(self, tool):
        return tool[Indexes.T_LOCATION] is None or self.cur_kitchenware in tool[Indexes.T_LOCATION].split(" | ")

    def check_tools_definition(self, tool, recipe, sentence_in_step):
        if tool[Indexes.T_DEFINE] is None:
            return True
        definitions = tool[Indexes.T_DEFINE].split(" | ")
        print("[check_tools_definition] found tool " + tool[Indexes.T_TOOL] + " checking " + str(definitions))

        for definition in definitions:
            if "&" in definition:
                conjunction_counter = 0
                conjunction_def_list = definition.split(" & ")
                for conjunction_def in conjunction_def_list:
                    if self.is_tool_suitable(tool, conjunction_def, recipe, sentence_in_step):
                        conjunction_counter += 1
                if conjunction_counter == len(conjunction_def_list):
                    return True
            else:
                if self.is_tool_suitable(tool, definition, recipe, sentence_in_step):
                    return True
        return False

    def is_tool_suitable(self, tool, definition, entire_recipe, sentence_in_step):
        if definition == "title":
            print("[is_tool_suitable] title")
            return check_title(tool, entire_recipe[Indexes.R_TITLE].lower())
        elif definition == "isa":
            print("[is_tool_suitable] ISA")
            return match_definition_to_concept_net(tool, Indexes.T_ISA, self.subjects_in_step, False)
        elif definition == "not_isa":
            print("[is_tool_suitable] NOT_ISA")
            return not match_definition_to_concept_net(tool, Indexes.T_NOT_ISA, self.subjects_in_step, False)
        elif definition == "isa s":
            print("[is_tool_suitable] ISA S")
            return match_definition_to_concept_net(tool, Indexes.T_ISA, self.subjects_in_step[sentence_in_step], True)
        elif definition == "not_isa s":
            print("[is_tool_suitable] ISA S")
            return match_definition_to_concept_net(tool, Indexes.T_NOT_ISA, self.subjects_in_step[sentence_in_step], True)
        elif definition == "subject":
            print("[is_tool_suitable] SUBJECT")
            return match_definition_to_recipe(tool, Indexes.T_SUBJECT, self.subjects_in_step)
        elif definition == "not_subject":
            print("[is_tool_suitable] not_subject")
            return not match_definition_to_recipe(tool, Indexes.T_NOT_SUBJECT, self.subjects_in_step)
        elif definition == "size":
            print("[is_tool_suitable] size")
            return match_definition_to_ingredient(tool, Indexes.T_SIZE, self.verbs_in_ingredient)
        elif definition == "not_size":
            print("[is_tool_suitable] not_size")
            return not match_definition_to_ingredient(tool, Indexes.T_NOT_SIZE, self.verbs_in_ingredient)
        elif definition == "ingredient":
            print("[is_tool_suitable] ingredient")
            return match_definition_to_ingredient(tool, Indexes.T_INGREDIENT, self.nouns_in_ingredient)
        elif definition == "not_ingredient":
            print("[is_tool_suitable] not_ingredient")
            return not match_definition_to_ingredient(tool, Indexes.T_NOT_INGREDIENT, self.nouns_in_ingredient)
        return False
