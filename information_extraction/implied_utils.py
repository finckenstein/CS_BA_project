#!/usr/bin/env python3
import ast
import spacy
import csv
from database_query import ToolI
from database_query import RecipeI
from database_query import KitchenwareI
from database_query import sql_fetch_recipe_db
from database_query import sql_fetch_tools_db
from database_query import sql_fetch_kitchenware_db
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
    print("[check_title] current title: " + str(recipe_title))
    for curr_tool_title in tool[ToolI.TITLE].split(" | "):
        print("[check_title] tool:" + str(curr_tool_title))
        if str(curr_tool_title) in str(recipe_title):
            return True
    return False


def match_definition_to_recipe(tool, index, subjects_in_step):
    for subject in tool[index].split(" | "):
        if " & " in subject:
            counter = 0
            conj_concept_list = subject.split(" & ")
            for conj_subject in conj_concept_list:
                for key in subjects_in_step:
                    for subject_target in subjects_in_step[key]:
                        if subject_target == conj_subject:
                            counter += 1
            if counter == len(conj_concept_list):
                print("[match_definition_to_recipe] RETURN TRUE because counter equals conjunction def")
                return True
        else:
            for key in subjects_in_step:
                for subject_target in subjects_in_step[key]:
                    if subject_target == subject:
                        print("[match_definition_to_recipe] RETURN TRUE")
                        return True
    print("[match_definition_to_recipe] RETURN FALSE BECAUSE " + str(tool[index].split(" | ")) + " NOT IN " + str(
        subjects_in_step))
    return False


def match_definition_to_ingredient(tool, index, ingredient_list):
    print("[match_definition_to_ingredient] ingredient list: " + str(ingredient_list))
    print("[match_definition_to_ingredient] tool: " + str(tool[ToolI.TOOL]))
    for keyword in tool[index].split(" | "):
        print("keyword from tool " + str(keyword))
        if " & " in keyword:
            conj_counter = 0
            conj_keyword_list = keyword.split(" & ")
            for conj_keyword in conj_keyword_list:
                for ingredient in ingredient_list:
                    if ingredient == conj_keyword:
                        print("[match_definition_to_ingredient] increase counter because " + str(
                            ingredient) + " is equal to " + str(conj_keyword))
                        conj_counter += 1
            if conj_counter == len(conj_keyword_list):
                print("[match_definition_to_ingredient] return True because counter equals length of conjunction def")
                return True
        else:
            for ingredient in ingredient_list:
                if ingredient == keyword:
                    print("[match_definition_to_ingredient] RETURN TRUE because " + str(
                        ingredient) + " is equal to " + str(keyword))
                    return True
    print("[match_definition_to_ingredient] RETURN FALSE")
    return False


def match_definition_to_concept_net(tool, index, subjects_to_match, just_sentence):
    for concept in tool[index].split(" | "):
        if "&" in concept:
            conj_concept_list = concept.split(" & ")
            all_concepts_true = True
            for conj_concept in conj_concept_list:
                if not concept_found_concept_net(conj_concept, subjects_to_match, just_sentence):
                    all_concepts_true = False
                    break
            if all_concepts_true:
                return True
        else:
            if concept_found_concept_net(concept, subjects_to_match, just_sentence):
                return True
    return False


