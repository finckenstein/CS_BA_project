#!/usr/bin/env python3
import csv
import sqlite3
import ast
import os
from moviepy.editor import VideoFileClip


def sql_fetch_recipes_with_video(url):
    recipe_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/old_recipes/recipes_with_video.db')
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM RecipesWithVideo;")
    else:
        recipe_cursor.execute("SELECT * FROM RecipesWithVideo WHERE URL = " + url + ";")
    return recipe_cursor.fetchall()


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


def sql_fetch_recipe_db(url):
    recipe_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/old_recipes/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM Recipes;")
    else:
        recipe_cursor.execute("SELECT * FROM Recipes WHERE URL = " + url + ";")
    return recipe_cursor.fetchall()


def write_to_csv(data, filename):
    fields = ['URL', 'Title', 'Rating', 'Serving', 'Time', 'Category', 'Ingredients', 'Preparation', 'Nutritional Info',
              'Video_ID']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        csvfile.close()


def to_dictionary(recipe_tuple, is_from_video):
    if is_from_video:
        return {'URL': recipe_tuple[RecipeWithVideoI.URL],
                'Title': recipe_tuple[RecipeWithVideoI.TITLE],
                'Rating': recipe_tuple[RecipeWithVideoI.RATING],
                'Serving': recipe_tuple[RecipeWithVideoI.SERVING],
                'Time': recipe_tuple[RecipeWithVideoI.TIME],
                'Category': recipe_tuple[RecipeWithVideoI.CATEGORY],
                'Ingredients': recipe_tuple[RecipeWithVideoI.INGREDIENTS],
                'Preparation': recipe_tuple[RecipeWithVideoI.PREPARATION],
                'Nutritional Info': recipe_tuple[RecipeWithVideoI.NUTRITION],
                'Video_ID': recipe_tuple[RecipeWithVideoI.VIDEO_ID]}
    else:
        return {'URL': recipe_tuple[RecipeWithVideoI.URL],
                'Title': recipe_tuple[RecipeWithVideoI.TITLE],
                'Rating': recipe_tuple[RecipeWithVideoI.RATING],
                'Serving': recipe_tuple[RecipeWithVideoI.SERVING],
                'Time': recipe_tuple[RecipeWithVideoI.TIME],
                'Category': recipe_tuple[RecipeWithVideoI.CATEGORY],
                'Ingredients': recipe_tuple[RecipeWithVideoI.INGREDIENTS],
                'Preparation': recipe_tuple[RecipeWithVideoI.PREPARATION],
                'Nutritional Info': recipe_tuple[RecipeWithVideoI.NUTRITION]}


def fetch_all_urls(recipe_array):
    url_array = []
    for tmp_recipe in recipe_array:
        url_array.append(tmp_recipe['URL'])
    return url_array


def fetch_recipes_without_video(video_stored, video_not_stored):
    all_recipes = sql_fetch_recipe_db("all")
    url_of_stored_video = fetch_all_urls(video_stored)
    url_of_not_stored_video = fetch_all_urls(video_not_stored)
    tmp_recipe_without_video = []

    for recipe in all_recipes:
        recipe = to_dictionary(recipe, False)
        if (recipe['URL'] not in url_of_stored_video
                and recipe['URL'] not in url_of_not_stored_video
                and recipe not in tmp_recipe_without_video):
            tmp_recipe_without_video.append(recipe)

    return tmp_recipe_without_video


def fetch_number_of_words(preparation):
    prep_dic = ast.literal_eval(preparation)
    wc = 0

    for step in prep_dic.values():
        words_in_step = step.split(" ")
        wc += len(words_in_step)

    return wc


def recipe_video_is_unique(url, vid_id, recis):
    for reci in recis:
        if reci['Video_ID'] == vid_id and reci['URL'] != url:
            return False
    return True


def fetch_video_id(f):
    file_parts_array = f.split('_')
    tmp_id = ''

    for file_part in file_parts_array:
        if '(' in file_part:
            start_index = file_part.index('(') + 1
            while not file_part[start_index] == ')':
                tmp_id += file_part[start_index]
                start_index += 1
    return int(tmp_id)


def fetch_video_length(vid_file):
    clip = VideoFileClip(vid_file)
    dur = clip.duration
    return dur


def fetch_video_file(video_files, video_id):
    for vid in video_files:
        if ".mp4" in vid and fetch_video_id(vid) == video_id:
            return vid
    return None


if __name__ == '__main__':
    recipes_with_video = sql_fetch_recipes_with_video("all")
    recipes_with_video_stored = []
    recipes_with_video_not_stored = []
    PATH_TO_DIRECTORY = "/home/leander/Desktop/automatic_KB/recipes/"

    for recipe_w_vid in recipes_with_video:
        if recipe_w_vid[RecipeWithVideoI.VIDEO_ID] is not None:
            recipes_with_video_stored.append(to_dictionary(recipe_w_vid, True))
        else:
            recipes_with_video_not_stored.append(to_dictionary(recipe_w_vid, True))

    recipes_without_video = fetch_recipes_without_video(recipes_with_video_stored, recipes_with_video_not_stored)

    PATH_TO_VIDEOS = "/media/leander/1F1C-606E/videos/"
    videos = os.listdir(PATH_TO_VIDEOS)

    recipe_with_1to1_video = []
    recipe_without_1to1_video = []

    for rec in recipes_with_video_stored:
        word_count = fetch_number_of_words(rec['Preparation'])
        vid_file = fetch_video_file(videos, rec['Video_ID'])
        vid_duration = fetch_video_length(PATH_TO_VIDEOS + vid_file)
        if recipe_video_is_unique(rec['URL'], rec['Video_ID'], recipes_with_video_stored) and word_count >= vid_duration:
            recipe_with_1to1_video.append(rec)
        else:
            recipe_without_1to1_video.append(rec)

    write_to_csv(recipes_with_video_stored, PATH_TO_DIRECTORY+"recipes_with_video_stored.csv")
    write_to_csv(recipes_with_video_not_stored, PATH_TO_DIRECTORY+"recipes_with_video_not_stored.csv")
    write_to_csv(recipes_without_video, PATH_TO_DIRECTORY+"recipes_without_video.csv")
    write_to_csv(recipe_without_1to1_video, PATH_TO_DIRECTORY+"recipes_without_1to1_video.csv")
    write_to_csv(recipe_with_1to1_video, PATH_TO_DIRECTORY+"recipes_with_1to1_video.csv")

    print(len(recipes_with_video_stored))
    print(len(recipe_without_1to1_video))
    print(len(recipe_with_1to1_video))
    print(len(recipes_with_video_not_stored))
    print(len(recipes_without_video))
