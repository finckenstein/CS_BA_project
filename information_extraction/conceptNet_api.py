import requests
import time
import ast


def query_concept_net(step_object, target_concept):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/"+str(step_object)+"&rel=/r/IsA&end=/c/en/"+str(target_concept)
    obj = requests.get(uri).json()
    obj.keys()
    print(len(obj['edges']))
    return len(obj['edges'])


def concept_found_concept_net(target_concept, object_list, just_sentence):
    print("[find_all_concepts] given list: " + str(object_list) + " and target concept " + str(target_concept))
    if just_sentence:
        for step_object in object_list:
            if ':' in step_object:
                list_of_target_concept_that_need_to_hold = ast.literal_eval(step_object)
                for target_concept_all in list_of_target_concept_that_need_to_hold:
                    num_of_concepts_found = query_concept_net(step_object, target_concept_all)
                    if num_of_concepts_found == 0:
                        print("[concept_found_in_step] returning True")
                        return False
                    time.sleep(1)
            if len(step_object.split(" ")) > 1:
                continue
            else:
                num_of_concepts_found = query_concept_net(step_object, target_concept)
                if num_of_concepts_found > 0:
                    print("[concept_found_in_step] returning True")
                    return True
            time.sleep(1)
    else:
        for key in object_list:
            for step_object in object_list[key]:
                if ':' in step_object:
                    list_of_target_concept_that_need_to_hold = ast.literal_eval(step_object)
                    for target_concept_all in list_of_target_concept_that_need_to_hold:
                        num_of_concepts_found = query_concept_net(step_object, target_concept_all)
                        if num_of_concepts_found == 0:
                            print("[concept_found_in_step] returning True")
                            return False
                        time.sleep(1)
                if len(step_object.split(" ")) > 1:
                    continue
                num_of_concepts_found = query_concept_net(step_object, target_concept)
                if num_of_concepts_found > 0:
                    print("[concept_found_in_step] returning True")
                    return True
                time.sleep(1)
    return False
