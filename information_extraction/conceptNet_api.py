import requests
import time
import ast


def query_concept_net(step_object):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
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


def all_subjects_match_concept(target_concept, surface_text, is_not):
    target_concept_all = ast.literal_eval(target_concept)
    concept_list = target_concept_all['all'].split(", ")
    print("\n\n" + str(concept_list) + "\n\n")

    if is_not:
        for relation in surface_text:
            for concept in concept_list:
                if str(concept) in relation:
                    print("[all_subjects_must_match_concept] return False because "
                          + str(concept) + " is in " + str(relation))
                    return False
    else:
        for relation in surface_text:
            for concept in concept_list:
                if not str(concept) in relation:
                    print("[all_subjects_must_match_concept] return False because "
                          + str(concept) + " is not in " + str(relation))
                    return False
    print("[all_subjects_must_match_concept] return True because nothing was found")
    return True


def match_to_concept_net(tool, index, subjects_in_step, possible_key, is_not):
    subjects = convert_dictionary_to_list(subjects_in_step, possible_key)
    subject_isa_rel_list = fetch_relations_for_subjects(subjects)

    for target_concept in tool[index].split(" | "):
        print("Match current target concept: " + str(target_concept))
        if " & " in target_concept:
            all_true = True
            for conj_target_concept in target_concept.split(" & "):
                print("In conjunction. Checking target concept: " + str(conj_target_concept))
                if ("all" in conj_target_concept
                        and all_subjects_match_concept(conj_target_concept, subject_isa_rel_list, is_not)):
                    print("CONJUNCTION ALL SUBJECT: FALSE and BREAK OUT OF LOOP")
                    all_true = False
                    break
                elif ("all" not in conj_target_concept
                      and not match_concept_to_edge(conj_target_concept, subject_isa_rel_list)
                      and not is_not):
                    print("CONJUNCTION: FALSE and BREAK OUT OF LOOP")
                    all_true = False
                    break
            if all_true:
                print("CONJUNCTION RETURN TRUE")
                return True
        elif ("all" in target_concept
              and all_subjects_match_concept(target_concept, subject_isa_rel_list, is_not)):
            print("[match_definition_to_concept_net] RETURN TRUE")
            return True
        else:
            if match_concept_to_edge(target_concept, subject_isa_rel_list) and not is_not:
                print("[match_definition_to_concept_net] RETURN TRUE")
                return True
    print("[match_definition_to_concept_net] RETURN FALSE")
    return False
