#!/usr/bin/env python3
import spacy
import os
import sys
from conceptNet_api import match_to_concept_net
from conceptNet_api import filter_out_non_foods

from alias_functions import string_to_dictionary
from alias_functions import write_to_csv
from alias_functions import check_title
from alias_functions import match_definition_to_recipe
from alias_functions import match_definition_to_ingredient
from alias_functions import is_size_bowl
from alias_functions import is_verb_or_pronoun
from alias_functions import is_small_medium_or_large

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('database_query'))))
import database_query as db


class FindImpliedTools:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')

        self.entire_kitchenware_kb = db.sql_fetch_kitchenware_db("../")
        self.cur_kitchenware = None
        self.kitchenware = []
        self.initialize_kitchenware_array()
        print(self.kitchenware)

        self.entire_tool_kb = db.sql_fetch_tools_db("../")
        self.verbs_in_step = []
        self.subjects_in_step = {}

        self.verbs_in_ingredient = []
        self.foods_in_ingredient = []

        all_data = []
        self.tools = []
        self.edited_recipe = ""
        recipe_rows = db.sql_fetch_recipe_db("URL=='https://tasty.co/recipe/healthy-banana-pancakes'",
                                             "../")
        for recipe in recipe_rows:
            self.parse_ingredients(recipe[db.RecipeI.INGREDIENTS])
            self.parse_recipe(recipe)

            dic = {'URL': recipe[db.RecipeI.URL], 'Preparation': self.edited_recipe, 'Utils': self.tools}
            all_data.append(dic)

            self.reset_variable()

        print(all_data)
        # write_to_csv(all_data)

    def reset_variable(self):
        self.verbs_in_ingredient = []
        self.foods_in_ingredient = []
        self.tools = []
        self.edited_recipe = ""

    def initialize_kitchenware_array(self):
        for row in self.entire_kitchenware_kb:
            for kitchenware in row[db.KitchenwareI.KITCHENWARE].split(", "):
                if kitchenware not in self.kitchenware:
                    self.kitchenware.append(kitchenware)

    def parse_ingredients(self, ingredient_str):
        ingredient_list = string_to_dictionary(ingredient_str)
        elem_index = 0

        for key in ingredient_list:
            for ingredient_elem in ingredient_list[key]:
                print(str(ingredient_elem))
                temp_nouns = self.fetch_nouns_and_initialize_verbs(ingredient_elem)
                temp_food = {elem_index: filter_out_non_foods(temp_nouns)}
                self.foods_in_ingredient.append(temp_food)
                elem_index += 1

        print("VERBS: " + str(self.verbs_in_ingredient))
        print("NOUNS: " + str(self.foods_in_ingredient))

    def fetch_nouns_and_initialize_verbs(self, ingredient_elem):
        temp_nouns = []
        token_index = 0
        elem_spacy = self.nlp(ingredient_elem)

        while token_index < len(elem_spacy):
            token = elem_spacy[token_index]
            if token.pos_ == "NOUN":
                noun = token.lemma_.lower()
                print("noun: " + noun)
                if token.dep_ == "compound":
                    temp_nouns.append(noun + " " + elem_spacy[token_index + 1].lemma_.lower())
                    token_index += 1
                elif noun not in str(temp_nouns):
                    temp_nouns.append(noun)
            elif token.pos_ == "VERB" and not token.lemma_.lower() in self.verbs_in_ingredient:
                self.verbs_in_ingredient.append(token.lemma_.lower())
            token_index += 1

        print("nouns found: " + str(temp_nouns))
        return temp_nouns

    def parse_recipe(self, recipe):
        dictionary = string_to_dictionary(recipe[db.RecipeI.PREPARATION])
        for key in dictionary:
            self.edited_recipe += str(key) + ") "
            step = self.nlp(dictionary[key])
            sentences = list(step.sents)
            self.find_verbs_and_nouns_in_step(sentences)

            print("\n\n", key, dictionary[key])
            print("NOUNS IN THIS STEP: " + str(self.subjects_in_step))
            print("VERBS IN THIS STEP: " + str(self.verbs_in_step))

            num_sentence = 0
            for sentence in sentences:
                self.analyse_recipe_sentence(sentence, recipe, num_sentence)
                num_sentence += 1

            self.subjects_in_step = {}
            self.verbs_in_step = []

    def analyse_recipe_sentence(self, sentence, recipe, num_sentence):
        self.find_kitchenware(num_sentence)
        print("[parse_preparation] current kitchenware: " + str(self.cur_kitchenware))
        index = 0
        while index < len(sentence):
            token = sentence[index]
            token_text = token.text.lower()
            self.handle_punctuation_in_output_text(token)

            if is_verb_or_pronoun(token):
                if token.dep_ == "amod":
                    index += 1
                    continue
                print("VERB: " + token_text)

                self.check_potential_kitchenware_change(token_text)
                self.find_tool_that_corresponds_to_verb(recipe, token_text, num_sentence)

            index = self.potential_change_in_kitchenware(token, token_text, sentence, index)

    def potential_change_in_kitchenware(self, token, token_text, sentence, index):
        if token.pos_ == "NOUN":
            if token.dep_ == "compound":
                self.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
            else:
                self.match_noun_to_kitchenware(token_text)

        elif token.pos_ == "ADJ" and is_small_medium_or_large(token_text):
            if sentence[index + 1].text.lower() == "bowl":
                print("FOUND: " + token_text + sentence[index + 1].text.lower())
                self.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
                index += 1
                self.edited_recipe += str(sentence[index].text) + " "
            elif sentence[index + 2].text.lower() == "bowl":
                print("FOUND: " + token_text + sentence[index + 2].text.lower())
                self.match_noun_to_kitchenware(token_text + " " + sentence[index + 2].text.lower())
                index += 2
                self.edited_recipe += str(sentence[index - 1].text) + " " + str(sentence[index].text)

        return index + 1

    def handle_punctuation_in_output_text(self, token):
        if token.pos_ == "PUNCT":
            self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += str(token.text) + " "

    def match_noun_to_kitchenware(self, noun):
        if not noun == self.cur_kitchenware and noun in self.kitchenware:
            print("[match_noun_to_kitchenware] changed kitchenware from " + self.cur_kitchenware + " to " + noun)
            self.cur_kitchenware = noun

    def check_potential_kitchenware_change(self, verb):
        for kb_row in self.entire_kitchenware_kb:
            if kb_row[db.KitchenwareI.VERB] == verb:
                if self.cur_kitchenware is None or self.cur_kitchenware not in kb_row[db.KitchenwareI.KITCHENWARE]:
                    print("[check_potential_kitchenware_change] changed cur_kitchenware from " +
                          str(self.cur_kitchenware) + " to " + str(kb_row[db.KitchenwareI.DEFAULT]))
                    self.cur_kitchenware = kb_row[db.KitchenwareI.DEFAULT]
                break

    def find_verbs_and_nouns_in_step(self, step):
        num_sentences = 0
        for sentence in step:
            self.initialize_subject_and_verbs(num_sentences, sentence)
            num_sentences += 1

    def initialize_subject_and_verbs(self, num_sentences, sentence):
        i = 0
        self.subjects_in_step[num_sentences] = []
        while i < len(sentence):
            token = sentence[i]
            token_text = token.lemma_.lower()

            if is_verb_or_pronoun(token) and token_text not in self.verbs_in_step:
                self.verbs_in_step.append(token_text)
            elif token.pos_ == "NOUN":
                compound_noun = str(token_text + " " + sentence[i + 1].lemma_.lower())
                if token.dep_ == "compound" and compound_noun not in self.subjects_in_step:
                    self.subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 1].lemma_.lower())
                    self.subjects_in_step[num_sentences].append(sentence[i + 1].lemma_.lower())
                    i += 1
                elif token_text not in self.subjects_in_step:
                    self.subjects_in_step[num_sentences].append(token_text)
            elif is_small_medium_or_large(token_text):
                if is_size_bowl(sentence, i + 1):
                    self.subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 1].lemma_.lower())
                    i += 1
                elif is_size_bowl(sentence, i + 2):
                    self.subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 2].lemma_.lower())
                    i += 2
                elif is_size_bowl(sentence, i + 3):
                    self.subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 3].lemma_.lower())
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

            if (tool[db.ToolI.DIRECT_VERB] is not None
                    and verb in tool[db.ToolI.DIRECT_VERB].split(", ")
                    and kitchenware_is_appropriate):
                print("[find_tool] added " + tool[db.ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            elif (tool[db.ToolI.AMBIGUOUS_VERB] is not None
                    and verb in tool[db.ToolI.AMBIGUOUS_VERB].split(", ")
                    and kitchenware_is_appropriate
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[db.ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            elif (tool[db.ToolI.IMPLIED] is not None
                    and verb in tool[db.ToolI.IMPLIED].split(", ")
                    and kitchenware_is_appropriate
                    and self.is_implied_tool_applicable(tool)
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[db.ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

    def is_implied_tool_applicable(self, tool):
        print("[is_implied_tool_applicable] verbs: " + str(self.verbs_in_step))

        if tool[db.ToolI.AMBIGUOUS_VERB] is not None:
            for ambiguous_verb in tool[db.ToolI.AMBIGUOUS_VERB].split(", "):
                for verb in self.verbs_in_step:
                    if ambiguous_verb == verb:
                        print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " equals " + ambiguous_verb)
                        return False
        elif tool[db.ToolI.DIRECT_VERB] is not None:
            for direct_verb in tool[db.ToolI.DIRECT_VERB].split(", "):
                for verb in self.verbs_in_step:
                    if direct_verb == verb:
                        print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " equals " + direct_verb)
                        return False
        print("[is_implied_tool_applicable]RETURN TRUE")
        return True

    def is_kitchenware_appropriate(self, tool):
        return tool[db.ToolI.KITCHENWARE] is None or self.cur_kitchenware in tool[db.ToolI.KITCHENWARE].split(" | ")

    def append_tool_to_list(self, tool):
        if not (tool[db.ToolI.TOOL] in self.tools):
            self.tools.append(tool[db.ToolI.TOOL])
        self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += "(" + str(self.tools.index(tool[db.ToolI.TOOL])) + ") "

    def check_tools_definition(self, tool, recipe, sentence_num):
        if tool[db.ToolI.DEFINE] is None:
            return True
        definitions = tool[db.ToolI.DEFINE].split(" | ")
        print("[check_tools_definition] found tool " + tool[db.ToolI.TOOL] + " checking " + str(definitions))

        for definition in definitions:
            print("in loop. Checking: " + str(definition) + " for " + str(tool[db.ToolI.TOOL]))
            if " & " in definition and self.all_definitions_hold(tool, definition.split(" & "), recipe, sentence_num):
                print("[check_tools_definition] All definitions in conjunction hold. Returning True")
                return True
            elif self.is_tool_suitable(tool, definition, recipe, sentence_num):
                print("[check_tools_definition] in elif. Returning True")
                return True
        print("[check_tools_definition] returning False")
        return False

    def all_definitions_hold(self, tool, conjunction_def_list, recipe, sentence_in_step):
        print("[all_definitions_hold] FOUND CONJUNCTION DEFINITION" + str(conjunction_def_list))
        for conjunction_def in conjunction_def_list:
            print("CONJUNCTION ITERATION: " + str(conjunction_def))
            if not self.is_tool_suitable(tool, conjunction_def, recipe, sentence_in_step):
                return False
        return True

    def is_tool_suitable(self, tool, definition, entire_recipe, sentence_in_step):
        definition = definition.strip()
        print("|" + str(definition) + "|")
        print("[is_tool_suitable] tool: " + str(tool[db.ToolI.TOOL]) + ", checking the following: ")
        if definition == "title":
            print("[is_tool_suitable] title")
            return check_title(tool[db.ToolI.TITLE].split(" | "), entire_recipe[db.RecipeI.TITLE].lower())
        elif definition == "isa":
            print("[is_tool_suitable] ISA")
            return match_to_concept_net(tool, db.ToolI.ISA, self.subjects_in_step, -1, False)
        elif definition == "not_isa":
            print("[is_tool_suitable] NOT_ISA")
            return match_to_concept_net(tool, db.ToolI.NOT_ISA, self.subjects_in_step, -1, True)
        elif definition == "isa s":
            print("[is_tool_suitable] ISA S")
            return match_to_concept_net(tool, db.ToolI.ISA, self.subjects_in_step, sentence_in_step, False)
        elif definition == "not_isa s":
            print("[is_tool_suitable] NOT_ISA S")
            return match_to_concept_net(tool, db.ToolI.NOT_ISA, self.subjects_in_step, sentence_in_step, True)
        elif definition == "subject":
            print("[is_tool_suitable] SUBJECT")
            return match_definition_to_recipe(tool, db.ToolI.SUBJECT, self.subjects_in_step)
        elif definition == "not_subject":
            print("[is_tool_suitable] not_subject")
            return not match_definition_to_recipe(tool, db.ToolI.NOT_SUBJECT, self.subjects_in_step)
        elif definition == "size":
            print("[is_tool_suitable] size")
            return match_definition_to_ingredient(tool, db.ToolI.SIZE, self.verbs_in_ingredient)
        elif definition == "not_size":
            print("[is_tool_suitable] not_size")
            return not match_definition_to_ingredient(tool, db.ToolI.NOT_SIZE, self.verbs_in_ingredient)
        elif definition == "ingredient":
            print("[is_tool_suitable] ingredient")
            return match_definition_to_ingredient(tool, db.ToolI.INGREDIENT, self.foods_in_ingredient)
        elif definition == "not_ingredient":
            print("[is_tool_suitable] not_ingredient")
            return not match_definition_to_ingredient(tool, db.ToolI.NOT_INGREDIENT, self.foods_in_ingredient)
        print("[is_tool_suitable] nothing matched so returning FALSE")
        return False
