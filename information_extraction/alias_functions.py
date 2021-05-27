import ast
import csv


def string_to_dictionary(prep_str):
    return ast.literal_eval(prep_str)


def write_to_csv(data):
    fields = ['URL', 'Preparation', 'Utils']
    filename = "found_utils.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def check_title(tool_title_list, recipe_title):
    print("[check_title] current title: " + str(recipe_title))
    for curr_tool_title in tool_title_list:
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
    print("[match_definition_to_ingredient] RETURN FALSE BECAUSE " + str(tool[index].split(" | ")) + " NOT IN " + str(
        ingredient_list))
    return False


def is_size_bowl(sentence, offset):
    return offset < len(sentence) - 1 and "bowl" in sentence[offset].text.lower()


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_small_medium_or_large(token_text):
    return token_text == "small" or token_text == "medium" or token_text == "large"
