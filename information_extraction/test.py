import requests
import time
import ast


def fetch_food_key_and_relations(key, foods):
    tmp = {}
    for food_key in foods[key]:
        for elem in foods[key][food_key]:
            all_foods[food_key] = elem
    return tmp


if __name__ == '__main__':
    all_foods = {0: {'mixer': ['/a/[/r/IsA/,/c/en/mixer/n/wn/artifact/,/c/en/electronic_equipment/n/wn/artifact/]',
                               '/a/[/r/IsA/,/c/en/mixer/n/wn/artifact/,/c/en/kitchen_utensil/n/wn/artifact/]',
                               '/a/[/r/IsA/,/c/en/mixer/n/wn/food/,/c/en/beverage/n/wn/food/]',
                               '/a/[/r/IsA/,/c/en/mixer/n/,/c/en/component/n/opencyc/audio_system_component/]'],
                     'salad': ['is_healthy', 'is_good']},
                 1: {'dough': ['/a/[/r/IsA/,/c/en/dough/n/wn/food/,/c/en/concoction/n/wn/food/]',
                               '/a/[/r/IsA/,/c/en/dough/n/,/c/en/semisolid/n/]',
                               '/a/[/r/IsA/,/c/en/dough/n/,/c/en/pastelike_thing/n/]',
                               '/a/[/r/IsA/,/c/en/dough/n/,/c/en/raw_edibles/n/]',
                               '/a/[/r/IsA/,/c/en/dough/n/,/c/en/beige/n/]']}}
    print(all_foods)
    for sentence_key in all_foods:
        print(sentence_key)
        all_foods.update(fetch_food_key_and_relations(sentence_key, all_foods))
    print(all_foods)

