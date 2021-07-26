#!/usr/bin/env python3
import sqlite3


def sql_fetch_1to1_videos(url):
    recipe_conn = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/db/recipes_with_1to1_video.db')
    recipe_cursor = recipe_conn.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM RecipesWith1To1Video;")
    else:
        recipe_cursor.execute("SELECT * FROM RecipesWith1To1Video WHERE URL = '" + url + "';")
    return recipe_cursor.fetchall()


def sql_fetch_recipe_db(url):
    recipe_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/old_recipes/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM Recipes;")
    else:
        recipe_cursor.execute("SELECT * FROM Recipes WHERE URL = " + url + ";")
    return recipe_cursor.fetchall()


def sql_fetch_recipes_with_video(url):
    recipe_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/old_recipes/recipes_with_video.db')
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM RecipesWithVideo;")
    else:
        recipe_cursor.execute("SELECT * FROM RecipesWithVideo WHERE URL = " + url + ";")
    return recipe_cursor.fetchall()


def sql_fetch_tools_db():
    utils_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/constructed_knowledge/tools.db')
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Tools;")
    return utils_cursor.fetchall()


def sql_fetch_kitchenware_db():
    utils_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/constructed_knowledge/kitchenware.db')
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


class RecipeWithVideoI:
    URL = 0
    TITLE = 1
    RATING = 2
    SERVING = 3
    TIME = 4
    CATEGORY = 5
    INGREDIENTS = 6
    PREPARATION = 7
    NUTRITION = 8
    VIDEO_ID = 9


class KitchenwareI:
    VERB = 0
    KITCHENWARE = 1
    DEFAULT = 2
