import database_query as db
from alias_functions import string_to_dictionary


def check_title(tool_title_list, recipe_title):
    # print("[check_title] current title: " + str(recipe_title))
    for curr_tool_title in tool_title_list:
        # print("[check_title] tool:" + str(curr_tool_title))
        if str(curr_tool_title) in str(recipe_title):
            return True
    return False


def fetch_keys_from_dic(dic):
    tmp = []
    for elem in dic:
        for key in elem:
            tmp.append(key)
    return tmp


def fetch_relations_for_subjects(foods, key):
    isa_rel = {}
    if key == -1:
        for sentence_key in foods:
            for food_key in foods[sentence_key]:
                isa_rel[food_key] = foods[sentence_key][food_key]
    else:
        for food_key in foods[key]:
            isa_rel[food_key] = foods[key][food_key]
    return isa_rel


def dic_items_to_list(dic):
    temp_list = []
    for key in dic:
        for elem in dic[key]:
            temp_list.append(elem)
    return temp_list


def match_ingredient_to_tools_keyword(tool, ingredients, food, key_val, db_index):
    # print("\n\n\n[match_ingredient_to_tools_keyword]: ", ingredients, type(ingredients))
    ingredient_dic = string_to_dictionary(ingredients)
    # print(type(ingredient_dic), food, type(food))
    keywords_from_ingredient = ingredient_dic.get(food)
    if keywords_from_ingredient is None:
        return True

    keywords_from_tool = string_to_dictionary(tool[db_index])
    # print("[match_ingredient_to_tools_keyword]")
    # print(keywords_from_tool)
    # print(ingredients)
    # print(keywords_from_ingredient)

    for key in keywords_from_tool:
        if key == key_val:
            for t_keyword_list in keywords_from_tool[key]:
                for t_keyword in t_keyword_list:
                    for i_keyword in keywords_from_ingredient:
                        if t_keyword in i_keyword:
                            # print("RETURN TRUE BECAUSE " + t_keyword, " in " + i_keyword)
                            return True
    # print("RETURN FALSE")
    return False


def size_matches(food, index, ingredients, tool):
    # print("[size_matches] received food: ", food)
    if index == db.ToolI.ISA:
        if tool[db.ToolI.NOT_SIZE] is None:
            return True
        else:
            return match_ingredient_to_tools_keyword(tool, ingredients, food, "isa", db.ToolI.NOT_SIZE)
    elif index == db.ToolI.NOT_ISA:
        if tool[db.ToolI.SIZE] is None:
            return False
        else:
            return match_ingredient_to_tools_keyword(tool, ingredients, food, "not_isa", db.ToolI.SIZE)


def match_concept_to_edge(concept, subject_isa_rel):
    for key in subject_isa_rel:
        for relation in subject_isa_rel[key]:
            if str(concept) in relation:
                # print("[match_concept_to_edge] return True because " + str(concept) + " in " + relation)
                return key
    # print("[match_concept_to_edge] return False")
    return None


def match_definition_to_relations(tool, index, foods_dic, possible_key, negation, ingredients):
    isa_rel_dic = fetch_relations_for_subjects(foods_dic, possible_key)

    for target_concept in tool[index].split(" | "):
        # print("Match current target concept: " + str(target_concept))

        if " & " in target_concept:
            counter = 0
            conj_list = target_concept.split(" & ")

            for conj_target_concept in conj_list:
                # print("In conjunction. Checking target concept: " + str(conj_target_concept))
                concept = match_concept_to_edge(conj_target_concept, isa_rel_dic)

                if ((concept and not negation and size_matches(concept, index, ingredients, tool))
                        or (not concept and negation)):
                    # print("CONJUNCTION: increment counter")
                    counter += 1
                elif concept and negation and size_matches(concept, index, ingredients, tool):
                    counter += 1

            if counter == len(conj_list):
                # print("CONJUNCTION RETURN TRUE")
                return True
            elif negation:
                return False
        else:
            concept = match_concept_to_edge(target_concept, isa_rel_dic)
            if concept and not negation and size_matches(concept, index, ingredients, tool):
                # print("[match_definition_to_concept_net] IN ELSE WITHOUT NEGATION. RETURNING True")
                return True
            elif concept and negation and not size_matches(concept, index, ingredients, tool):
                print("[match_definition_to_concept_net] IN ELSE WITH NEGATION. RETURNING False")
                return False
    # print("[match_definition_to_concept_net] AT THE END. RETURNING: " + str(negation))
    return negation


def match_definition_to_recipe(tool, index, subjects_in_step, negation):
    subject_list = dic_items_to_list(subjects_in_step)
    # print("[match_definition_to_recipe] START: ", subject_list)

    for subject in tool[index].split(" | "):
        if " & " in subject:
            counter = 0
            conj_list = subject.split(" & ")
            for conj_subject in conj_list:
                if (conj_subject in subject_list and not negation) or (conj_subject not in subject_list and negation):
                    # print("increment counter")
                    counter += 1
            if counter == len(conj_list):
                # print("[match_definition_to_recipe] in conjunction. RETURN TRUE.")
                return True
            elif negation:
                return False
        else:
            # print("disjunction. current subject: ", subject)
            if subject in subject_list and not negation:
                # print("[match_definition_to_recipe] in disjunction not negation. RETURN TRUE")
                return True
            elif subject in subject_list and negation:
                # print("[match_definition_to_recipe] in disjunction negation. RETURN FALSE")
                return False

    # print("[match_definition_to_recipe] AT THE END. RETURNING: " + str(negation))
    return negation


def match_definition_to_ingredient(tool, index, ingredient_dic, negation):
    ingredient_list = fetch_keys_from_dic(ingredient_dic)
    # print("[match_definition_to_ingredient] ingredient list: " + str(ingredient_list))
    for keyword in tool[index].split(" | "):
        # print("keyword from tool " + str(keyword))
        if " & " in keyword:
            counter = 0
            conj_list = keyword.split(" & ")
            for conj_keyword in conj_list:
                if ((conj_keyword in ingredient_list and not negation)
                        or (conj_keyword not in ingredient_list and negation)):
                    # print("increment counter")
                    counter += 1
            if counter == len(conj_list):
                # print("[match_definition_to_ingredient] in conjunction. counter equal len so returning True.")
                return True
            elif negation:
                return False
        else:
            if keyword in ingredient_list and not negation:
                # print("[match_definition_to_ingredient] in disjunction without negation. RETURN TRUE")
                return True
            elif keyword in ingredient_list and negation:
                # print("[match_definition_to_ingredient] in disjunction with negation. RETURN FALSE")
                return False
    # print("[match_definition_to_ingredient] AT THE END. RETURNING: " + str(negation))
    return negation