class FindImpliedTools:
    def __init__(self):
        self.entire_tool_kb = sql_fetch_tools_db()
        self.entire_kitchenware_kb = sql_fetch_kitchenware_db()
        recipe_rows = sql_fetch_recipe_db()
        self.nlp = spacy.load('en_core_web_trf')

        self.cur_kitchenware = None
        self.kitchenware = []
        self.initialize_kitchenware_array()
        print(self.kitchenware)

        self.edited_recipe = ""
        self.tools = []
        self.verbs_in_step = []
        self.verbs_in_ingredient = []
        self.nouns_in_ingredient = []
        self.subjects_in_step = {}

        all_data = []

        for recipe in recipe_rows:
            self.parse_ingredients(recipe[RecipeI.INGREDIENTS])
            self.parse_recipe(recipe)
            dic = {'URL': recipe[RecipeI.URL], 'Preparation': self.edited_recipe, 'Utils': self.tools}
            all_data.append(dic)

            self.verbs_in_ingredient = []
            self.nouns_in_ingredient = []
            self.tools = []
            self.edited_recipe = ""

        print(all_data)
        # write_to_csv(all_data)

    def initialize_kitchenware_array(self):
        for row in self.entire_kitchenware_kb:
            for kitchenware in row[KitchenwareI.KITCHENWARE].split(", "):
                if kitchenware not in self.kitchenware:
                    self.kitchenware.append(kitchenware)

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
        dictionary = string_to_dictionary(recipe[RecipeI.PREPARATION])
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
                self.find_kitchenware(num_sentence)
                print("[parse_preparation] current kitchenware: " + str(self.cur_kitchenware))
                index = 0
                while index < len(sentence):
                    token = sentence[index]
                    if token.pos_ == "PUNCT":
                        self.edited_recipe = self.edited_recipe[:-1]
                    self.edited_recipe += str(token.text) + " "
                    if token.pos_ == "VERB" or token.pos_ == "PRON":
                        if token.dep_ == "amod":
                            index += 1
                            continue
                        verb = token.lemma_.lower()
                        print("VERB: " + verb)
                        self.check_potential_kitchenware_change(verb)
                        self.find_tool_that_corresponds_to_verb(recipe, verb, num_sentence)
                    elif token.pos_ == "NOUN":
                        if token.dep_ == "compound":
                            self.match_noun_to_kitchenware(token.text.lower() + " " + sentence[index + 1].text.lower())
                        else:
                            self.match_noun_to_kitchenware(token.text.lower())
                    elif token.pos_ == "ADJ":
                        if (token.text.lower() == "large"
                                or token.text.lower() == "medium"
                                or token.text.lower() == "small"):
                            if sentence[index + 1].text.lower() == "bowl":
                                print("FOUND: " + token.text.lower() + sentence[index + 1].text.lower())
                                self.match_noun_to_kitchenware(token.text.lower() + " " + sentence[index+1].text.lower())
                                index += 1
                                self.edited_recipe += str(sentence[index].text) + " "
                            elif sentence[index + 2].text.lower() == "bowl":
                                print("FOUND: " + token.text.lower() + sentence[index + 2].text.lower())
                                self.match_noun_to_kitchenware(token.text.lower() + " " + sentence[index+2].text.lower())
                                index += 2
                                self.edited_recipe += str(sentence[index-1].text) + " " + str(sentence[index].text)
                    index += 1
                num_sentence += 1

            self.subjects_in_step = {}
            self.verbs_in_step = []

    def match_noun_to_kitchenware(self, noun):
        if not noun == self.cur_kitchenware and noun in self.kitchenware:
            print("[match_noun_to_kitchenware] changed kitchenware from " + self.cur_kitchenware + " to " + noun)
            self.cur_kitchenware = noun

    def check_potential_kitchenware_change(self, verb):
        for row in self.entire_kitchenware_kb:
            if row[KitchenwareI.VERB] == verb:
                if (self.cur_kitchenware is None
                        or self.cur_kitchenware not in row[KitchenwareI.KITCHENWARE]):
                    print("[check_potential_kitchenware_change] changed cur_kitchenware from " +
                          str(self.cur_kitchenware) + " to " + str(row[KitchenwareI.DEFAULT]))
                    self.cur_kitchenware = row[KitchenwareI.DEFAULT]
                break

    def find_verbs_and_nouns_in_step(self, step):
        num_sentences = 0
        for sentence in step:
            self.find_verbs_and_nouns_in_sentence(num_sentences, sentence)
            num_sentences += 1

    def find_verbs_and_nouns_in_sentence(self, num_sentences, sentence):
        i = 0
        self.subjects_in_step[num_sentences] = []
        while i < len(sentence):
            # print("[find_verbs_and_nouns_in_sentence]" + str(sentence[i].lemma_.lower()))
            if (sentence[i].pos_ == "VERB" or sentence[i].pos_ == "PRON"
                    and not sentence[i].lemma_.lower() in self.verbs_in_step):
                self.verbs_in_step.append(sentence[i].lemma_.lower())
            if sentence[i].pos_ == "NOUN":
                if (sentence[i].dep_ == "compound"
                        and not str(sentence[i].lemma_.lower() + " " + sentence[
                            i + 1].lemma_.lower()) in self.subjects_in_step):
                    self.subjects_in_step[num_sentences].append(
                        sentence[i].lemma_.lower() + " " + sentence[i + 1].lemma_.lower())
                    self.subjects_in_step[num_sentences].append(sentence[i + 1].lemma_.lower())
                    i += 1
                elif (sentence[i].dep_ == "nsubj"
                      or sentence[i].dep_ == "dobj"
                      or sentence[i].dep_ == "pobj"
                      or sentence[i].dep_ == "conj"
                      and not sentence[i].lemma_.lower() in self.subjects_in_step):
                    self.subjects_in_step[num_sentences].append(sentence[i].lemma_.lower())
            elif (sentence[i].lemma_.lower() == "small"
                  or sentence[i].lemma_.lower() == "medium"
                  or sentence[i].lemma_.lower() == "large"):
                if i + 1 < len(sentence) - 1 and "bowl" in sentence[i + 1].text.lower():
                    self.subjects_in_step[num_sentences].append(
                        sentence[i].lemma_.lower() + " " + sentence[i + 1].lemma_.lower())
                    i += 1
                elif i + 2 < len(sentence) - 1 and "bowl" in sentence[i + 2].text.lower():
                    self.subjects_in_step[num_sentences].append(
                        sentence[i].lemma_.lower() + " " + sentence[i + 2].lemma_.lower())
                    i += 2
                elif i + 3 < len(sentence) - 1 and "bowl" in sentence[i + 3].text.lower():
                    self.subjects_in_step[num_sentences].append(
                        sentence[i].lemma_.lower() + " " + sentence[i + 3].lemma_.lower())
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

            if (tool[ToolI.DIRECT_VERB] is not None
                    and verb in tool[ToolI.DIRECT_VERB].split(", ")
                    and kitchenware_is_appropriate):
                print("[find_tool] added " + tool[ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            if (tool[ToolI.AMBIGUOUS_VERB] is not None
                    and verb in tool[ToolI.AMBIGUOUS_VERB].split(", ")
                    and kitchenware_is_appropriate
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

            if (tool[ToolI.IMPLIED] is not None
                    and verb in tool[ToolI.IMPLIED].split(", ")
                    and kitchenware_is_appropriate
                    and self.is_implied_tool_applicable(tool)
                    and self.check_tools_definition(tool, recipe, sentence_in_step)):
                print("[find_tool] added " + tool[ToolI.TOOL] + " because of " + verb + "\n\n")
                self.append_tool_to_list(tool)

    def append_tool_to_list(self, tool):
        if not (tool[ToolI.TOOL] in self.tools):
            self.tools.append(tool[ToolI.TOOL])
        self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += "(" + str(self.tools.index(tool[ToolI.TOOL])) + ") "

    def is_implied_tool_applicable(self, tool):
        print("[is_implied_tool_applicable] verbs: " + str(self.verbs_in_step))

        if tool[ToolI.AMBIGUOUS_VERB] is not None:
            for ambiguous_verb in tool[ToolI.AMBIGUOUS_VERB].split(", "):
                for verb in self.verbs_in_step:
                    if ambiguous_verb == verb:
                        print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " equals " + ambiguous_verb)
                        return False
        if tool[ToolI.DIRECT_VERB] is not None:
            for direct_verb in tool[ToolI.DIRECT_VERB].split(", "):
                for verb in self.verbs_in_step:
                    if direct_verb == verb:
                        print("[is_implied_tool_applicable]RETURN FALSE BECAUSE " + verb + " equals " + direct_verb)
                        return False
        print("[is_implied_tool_applicable]RETURN TRUE")
        return True

    def is_kitchenware_appropriate(self, tool):
        return tool[ToolI.KITCHENWARE] is None or self.cur_kitchenware in tool[ToolI.KITCHENWARE].split(" | ")

    def check_tools_definition(self, tool, recipe, sentence_in_step):
        if tool[ToolI.DEFINE] is None:
            return True
        definitions = tool[ToolI.DEFINE].split(" | ")
        print("[check_tools_definition] found tool " + tool[ToolI.TOOL] + " checking " + str(definitions))

        for definition in definitions:
            print("in loop. Checking: " + str(definition) + " for " + str(tool[ToolI.TOOL]))
            if " & " in definition:
                conjunction_def_list = definition.split(" & ")
                print("[check_tools_definition] FOUND CONJUNCTION DEFINITION" + str(conjunction_def_list))
                all_definitions_hold = True
                for conjunction_def in conjunction_def_list:
                    print("CONJUNCTION ITERATION: " + str(conjunction_def))
                    if not self.is_tool_suitable(tool, conjunction_def, recipe, sentence_in_step):
                        all_definitions_hold = False
                        break
                if all_definitions_hold:
                    return True
            else:
                tool_suitable = self.is_tool_suitable(tool, definition, recipe, sentence_in_step)
                print("[check_tools_definition] in else. is_tool_suitable returned: " + str(tool_suitable))
                if tool_suitable:
                    return True
        print("[check_tools_definition] returning False")
        return False

    def is_tool_suitable(self, tool, definition, entire_recipe, sentence_in_step):
        definition = definition.strip()
        print("|" + str(definition) + "|")
        if definition == "title":
            print("[is_tool_suitable] title")
            return check_title(tool, entire_recipe[RecipeI.TITLE].lower())
        elif definition == "isa":
            print("[is_tool_suitable] ISA")
            return match_definition_to_concept_net(tool, ToolI.ISA, self.subjects_in_step, False)
        elif definition == "not_isa":
            print("[is_tool_suitable] NOT_ISA")
            return not match_definition_to_concept_net(tool, ToolI.NOT_ISA, self.subjects_in_step, False)
        elif definition == "isa s":
            print("[is_tool_suitable] ISA S")
            return match_definition_to_concept_net(tool, ToolI.ISA, self.subjects_in_step[sentence_in_step], True)
        elif definition == "not_isa s":
            print("[is_tool_suitable] NOT_ISA S")
            return match_definition_to_concept_net(tool, ToolI.NOT_ISA, self.subjects_in_step[sentence_in_step], True)
        elif definition == "subject":
            print("[is_tool_suitable] SUBJECT")
            return match_definition_to_recipe(tool, ToolI.SUBJECT, self.subjects_in_step)
        elif definition == "not_subject":
            print("[is_tool_suitable] not_subject")
            return not match_definition_to_recipe(tool, ToolI.NOT_SUBJECT, self.subjects_in_step)
        elif definition == "size":
            print("[is_tool_suitable] size")
            return match_definition_to_ingredient(tool, ToolI.SIZE, self.verbs_in_ingredient)
        elif definition == "not_size":
            print("[is_tool_suitable] not_size")
            return not match_definition_to_ingredient(tool, ToolI.NOT_SIZE, self.verbs_in_ingredient)
        elif definition == "ingredient":
            print("[is_tool_suitable] ingredient")
            return match_definition_to_ingredient(tool, ToolI.INGREDIENT, self.nouns_in_ingredient)
        elif definition == "not_ingredient":
            print("[is_tool_suitable] not_ingredient")
            return not match_definition_to_ingredient(tool, ToolI.NOT_INGREDIENT, self.nouns_in_ingredient)
        print("[is_tool_suitable] nothing matched so returning FALSE")
        return False
