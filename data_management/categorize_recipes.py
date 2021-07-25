import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('/home/leander/Desktop/automatic_KB/database_query'))))
from database_query import sql_fetch_recipe_db
from database_query import RecipeWithVideoI
from database_query import sql_fetch_recipes_with_video


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


def fetch_videos_without_video(video_stored, video_not_stored):
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


def fetch_video_ids_not_unique(video_stored):
    video_id_array = []
    occurrence = []

    for recipe in video_stored:
        if recipe['Video_ID'] not in video_id_array:
            video_id_array.append(recipe['Video_ID'])
            occurrence.append(1)
        else:
            occurrence[video_id_array.index(recipe['Video_ID'])] += 1

    not_unique_id = []
    for vid_id in video_id_array:
        if occurrence[video_id_array.index(vid_id)] > 1:
            not_unique_id.append(vid_id)
    return not_unique_id


if __name__ == '__main__':
    recipes_with_video = sql_fetch_recipes_with_video("all")
    print(recipes_with_video)
    recipes_with_video_stored = []
    recipes_with_video_not_stored = []
    PATH_TO_DIRECTORY = "/home/leander/Desktop/automatic_KB/recipes/"

    for recipe_w_vid in recipes_with_video:
        if recipe_w_vid[RecipeWithVideoI.VIDEO_ID] is not None:
            recipes_with_video_stored.append(to_dictionary(recipe_w_vid, True))
        else:
            recipes_with_video_not_stored.append(to_dictionary(recipe_w_vid, True))

    recipes_without_video = fetch_videos_without_video(recipes_with_video_stored, recipes_with_video_not_stored)
    video_id_not_unique = fetch_video_ids_not_unique(recipes_with_video_stored)
    print(video_id_not_unique)

    recipe_with_1to1_video = []
    recipe_without_1to1_video = []

    for recipe in recipes_with_video_stored:
        if recipe['Video_ID'] in video_id_not_unique:
            recipe_without_1to1_video.append(recipe)
        else:
            recipe_with_1to1_video.append(recipe)

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
