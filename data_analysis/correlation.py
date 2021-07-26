#!/usr/bin/env python3

# Remove opencv pip uninstall python-opencv for this to display the graph
# Internal thread error due to sharing graphics library (?)
import os
import sqlite3
import ast
from moviepy.editor import VideoFileClip
import matplotlib.pyplot as plt
import numpy as np


def sql_fetch_1to1_videos():
    recipe_conn = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/db/recipes_with_1to1_video.db')
    recipe_cursor = recipe_conn.cursor()
    recipe_cursor.execute("SELECT * FROM RecipesWith1To1Video;")
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


def fetch_video_file(video_files, video_id):
    for vid in video_files:
        if ".mp4" in vid and fetch_video_id(vid) == video_id:
            return vid
    return None


def fetch_number_of_words(preparation):
    prep_dic = ast.literal_eval(preparation)
    word_count = 0

    for step in prep_dic.values():
        words_in_step = step.split(" ")
        word_count += len(words_in_step)

    return word_count


def fetch_video_length(vid_file):
    clip = VideoFileClip(vid_file)
    dur = clip.duration
    return dur


if __name__ == "__main__":
    PATH_TO_VIDEOS = "/media/leander/1F1C-606E/videos/"
    videos = os.listdir(PATH_TO_VIDEOS)
    recipes_1to1_videos = sql_fetch_1to1_videos()
    data = []
    number_of_words = []
    duration_of_video = []

    for recipe in recipes_1to1_videos:
        print(recipe[RecipeWithVideoI.URL])
        video_file = fetch_video_file(videos, recipe[RecipeWithVideoI.VIDEO_ID])
        print("video ID: ", recipe[RecipeWithVideoI.VIDEO_ID])
        assert video_file is not None, "something is seriously wrong"

        word_count = fetch_number_of_words(recipe[RecipeWithVideoI.PREPARATION])
        duration = fetch_video_length(PATH_TO_VIDEOS + video_file)
        print("word count: ", word_count)
        print("video duration: ", duration)
        number_of_words.append(int(word_count))
        duration_of_video.append(int(duration))

    m = np.polyfit(number_of_words, duration_of_video, deg=1)
    plt.plot(number_of_words, duration_of_video, '.')
    plt.plot(number_of_words, m[0]*np.array(number_of_words) + m[1], '-')
    plt.xlabel('Word Count in Preparation')
    plt.ylabel('Video Duration')
    plt.title('Graph to show the word count in relation to video duration')
    plt.show()

    correlation = np.corrcoef(number_of_words, duration_of_video)
    print(correlation[0, 1])
    # correlation coefficient 0.8262568746718546
    print(correlation[1, 0])
    # correlation coefficient 0.8262568746718546