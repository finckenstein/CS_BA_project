#!/usr/bin/env python3
from computer_vision.inference_with_KT_model import iterate_over_video
import os
from moviepy.editor import VideoFileClip
from database_query import RecipeWithVideoI
import ast
from computer_vision.tensorflow_object_detection_utils import label_map_util
import tensorflow as tf
import pathlib


def load_model(model_path):
    model_dir = pathlib.Path(model_path) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    return model


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


def fetch_video_length(vid_file):
    clip = VideoFileClip(vid_file)
    dur = clip.duration
    return int(dur)


def fetch_number_of_words(preparation):
    prep_dic = ast.literal_eval(preparation)
    word_count = 0

    for step in prep_dic.values():
        words_in_step = step.split(" ")
        word_count += len(words_in_step)

    return word_count


class SyncingTextWithVideo:
    def __init__(self, recipe):
        PATH_TO_VIDEOS = "/media/leander/1F1C-606E/videos/"
        PATH_TO_LABELS = '/home/leander/Desktop/automatic_KB/computer_vision/CV_Kitchen_Tools/kitchen_tools_label_map.pbtxt'
        model_name = '/home/leander/Desktop/automatic_KB/computer_vision/CV_Kitchen_Tools/CV_KT_detection_model_B4/'

        self.unsupported_kt = ['grill', 'barbecue', 'bbq', 'air fryer', 'mixer', 'blender']
        self.detectable_kt = {'bowl': ['small bowl', 'medium bowl', 'large bowl'],
                              'pan': ['saucepan', 'skillet', 'griddle'],
                              'pot': [],
                              'baking sheet': ['sheet pan'],
                              'baking dish': ['foil dish', 'casserole']}

        self.videos = os.listdir(PATH_TO_VIDEOS)
        self.category_i = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
        self.model = load_model(model_name)

        self.word_remainder = 0
        self.video_timestamp = 0
        self.counter = 0

        video_file = fetch_video_file(self.videos, recipe[RecipeWithVideoI.VIDEO_ID])
        self.path_to_video = PATH_TO_VIDEOS + video_file

        video_duration = fetch_video_length(PATH_TO_VIDEOS + video_file)
        word_count = fetch_number_of_words(recipe[RecipeWithVideoI.PREPARATION])
        self.words_per_second = word_count/video_duration

    def get_cv_detected_kitchenware(self):
        video_detected_kitchenware = None
        if self.counter >= int(self.words_per_second):

            self.word_remainder += self.words_per_second - self.counter
            self.counter = 0

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp, self.category_i, self.model)
            # print(video_detected_kitchenware)
            self.video_timestamp += int(self.words_per_second)

        elif self.word_remainder >= 1:
            self.word_remainder -= 1

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp, self.category_i, self.model)
            # print("\n\n\n[analysis_recipe_sentence] detected_kitchenware: ", video_detected_kitchenware)
            self.video_timestamp += 1

        self.counter += 1
        # print("word_remainder: ", self.word_remainder)
        # print("counter: ", self.counter)
        # print("words_per_seconds: ", self.words_per_second)
        # print("video_timestamp: ", self.video_timestamp)

        return video_detected_kitchenware
