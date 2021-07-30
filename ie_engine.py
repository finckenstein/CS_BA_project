#!/usr/bin/env python3
import spacy

from alias_functions import string_to_dictionary
from alias_functions import is_verb_or_pronoun

from check_definitions import check_title
from check_definitions import match_definition_to_ingredient
from check_definitions import match_definition_to_recipe
from check_definitions import match_definition_to_relations

from sync import SyncingTextWithVideo
from output import Output

import database_query as db
from kitchenware import Kitchenware
from step import Step
from collections import Counter


def highest_occurrence(kt_list):
    occurrence_dic = Counter(kt_list)
    print("[highest_occurrence] ", occurrence_dic)
    max_val = (None, 0)
    for key in occurrence_dic:
        if occurrence_dic[key] >= max_val[1]:
            max_val = (key, occurrence_dic[key])
    return max_val[0]


def fetch_remaining_words(dictionary, key):
    word_count = 0
    for k in dictionary:
        if k == key:
            for sentences in dictionary[k]:
                words_in_step = sentences.split(" ")
                word_count += len(words_in_step)
    return word_count


class IEEngine:
    def __init__(self):
        self.entire_tool_kb = db.sql_fetch_tools_db()
        self.kt_obj = Kitchenware(db.sql_fetch_kitchenware_db())
        self.step = None
        self.foods_in_ingredient = []
        print("\n\n\n", self.kt_obj.kitchenware, "\n\n\n")

        self.cv_identified_kt = []
        self.txt_identified_kt = []

        all_data = []

        recipe_rows = db.sql_fetch_1to1_videos("https://tasty.co/recipe/orange-cauliflower-chicken")
        for recipe in recipe_rows:
            self.output = Output()
            self.sync = SyncingTextWithVideo(recipe)
            self.foods_in_ingredient = recipe[db.RecipeI.INGREDIENTS]
            self.parse_recipe(recipe)
            all_data.append({'URL': recipe[db.RecipeI.URL],
                             'Preparation': self.output.edited_recipe,
                             'Tools': self.output.tools})

        print("\n\n", all_data[0]['Preparation'], all_data[0]['Tools'])
        # write_to_csv(all_data)

    def parse_recipe(self, recipe):
        nlp = spacy.load('en_core_web_trf')
        dictionary = string_to_dictionary(recipe[db.RecipeI.PREPARATION])
        print("\n\n", dictionary)
        for key in dictionary:
            self.output.edited_recipe += str(key) + ") "
            step = nlp(dictionary[key])
            sentences = list(step.sents)
            self.step = Step(sentences)

            print("\n\n", key, dictionary[key])
            num_sentence = 0
            for sentence in sentences:

                print("all CV detected: ", self.cv_identified_kt)
                print("all TXT detected", self.kt_obj.cur_kitchenware)

                cv_detected = highest_occurrence(self.cv_identified_kt)
                txt_detected = highest_occurrence(self.txt_identified_kt)

                print("most common cv_detected: ", cv_detected)
                print("most common txt_detected: ", txt_detected)

                if not self.sync.wait and cv_detected != txt_detected:
                    self.sync.wait = True
                elif self.sync.wait and cv_detected == txt_detected:
                    self.sync.wait = False
                    self.sync.reset_words_per_minute(fetch_remaining_words(dictionary, key))
                    self.cv_identified_kt = []
                else:
                    self.cv_identified_kt = []

                self.txt_identified_kt = []

                self.analyse_recipe_sentence(sentence, recipe, num_sentence)
                num_sentence += 1

    def analyse_recipe_sentence(self, sentence, recipe, num_sentence):
        self.kt_obj.find_kitchenware(self.step.subjects[num_sentence])
        index = 0
        explicitly_stated = False
        implicitly_stated = False
        while index < len(sentence):
            token = sentence[index]
            token_text = token.lemma_.lower()
            self.output.append_token_to_text(token)

            print("Current word: ", token)

            if is_verb_or_pronoun(token) and token.dep_ == "amod":
                index += 1
                continue
            elif is_verb_or_pronoun(token):
                # print("VERB: " + token_text)
                if self.kt_obj.check_verb_to_verify_implied_kitchenware(token_text):
                    implicitly_stated = True
                self.find_tool_that_corresponds_to_verb(recipe, token_text, num_sentence)

            if self.kt_obj.check_explicit_change_in_kitchenware(token, token_text, sentence, index):
                explicitly_stated = True

            index += self.output.check_for_bowl(token_text, sentence, index)

            text_kitchenware = self.kt_obj.convert_txt_kt_to_cv_kt(self.sync.detectable_kt, self.sync.unsupported_kt)
            self.txt_identified_kt.append(text_kitchenware)
            print("[analyse_recipe_sentence] self.kitchen_obj.cur_kitchenware: ", self.kt_obj.cur_kitchenware)
            print("which is equivalent to : ", text_kitchenware)
            print("explicitly_stated: ", explicitly_stated)
            print("explicitly_stated: ", implicitly_stated)
            print("self.sync.wait: ", self.sync.wait)

            if not self.sync.wait and token.pos_ != "PUNCT" and token.pos_ != "NUM":
                cv_kitchenware = self.sync.get_cv_detected_kitchenware()
                if cv_kitchenware is None:
                    print("cv_kitchenware is None. Continue.\n")
                    continue

                cv_kitchenware = cv_kitchenware.replace("-", " ")
                self.cv_identified_kt.append(cv_kitchenware)
                print("[analyse_recipe_sentence] cv_kitchenware: ", cv_kitchenware)

                if (text_kitchenware is not None
                        and cv_kitchenware != text_kitchenware
                        and not (explicitly_stated or implicitly_stated)):
                    print("[analyse_recipe_sentence] CV corrected text. Changed kitchenware:")
                    print("from: ", text_kitchenware, " to: ", cv_kitchenware)
                    self.kt_obj.cur_kitchenware = cv_kitchenware
                else:
                    print("No change to self.kitchen_obj.cur_kitchenware")
            print("Checking next word\n\n")

    def find_tool_that_corresponds_to_verb(self, recipe, verb, sentence_in_step):
        for tool in self.entire_tool_kb:
            kitchenware_is_appropriate = self.kt_obj.is_kitchenware_appropriate(tool)

            if (tool[db.ToolI.DIRECT_VERB] is not None
                    and verb in tool[db.ToolI.DIRECT_VERB].split(", ")
                    and kitchenware_is_appropriate):
                self.output.append_tool_to_list(tool, db.ToolI.TOOL)

            elif (tool[db.ToolI.AMBIGUOUS_VERB] is not None
                  and verb in tool[db.ToolI.AMBIGUOUS_VERB].split(", ")
                  and kitchenware_is_appropriate
                  and self.check_tools_definition(tool, recipe, sentence_in_step)):
                self.output.append_tool_to_list(tool, db.ToolI.TOOL)

            elif (tool[db.ToolI.IMPLIED] is not None
                  and verb in tool[db.ToolI.IMPLIED].split(", ")
                  and kitchenware_is_appropriate
                  and self.is_implied_tool_applicable(tool)
                  and self.check_tools_definition(tool, recipe, sentence_in_step)):
                self.output.append_tool_to_list(tool, db.ToolI.TOOL)

    def is_implied_tool_applicable(self, tool):
        # print("[is_implied_tool_applicable] verbs: " + str(self.step.verbs))

        if (tool[db.ToolI.AMBIGUOUS_VERB] is not None
                and not self.will_tool_be_covered(tool[db.ToolI.AMBIGUOUS_VERB].split(", "))):
            # print("[is_implied_tool_applicable]RETURN FALSE")
            return False
        elif (tool[db.ToolI.DIRECT_VERB] is not None
              and not self.will_tool_be_covered(tool[db.ToolI.DIRECT_VERB].split(", "))):
            # print("[is_implied_tool_applicable]RETURN FALSE")
            return False
        else:
            # print("[is_implied_tool_applicable]RETURN TRUE")
            return True

    def will_tool_be_covered(self, verbs):
        for verb in verbs:
            if verb in self.step.verbs:
                # print("[will_tool_be_covered]RETURN FALSE BECAUSE " + verb + " is in " + str(self.step.verbs))
                return False
        return True

    def check_tools_definition(self, tool, recipe, sentence_num):
        if tool[db.ToolI.DEFINE] is None:
            return True

        definitions = tool[db.ToolI.DEFINE].split(" | ")
        # print("[check_tools_definition] found tool " + tool[db.ToolI.TOOL] + " checking " + str(definitions))

        for definition in definitions:
            # print("in loop. Checking: " + str(definition) + " for " + str(tool[db.ToolI.TOOL]))
            if " & " in definition and self.all_definitions_hold(tool, definition.split(" & "), recipe, sentence_num):
                # print("[check_tools_definition] All definitions in conjunction hold. Returning True")
                return True
            elif " & " not in definition and self.is_tool_suitable(tool, definition, recipe, sentence_num):
                # print("[check_tools_definition] in elif. Returning True")
                return True
        # print("[check_tools_definition] returning False")
        return False

    def all_definitions_hold(self, tool, conjunction_def_list, recipe, sentence_in_step):
        # print("[all_definitions_hold] FOUND CONJUNCTION DEFINITION" + str(conjunction_def_list))
        for conjunction_def in conjunction_def_list:
            # print("CONJUNCTION ITERATION: " + str(conjunction_def))
            if not self.is_tool_suitable(tool, conjunction_def, recipe, sentence_in_step):
                return False
        return True

    # TODO: self.foods_in_ingredient is not longer a dictionary. Its now a tuple received from DB
    def is_tool_suitable(self, tool, definition, entire_recipe, sentence_key):
        definition = definition.strip()
        # print("[is_tool_suitable] tool: " + str(tool[db.ToolI.TOOL]) + ", checking the following: " + str(definition))

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
