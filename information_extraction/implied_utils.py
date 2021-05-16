#!/usr/bin/env python3
import ast
import spacy
import csv
from database_query import Indexes
from database_query import sql_fetch_recipe_db
from database_query import sql_fetch_util_db
from conceptNet_api import concept_found_conceptNet


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


def match_definition_to_recipe(tool, index, string_to_match):
    for subject in tool[index].split(" | "):
        if "&" in subject:
            conj_counter = 0
            conj_concept_list = subject.split(" & ")
            for conj_subject in conj_concept_list:
                if conj_subject in string_to_match:
                    conj_counter += 1
            if conj_counter == len(conj_concept_list):
                return True
        else:
            if subject in string_to_match:
                return True
    return False


class FindImpliedTools:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')
        self.cur_kitchenware = None
        self.kitchenware = ['grill', 'barbecue', 'bbq', 'fryer', 'skillet', 'pan', 'pot', 'saucepan', 'bowl',
                            'casserole', 'sheet', 'mixer', 'blender', 'dish']

        self.entire_tool_kb = sql_fetch_util_db()
        recipe_rows = sql_fetch_recipe_db()

        self.edited_recipe = ""
        self.tools = []
        self.subjects_in_step = []
        self.verbs_in_step = []
        all_data = []

        for row in recipe_rows:
            self.parse_recipe(row)
            dic = {'URL': row[Indexes.R_URL], 'Preparation': self.edited_recipe, 'Utils': self.tools}
            all_data.append(dic)

            self.tools = []
            self.edited_recipe = ""

        print(all_data)
        # write_to_csv(all_data)

    def parse_recipe(self, recipe):
        dictionary = string_to_dictionary(recipe[Indexes.R_PREPARATION])
        for key in dictionary:
            self.edited_recipe += str(key) + ") "
            step = self.nlp(dictionary[key])
            sentences = list(step.sents)

            self.find_verbs_and_nouns(sentences)
            self.find_kitchenware()

            print(key, dictionary[key])
            print("NOUNS IN THIS STEP: " + str(self.subjects_in_step))
            print("VERBS IN THIS STEP: " + str(self.verbs_in_step))
            print("[parse_preparation] current kitchenware: " + str(self.cur_kitchenware))

            for sentence in sentences:
                for token in sentence:
                    if token.pos_ == "PUNCT":
                        self.edited_recipe = self.edited_recipe[:-1]
                    self.edited_recipe += str(token.text) + " "
                    if token.pos_ == "VERB" or token.pos_ == "PRON":
                        verb = token.lemma_.lower()
                        print("VERB: " + verb)
                        self.find_tool_that_corresponds_to_verb(recipe, verb)

            self.subjects_in_step = []
            self.verbs_in_step = []

    def find_verbs_and_nouns(self, step):
        for sentence in step:
            for token in sentence:
                if token.pos_ == "VERB" or token.pos_ == "PRON":
                    self.verbs_in_step.append(token.lemma_.lower())
                if token.pos_ == "NOUN" and token.dep_ == "dobj" or token.dep_ == "pobj":
                    self.subjects_in_step.append(token.lemma_.lower())

    def find_kitchenware(self):
        for noun in self.subjects_in_step:
            if noun in self.kitchenware:
                self.cur_kitchenware = noun
                break

    def find_tool_that_corresponds_to_verb(self, recipe, verb):
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
                    and self.check_tools_definition(tool, recipe)):
                print("[find_tool] added " + tool[Indexes.T_TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            if (tool[Indexes.T_IMPLIED] is not None
                    and verb in tool[Indexes.T_IMPLIED].split(", ")
                    and kitchenware_is_appropriate
                    and self.is_implied_tool_applicable(tool)
                    and self.check_tools_definition(tool, recipe)):

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
                    print("RETURN FALSE BECAUSE " + verb + " in " + str(self.verbs_in_step))
                    return False
        if tool[Indexes.T_DIRECT_VERB] is not None:
            for verb in tool[Indexes.T_DIRECT_VERB].split(", "):
                if verb in self.verbs_in_step:
                    print("RETURN FALSE BECAUSE " + verb + " in " + str(self.verbs_in_step))
                    return False
        print("RETURN TRUE")
        return True

    def remove_implied_tools(self, tool):
        temp = []
        for implied_verb in tool[Indexes.T_IMPLIED]:
            if implied_verb in self.verbs_in_step:
                temp.append(implied_verb)
        return temp

    def is_kitchenware_appropriate(self, tool):
        return tool[Indexes.T_LOCATION] is None or self.cur_kitchenware in tool[Indexes.T_LOCATION].split(" | ")

    def check_tools_definition(self, tool, recipe):
        definitions = tool[Indexes.T_DEFINE].split(" | ")
        print("[check_tools_definition] found tool " + tool[Indexes.T_TOOL] + " checking " + str(definitions))

        for definition in definitions:
            if "&" in definition:
                conjunction_counter = 0
                conjunction_def_list = definition.split(" & ")
                for conjunction_def in conjunction_def_list:
                    if self.is_tool_suitable(tool, conjunction_def, recipe):
                        conjunction_counter += 1
                if conjunction_counter == len(conjunction_def_list):
                    return True
            else:
                if self.is_tool_suitable(tool, definition, recipe):
                    return True
        return False

    def is_tool_suitable(self, tool, definition, entire_recipe):
        if definition == "title":
            print("[is_tool_suitable] title")
            return check_title(tool, entire_recipe[Indexes.R_TITLE].lower())
        elif definition == "isa":
            print("[is_tool_suitable] ISA")
            return self.handle_isa(tool, Indexes.T_ISA)
        elif definition == "not_isa":
            print("[is_tool_suitable] NOT_ISA")
            return not self.handle_isa(tool, Indexes.T_NOT_ISA)
        elif definition == "subject":
            print("[is_tool_suitable] SUBJECT")
            return match_definition_to_recipe(tool, Indexes.T_SUBJECT, self.subjects_in_step)
        elif definition == "not_subject":
            print("[is_tool_suitable] not_subject")
            return not match_definition_to_recipe(tool, Indexes.T_NOT_SUBJECT, self.subjects_in_step)
        elif definition == "size":
            print("[is_tool_suitable] size")
            return match_definition_to_recipe(tool, Indexes.T_SIZE, entire_recipe[Indexes.R_INGREDIENTS])
        elif definition == "not_size":
            print("[is_tool_suitable] not_size")
            return not match_definition_to_recipe(tool, Indexes.T_NOT_SIZE, entire_recipe[Indexes.R_INGREDIENTS])
        elif definition == "ingredient":
            print("[is_tool_suitable] ingredient")
            return match_definition_to_recipe(tool, Indexes.T_INGREDIENT, entire_recipe[Indexes.R_INGREDIENTS])
        elif definition == "not_ingredient":
            print("[is_tool_suitable] not_ingredient")
            return not match_definition_to_recipe(tool, Indexes.T_NOT_INGREDIENT, entire_recipe[Indexes.R_INGREDIENTS])
        return False

    def handle_isa(self, tool, index):
        for concept in tool[index].split(" | "):
            if "&" in concept:
                conj_counter = 0
                conj_concept_list = concept.split(" & ")
                for conj_concept in conj_concept_list:
                    if concept_found_conceptNet(conj_concept, self.subjects_in_step):
                        conj_counter += 1
                if conj_counter == len(conj_concept_list):
                    return True
            else:
                if concept_found_conceptNet(concept, self.subjects_in_step):
                    return True
        return False
