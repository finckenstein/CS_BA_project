from alias_functions import is_small_medium_or_large
from alias_functions import is_size_bowl


class Output:
    def __init__(self):
        self.edited_recipe = ""
        self.tools = []

    def check_for_bowl(self, token_text, sentence, index):
        increment = 0
        if is_small_medium_or_large(token_text):
            if is_size_bowl(sentence, index + 1):
                increment += 1
                self.edited_recipe += str(sentence[index + 1].text) + " "
            elif is_size_bowl(sentence, index + 2):
                increment += 2
                self.edited_recipe += (str(sentence[index + 1].text) + " " + str(sentence[index + 2].text))
            elif is_size_bowl(sentence, index + 3):
                increment += 3
                self.edited_recipe += (str(sentence[index + 1].text) + " "
                                       + str(sentence[index + 2].text) + " "
                                       + str(sentence[index + 3].text))
        return increment + 1

    def append_token_to_text(self, token):
        if token.pos_ == "PUNCT":
            self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += str(token.text) + " "

    def insert_label(self, tool):
        self.edited_recipe = self.edited_recipe[:-1]
        self.edited_recipe += "(" + tool + ") "

    def append_tool_to_list(self, tool, tool_index):
        if tool[tool_index] not in self.tools:
            self.tools.append(tool[tool_index])

        self.insert_label(str(self.tools.index(tool[tool_index])))
