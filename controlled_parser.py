#!/usr/bin/env python3
import spacy

from alias_functions import string_to_dictionary
from alias_functions import check_title
from alias_functions import match_definition_to_relations
from alias_functions import match_definition_to_recipe
from alias_functions import match_definition_to_ingredient
from alias_functions import is_size_bowl
from alias_functions import is_verb_or_pronoun
from alias_functions import is_small_medium_or_large

from sync import SyncingTextWithVideo

import database_query as db
from kitchenware import Kitchenware
from step import Step


class Parser:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_trf')
        self.entire_tool_kb = db.sql_fetch_tools_db()

        self.kitchen_obj = Kitchenware(db.sql_fetch_kitchenware_db())
        self.step = None

        self.foods_in_ingredient = []
        self.tools = []
        self.edited_recipe = ""

        all_data = []

        recipe_rows = db.sql_fetch_1to1_videos("https://tasty.co/recipe/cashew-chicken-stir-fry")
        for recipe in recipe_rows:
            self.sync = SyncingTextWithVideo(recipe)
            self.foods_in_ingredient = recipe[db.RecipeI.INGREDIENTS]
            self.parse_recipe(recipe)

            dic = {'URL': recipe[db.RecipeI.URL], 'Preparation': self.edited_recipe, 'Utils': self.tools}
            all_data.append(dic)

            self.reset_variables()

        print(all_data)
        # write_to_csv(all_data)

    def reset_variables(self):
        self.foods_in_ingredient = []
        self.tools = []
        self.edited_recipe = ""

    def parse_recipe(self, recipe):
        dictionary = string_to_dictionary(recipe[db.RecipeI.PREPARATION])
        for key in dictionary:
            self.edited_recipe += str(key) + ") "
            step = self.nlp(dictionary[key])
            sentences = list(step.sents)
            self.step = Step(sentences)

            print("\n\n", key, dictionary[key])
            num_sentence = 0
            for sentence in sentences:
                self.analyse_recipe_sentence(sentence, recipe, num_sentence)
                num_sentence += 1

    def analyse_recipe_sentence(self, sentence, recipe, num_sentence):
        self.kitchen_obj.find_kitchenware(self.step.subjects[num_sentence])
        index = 0
        while index < len(sentence):
            token = sentence[index]
            token_text = token.lemma_.lower()
            self.handle_punctuation_in_output_text(token)

            if is_verb_or_pronoun(token) and token.dep_ == "amod":
                index += 1
                continue
            elif is_verb_or_pronoun(token):
                print("VERB: " + token_text)
                self.kitchen_obj.check_verb_to_verify_implied_kitchenware(token_text)
                self.find_tool_that_corresponds_to_verb(recipe, token_text, num_sentence)

            index = self.check_explicit_change_in_kitchenware(token, token_text, sentence, index)

            cv_kitchenware = self.sync.get_cv_detected_kitchenware()

            # TODO: compare cv_kitchenware to kitchenware stored in self.cur_kitchenware
            if cv_kitchenware is None:
                print("\n\nWords_per_frame is not == counter")
            else:
                print("\n\n\n\nCV DETECTED KITCHENWARE: ", cv_kitchenware)

    def found_bowl(self, bowl, index, increment, sentence):
        print("FOUND BOWL: " + bowl)
        self.kitchen_obj.match_noun_to_kitchenware(bowl)
        index += increment
        next_w = str(sentence[index].text)
        if increment == 1:
            self.edited_recipe += next_w + " "
        elif increment == 2:
            self.edited_recipe += (str(sentence[index - 1].text) + " " + next_w)
        elif increment == 3:
            self.edited_recipe += (str(sentence[index - 2].text) + " " + str(sentence[index - 1].text) + " " + next_w)
        return index

    # TODO: i think this function should be in kitchenware.py file
    def check_explicit_change_in_kitchenware(self, token, token_text, sentence, index):
        if token.pos_ == "NOUN":
            if token.dep_ == "compound":
                self.kitchen_obj.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
            else:
                self.kitchen_obj.match_noun_to_kitchenware(token_text)
        elif is_small_medium_or_large(token_text):
            if is_size_bowl(sentence, index + 1):
                index = self.found_bowl((token_text + " " + sentence[index + 1].text.lower()), index, 1, sentence)
            elif is_size_bowl(sentence, index + 2):
                index = self.found_bowl((token_text + " " + sentence[index + 2].text.lower()), index, 2, sentence)
            elif is_size_bowl(sentence, index + 3):
                index = self.found_bowl((token_text + " " + sentence[index + 3].text.lower()), index, 3, sentence)
        return index + 1

    def handle_punctuation_in_output_text(self, token):
        if token.pos_ == "PUNCT":
            self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += str(token.text) + " "

    def find_tool_that_corresponds_to_verb(self, recipe, verb, sentence_in_step):
        for tool in self.entire_tool_kb:
            kitchenware_is_appropriate = self.kitchen_obj.is_kitchenware_appropriate(tool)

            if (tool[db.ToolI.DIRECT_VERB] is not None
                    and verb in tool[db.ToolI.DIRECT_VERB].split(", ")
                    and kitchenware_is_appropriate):
                self.append_tool_to_list(tool, verb)

            elif (tool[db.ToolI.AMBIGUOUS_VERB] is not None
                  and verb in tool[db.ToolI.AMBIGUOUS_VERB].split(", ")
                  and kitchenware_is_appropriate
                  and self.check_tools_definition(tool, recipe, sentence_in_step)):
                self.append_tool_to_list(tool, verb)

            elif (tool[db.ToolI.IMPLIED] is not None
                  and verb in tool[db.ToolI.IMPLIED].split(", ")
                  and kitchenware_is_appropriate
                  and self.is_implied_tool_applicable(tool)
                  and self.check_tools_definition(tool, recipe, sentence_in_step)):
                self.append_tool_to_list(tool, verb)

    def is_implied_tool_applicable(self, tool):
        print("[is_implied_tool_applicable] verbs: " + str(self.step.verbs))

        if (tool[db.ToolI.AMBIGUOUS_VERB] is not None
                and not self.will_tool_be_covered(tool[db.ToolI.AMBIGUOUS_VERB].split(", "))):
            print("[is_implied_tool_applicable]RETURN FALSE")
            return False
        elif (tool[db.ToolI.DIRECT_VERB] is not None
              and not self.will_tool_be_covered(tool[db.ToolI.DIRECT_VERB].split(", "))):
            print("[is_implied_tool_applicable]RETURN FALSE")
            return False
        else:
            print("[is_implied_tool_applicable]RETURN TRUE")
            return True

    def will_tool_be_covered(self, verbs):
        for verb in verbs:
            if verb in self.step.verbs:
                print("[will_tool_be_covered]RETURN FALSE BECAUSE " + verb + " is in " + str(self.step.verbs))
                return False
        return True

    def append_tool_to_list(self, tool, verb):
        print("[append_tool_to_list] added " + tool[db.ToolI.TOOL] + " because of " + verb + "\n\n")
        if tool[db.ToolI.TOOL] not in self.tools:
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
            elif " & " not in definition and self.is_tool_suitable(tool, definition, recipe, sentence_num):
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

    # TODO: self.foods_in_ingredient is not longer a dictionary. Its now a tuple received from DB
    def is_tool_suitable(self, tool, definition, entire_recipe, sentence_key):
        definition = definition.strip()
        print("[is_tool_suitable] tool: " + str(tool[db.ToolI.TOOL]) + ", checking the following: " + str(definition))

        if definition == "title":
            return check_title(tool[db.ToolI.TITLE].split(" | "), entire_recipe[db.RecipeI.TITLE].lower())

        elif definition == "isa":
            return match_definition_to_relations(tool, db.ToolI.ISA, self.step.foods, -1, False,
                                                 self.foods_in_ingredient)
        elif definition == "not_isa":
            return match_definition_to_relations(tool, db.ToolI.NOT_ISA, self.step.foods, -1, True,
                                                 self.foods_in_ingredient)
        elif definition == "isa s":
            return match_definition_to_relations(tool, db.ToolI.ISA, self.step.foods, sentence_key, False,
                                                 self.foods_in_ingredient)
        elif definition == "not_isa s":
            return match_definition_to_relations(tool, db.ToolI.NOT_ISA, self.step.foods, sentence_key, True,
                                                 self.foods_in_ingredient)
        elif definition == "subject":
            return match_definition_to_recipe(tool, db.ToolI.SUBJECT, self.step.subjects, False)

        elif definition == "not_subject":
            return match_definition_to_recipe(tool, db.ToolI.NOT_SUBJECT, self.step.subjects, True)

        elif definition == "ingredient":
            return match_definition_to_ingredient(tool, db.ToolI.INGREDIENT, self.foods_in_ingredient, False)

        elif definition == "not_ingredient":
            return match_definition_to_ingredient(tool, db.ToolI.NOT_INGREDIENT, self.foods_in_ingredient, True)

        else:
            return False
#         elif definition == "size":
#             return match_definition_to_ingredient(tool, db.ToolI.SIZE, self.foods_in_ingredient, False)
#         elif definition == "not_size":
#             return match_definition_to_ingredient(tool, db.ToolI.NOT_SIZE, self.foods_in_ingredient, True)
