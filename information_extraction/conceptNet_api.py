import requests
import time


def concept_found_conceptNet(target_concept, object_list):
    print("[find_all_concepts] given list: " + str(object_list) + " and target concept " + str(target_concept))
    for key in object_list:
        for step_object in object_list[key]:
            print("[find_all_concepts] current object: " + step_object)
            uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA&end=/c/en/" + \
                  str(target_concept)
            obj = requests.get(uri).json()
            obj.keys()
            print(len(obj['edges']))
            if len(obj['edges']) > 0:
                print("[concept_found_in_step] returning True")
                return True
            time.sleep(1)
    return False
