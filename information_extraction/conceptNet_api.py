import requests
import time
import ast


def query_concept_net(step_object):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
    return obj['edges']


def convert_dictionary_to_list(subjects_in_step, possible_key):
    temp = []
    if possible_key == 0:
        for key in subjects_in_step:
            for nouns in subjects_in_step[key]:
                temp.append(nouns)
    else:
        temp = subjects_in_step[possible_key]
    return temp


def fetch_relations_for_subjects(subjects):
    relations = []
    for subject in subjects:
        relations.append(query_concept_net(subject))
    return relations


def all_subjects_must_match_concept(target_concept, isa_rel_for_subjects_in_step):
    target_concept_all = ast.literal_eval(target_concept)
    for found_isa in isa_rel_for_subjects_in_step:
        if target_concept_all not in found_isa:
            return False
    return True


def match_definition_to_concept_net(tool, index, subjects_in_step, possible_key):
    subjects = convert_dictionary_to_list(subjects_in_step, possible_key)
    isa_rel_for_subjects_in_step = fetch_relations_for_subjects(subjects)

    for target_concept in tool[index].split(" | "):
        if " & " in target_concept:
            all_true = True
            for conj_target_concept in target_concept.split(" & "):
                if ("all:[" in conj_target_concept
                        and not all_subjects_must_match_concept(target_concept, isa_rel_for_subjects_in_step)):
                    all_true = False
                    break
                if conj_target_concept not in isa_rel_for_subjects_in_step:
                    all_true = False
                    break
            if all_true:
                return True
        elif ("all:[" in target_concept
              and all_subjects_must_match_concept(target_concept, isa_rel_for_subjects_in_step)):
            return True
        else:
            if target_concept in isa_rel_for_subjects_in_step:
                return True
