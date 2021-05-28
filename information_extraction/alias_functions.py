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


def find_rel_list_in_dic_within_dic(foods, key):
    temp_rel = []
    for food_key in foods[key]:
        for elem in foods[key][food_key]:
            temp_rel.append(elem)
    return temp_rel


def fetch_relations_for_subjects(foods, key):
    isa_rel = []
    if key == -1:
        for sentence_key in foods:
            isa_rel += find_rel_list_in_dic_within_dic(foods, sentence_key)
    else:
        isa_rel = find_rel_list_in_dic_within_dic(foods, key)

    for rel in isa_rel:
        print(rel)

    return isa_rel


def match_concept_to_edge(concept, subject_isa_rel):
    for relation in subject_isa_rel:
        if str(concept) in relation:
            print("[match_concept_to_edge] return True because " + str(concept) + " in " + relation)
            return True
    print("[match_concept_to_edge] return False")
    return False


def match_definition_to_relations(tool, index, foods_dic, possible_key, negation):
    print(foods_dic)
    isa_rel_list = fetch_relations_for_subjects(foods_dic, possible_key)

    for target_concept in tool[index].split(" | "):
        print("Match current target concept: " + str(target_concept))
        if " & " in target_concept:
            all_true = True
            for conj_target_concept in target_concept.split(" & "):
                print("In conjunction. Checking target concept: " + str(conj_target_concept))
                concept_matches = match_concept_to_edge(conj_target_concept, isa_rel_list)
                if (not concept_matches and not negation) or (concept_matches and negation):
                    print("CONJUNCTION: BREAK OUT OF LOOP")
                    all_true = False
                    break
            if all_true:
                print("CONJUNCTION RETURN TRUE")
                return True
        else:
            concept_matches = match_concept_to_edge(target_concept, isa_rel_list)
            if (not concept_matches and negation) or (concept_matches and not negation):
                print("[match_definition_to_concept_net] IN ELSE RETURNING TRUE")
                return True
    print("[match_definition_to_concept_net] AT THE END. RETURNING FALSE")
    return False


def match_definition_to_recipe(tool, index, subjects_in_step, negation):
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


def match_definition_to_ingredient(tool, index, ingredient_list, negation):
    print("[match_definition_to_ingredient] ingredient list: " + str(ingredient_list))
    for keyword in tool[index].split(" | "):
        print("keyword from tool " + str(keyword))
        if " & " in keyword:
            all_true = True
            for conj_keyword in keyword.split(" & "):
                if ((conj_keyword not in ingredient_list and not negation)
                        or (conj_keyword in ingredient_list and negation)):
                    print("break out of loop because" + str(conj_keyword) + " is or is not in " + str(ingredient_list))
                    all_true = False
                    break
            if all_true:
                print("[match_definition_to_ingredient] in conjunction. All_true so returning True.")
                return True
        elif (keyword not in ingredient_list and negation) or (keyword in ingredient_list and not negation):
            print("[match_definition_to_ingredient] in disjunction. RETURN TRUE")
            return True
    print("[match_definition_to_ingredient] AT THE END. RETURN FALSE")
    return False


def is_size_bowl(sentence, offset):
    return offset < len(sentence) - 1 and "bowl" in sentence[offset].text.lower()


def is_verb_or_pronoun(token):
    return token.pos_ == "VERB" or token.pos_ == "PRON"


def is_small_medium_or_large(token_text):
    return token_text == "small" or token_text == "medium" or token_text == "large"
