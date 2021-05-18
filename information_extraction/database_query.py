import sqlite3


def sql_fetch_recipe_db():
    recipe_connection = sqlite3.connect('../data/raw_recipes/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    recipe_cursor.execute("SELECT * FROM Recipes WHERE URL=='https://tasty.co/recipe/orange-cauliflower-chicken';")
    return recipe_cursor.fetchall()


def sql_fetch_util_db():
    utils_connection = sqlite3.connect('../data/constructed_knowledge/tools.db')
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Tools;")
    return utils_cursor.fetchall()


class Indexes():
    T_TOOL = 0
    T_LOCATION = 1
    T_DIRECT_VERB = 2
    T_AMBIGUOUS_VERB = 3
    T_IMPLIED = 4
    T_DEFINE = 5
    T_TITLE = 6
    T_ISA = 7
    T_NOT_ISA = 8
    T_SIZE = 9
    T_NOT_SIZE = 10
    T_SUBJECT = 11
    T_NOT_SUBJECT = 12
    T_INGREDIENT = 13
    T_NOT_INGREDIENT = 14

    R_URL = 0
    R_TITLE = 1
    R_RATING = 2
    R_SERVING = 3
    R_TIME = 4
    R_CATEGORY = 5
    R_INGREDIENTS = 6
    R_PREPARATION = 7
    R_NUTRITION = 8
