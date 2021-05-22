import requests
import time


def query_concept_net(step_object):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/"+str(step_object)+"&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
    return obj['edges']


def concept_found_concept_net(target_concept, object_list):
    temp = []
    for curr_object in object_list:
        temp.append(query_concept_net(curr_object))

    for edges in temp:
        if target_concept in (str(edges)):
            print("TRUE")
        else:
            print("NOT TRUE")


if __name__ == '__main__':
    print(concept_found_concept_net("liquid", ["salmon", "water"]))


    # def query_concept_net(step_object, target_concept):
    #     print("[find_all_concepts] current object: " + step_object)
    #     uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA&end=/c/en/" + str(
    #         target_concept)
    #     obj = requests.get(uri).json()
    #     obj.keys()
    #     time.sleep(0.5)
    #     return len(obj['edges'])
    #
    #
    # def loop_over_object_match_for_all(target_concept, object_list):
    #     for step_object in object_list:
    #         if len(step_object.split(" ")) > 1:
    #             continue
    #         target_concept_for_all_objects = ast.literal_eval(target_concept)
    #         num_of_concepts_found = query_concept_net(step_object, target_concept_for_all_objects)
    #         if num_of_concepts_found == 0:
    #             return False
    #     return True
    #
    #
    # def all_objects_need_to_match_concept(target_concept, object_list, just_sentence):
    #     if just_sentence:
    #         return loop_over_object_match_for_all(target_concept, object_list)
    #     else:
    #         for key in object_list:
    #             if not loop_over_object_match_for_all(target_concept, object_list[key]):
    #                 return False
    #     return True
    #
    #
    # def loop_over_object_match_for_some(target_concept, object_list):
    #     for step_object in object_list:
    #         if len(step_object.split(" ")) > 1:
    #             continue
    #         num_of_concepts_found = query_concept_net(step_object, target_concept)
    #         if num_of_concepts_found > 0:
    #             return True
    #     return False
    #
    #
    # def one_object_need_to_match_concept(target_concept, object_list, just_sentence):
    #     if just_sentence:
    #         return loop_over_object_match_for_some(target_concept, object_list)
    #     else:
    #         for key in object_list:
    #             if loop_over_object_match_for_some(target_concept, object_list[key]):
    #                 return True
    #     return False
    #
    #
    # def concept_found_concept_net(target_concept, object_list, just_sentence):
    #     print("[concept_found_concept_net] given list: " + str(object_list) + " and target concept " + str(
    #         target_concept))
    #     if ':' in target_concept:
    #         temp1 = all_objects_need_to_match_concept(target_concept, object_list, just_sentence)
    #         print("[concept_found_concept_net] FOR ALL RETURNING: " + str(temp1))
    #         return temp1
    #     else:
    #         temp2 = one_object_need_to_match_concept(target_concept, object_list, just_sentence)
    #         print("[concept_found_concept_net] NOT ALL RETURNING: " + str(temp2))
    #         return temp2
