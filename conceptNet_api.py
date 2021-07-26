import requests
import time


def query_concept_net(uri):
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
    return obj['edges']


def is_noun_food(step_object):
    print("[is_noun_food] current object: " + str(step_object))
    food_uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "/n/wn/food&rel=/r/IsA"
    length = len(query_concept_net(food_uri))
    print(length)
    if length >= 1:
        return length
    plant_uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "/n/wn/plant&rel=/r/IsA"
    length = len(query_concept_net(plant_uri))
    print(length)
    if length >= 1:
        return length
    return 0


def get_edges(step_object):
    print("[find_all_concepts] current object: " + step_object)
    uri = "http://api.conceptnet.io/query?start=/c/en/" + str(step_object) + "&rel=/r/IsA"
    ids = []
    for edge in query_concept_net(uri):
        if edge['@id'] is not None:
            ids.append(edge['@id'])
    return ids


def filter_out_non_foods(nouns):
    real_food = {}
    print("[filter_out_non_foods]: received nouns: " + str(nouns))

    for noun in nouns:
        print(noun)
        if len(noun.split(" ")) > 1:
            compound_noun = noun.replace(" ", "_")
            if is_noun_food(compound_noun) and compound_noun not in real_food:
                real_food[compound_noun] = get_edges(compound_noun)
        elif is_noun_food(noun) and noun not in real_food:
            real_food[noun] = get_edges(noun)

    return real_food
