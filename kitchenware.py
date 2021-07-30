#!/usr/bin/env python3
from alias_functions import is_size_bowl
from database_query import KitchenwareI
from database_query import ToolI


class Kitchenware:
    def __init__(self, kitchenware_from_db):
        self.entire_kitchenware_kb = kitchenware_from_db
        self.cur_kitchenware = None
        self.kitchenware = []

        for row in self.entire_kitchenware_kb:
            for tmp_kitchenware in row[KitchenwareI.KITCHENWARE].split(", "):
                if tmp_kitchenware not in self.kitchenware:
                    self.kitchenware.append(tmp_kitchenware)

    def find_kitchenware(self, sentence):
        for noun in sentence:
            for tmp_kitchenware in self.kitchenware:
                if noun == tmp_kitchenware:
                    self.cur_kitchenware = noun
        # print("[find_kitchenware] current kitchenware: " + str(self.cur_kitchenware))

    def check_verb_to_verify_implied_kitchenware(self, verb):
        for kb_row in self.entire_kitchenware_kb:
            if kb_row[KitchenwareI.VERB] == verb:
                list_of_kb_kitchenware = kb_row[KitchenwareI.KITCHENWARE].split(", ")
                if self.cur_kitchenware is None or self.cur_kitchenware not in list_of_kb_kitchenware:
                    # print("[check_potential_kitchenware_change] changed cur_kitchenware from " +
                    #       str(self.cur_kitchenware) + " to " + str(kb_row[KitchenwareI.DEFAULT]))
                    self.cur_kitchenware = kb_row[KitchenwareI.DEFAULT]
                    return True
                elif self.cur_kitchenware in list_of_kb_kitchenware:
                    return True
        return False

    def match_noun_to_kitchenware(self, noun):
        if noun in self.kitchenware:
            # print("[match_noun_to_kitchenware] changed kitchenware from " + self.cur_kitchenware + " to " + noun)
            self.cur_kitchenware = noun
            return True
        return False

    def is_kitchenware_appropriate(self, tool):
        return tool[ToolI.KITCHENWARE] is None or self.cur_kitchenware in tool[ToolI.KITCHENWARE].split(" | ")

    def check_explicit_change_in_kitchenware(self, token, token_text, sentence, index):
        if token.pos_ == "NOUN":
            if token.dep_ == "compound":
                return self.match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
            else:
                return self.match_noun_to_kitchenware(token_text)
        elif is_size_bowl(sentence, index + 1):
            return self.match_noun_to_kitchenware((token_text + " " + sentence[index + 1].text.lower()))
        elif is_size_bowl(sentence, index + 2):
            return self.match_noun_to_kitchenware((token_text + " " + sentence[index + 2].text.lower()))
        elif is_size_bowl(sentence, index + 3):
            return self.match_noun_to_kitchenware((token_text + " " + sentence[index + 3].text.lower()))
        return False

    def convert_txt_kt_to_cv_kt(self, detectable_kt, unsupported_kt):
        if self.cur_kitchenware in unsupported_kt:
            return None
        for key in detectable_kt:
            for elem in detectable_kt[key]:
                if self.cur_kitchenware == elem or self.cur_kitchenware == key:
                    return key
