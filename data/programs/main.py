#!/usr/bin/env python3
from csv_to_db.recipes_to_db import RecipesToDB
from csv_to_db.tools_to_db import ToolsToDB
from csv_to_db.kitchenware_to_db import KitchenwareToDB
# from words_from_recipe import extract_words_and_occurrence_of_ingredients
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('../database_query'))))
import database_query as db

if __name__ == '__main__':
    KitchenwareToDB()
    ToolsToDB()
    # RecipesToDB()
    # extract_words_and_occurrence_of_ingredients("NOUN", db.RecipeI.INGREDIENTS,
    #                                             "../raw_recipes/Nouns_in_ingredients.csv")
