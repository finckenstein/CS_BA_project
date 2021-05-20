import sqlite3


def sql_fetch_recipe_db():
    recipe_connection = sqlite3.connect('../data/raw_recipes/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    recipe_cursor.execute("SELECT * FROM Recipes WHERE URL=='https://tasty.co/recipe/one-pot-broccoli-cheddar-soup';")
    return recipe_cursor.fetchall()


def sql_fetch_tools_db():
    utils_connection = sqlite3.connect('../data/constructed_knowledge/tools.db')
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Tools;")
    return utils_cursor.fetchall()


def sql_fetch_kitchenware_db():
    utils_connection = sqlite3.connect('../data/constructed_knowledge/kitchenware.db')
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Kitchenware;")
    return utils_cursor.fetchall()


class ToolI:
    TOOL = 0
    KITCHENWARE = 1
    DIRECT_VERB = 2
    AMBIGUOUS_VERB = 3
    IMPLIED = 4
    DEFINE = 5
    TITLE = 6
    ISA = 7
    NOT_ISA = 8
    SIZE = 9
    NOT_SIZE = 10
    SUBJECT = 11
    NOT_SUBJECT = 12
    INGREDIENT = 13
    NOT_INGREDIENT = 14


class RecipeI:
    URL = 0
    TITLE = 1
    RATING = 2
    SERVING = 3
    TIME = 4
    CATEGORY = 5
    INGREDIENTS = 6
    PREPARATION = 7
    NUTRITION = 8


class KitchenwareI:
    VERB = 0
    KITCHENWARE = 1
    DEFAULT = 2
