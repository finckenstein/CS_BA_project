import requests
import time
import ast


def query_concept_net(step_object):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.25)
    surface_text = []
    for edge in obj['edges']:
        if edge['surfaceText'] is not None:
            surface_text.append(edge['surfaceText'])
    return surface_text


def convert_dictionary_to_list(subjects_in_step, possible_key):
    temp = []
    if possible_key == -1:
        for key in subjects_in_step:
            for nouns in subjects_in_step[key]:
                temp.append(nouns)
    else:
        temp = subjects_in_step[possible_key]
    return temp


def fetch_relations_for_subjects(subjects):
    relations = []
    for subject in subjects:
        if len(subject.split(" ")) > 1:
            for sub in subject.split(" "):
                relations.append(query_concept_net(sub))
        else:
            relations.append(query_concept_net(subject))
    return relations


def match_concept_to_edge(concept, subject_isa_rel):
    for relation in subject_isa_rel:
        for text in relation:
            if str(concept) in text:
                print("[match_concept_to_edge] return True because " + str(concept) + " in " + text)
                return True
    print("[match_concept_to_edge] return False")
    return False


def match_to_concept_net(tool, index, subjects_in_step, possible_key, negation):
    subjects = convert_dictionary_to_list(subjects_in_step, possible_key)
    subject_isa_rel_list = fetch_relations_for_subjects(subjects)

    for target_concept in tool[index].split(" | "):
        print("Match current target concept: " + str(target_concept))
        if " & " in target_concept:
            all_true = True
            for conj_target_concept in target_concept.split(" & "):
                print("In conjunction. Checking target concept: " + str(conj_target_concept))
                concept_matches = match_concept_to_edge(conj_target_concept, subject_isa_rel_list)
                if not concept_matches and not negation:
                    print("CONJUNCTION: BREAK OUT OF LOOP")
                    all_true = False
                    break
                elif concept_matches and negation:
                    print("CONJUNCTION: BREAK OUT OF LOOP")
                    all_true = False
                    break

            if all_true:
                print("CONJUNCTION RETURN TRUE")
                return True
        else:
            if match_concept_to_edge(target_concept, subject_isa_rel_list):
                print("[match_definition_to_concept_net] RETURN "+str(not negation))
                return not negation
    print("[match_definition_to_concept_net] RETURN FALSE")
    return False


def get_ids_from_concept_net(step_object):
    print("[get_ids_from_concept_net] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
    ids = []
    for edge in obj['edges']:
        if edge['@id'] is not None:
            ids.append(edge['@id'])
    return ids


def filter_out_non_foods(nouns):
    non_food_related = ['artifact', 'intelligent', ]
    food_related_ids = ['food', 'plant']
    real_food = []
    print("HELLO: " + str(nouns))

    for noun in nouns:
        print(noun)
        for ids in get_ids_from_concept_net(noun):
            # print("RETURNED IDS: "+str(ids))
            for non_food in non_food_related:
                if non_food not in ids:
                    for food in food_related_ids:
                        if food in ids and noun not in str(real_food):
                            print("APPENDED: " + noun)
                            real_food.append(noun)
                else:
                    print("noun not added because its not a food: " + noun)

    print("REAL FOOD: "+str(real_food))
    return real_food
