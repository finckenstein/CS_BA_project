#!/usr/bin/env python3
import spacy

from alias_functions import string_to_dictionary
from alias_functions import is_small_medium_or_large
from alias_functions import is_verb_or_pronoun
from alias_functions import is_size_bowl

from computer_vision.inference_with_KT_model import iterate_over_video

import sys
import os
from moviepy.editor import VideoFileClip

sys.path.append('/home/leander/Desktop/automatic_KB/database_query')
import database_query as db
import ast

# subjects_in_step = {}
# verbs_in_step = []
# kitchenware = []
# entire_kitchenware_kb = ()
# cur_kitchenware = None
#
#
# def initialize_kitchenware_array():
#     for row in entire_kitchenware_kb:
#         for tmp_kitchenware in row[db.KitchenwareI.KITCHENWARE].split(", "):
#             if tmp_kitchenware not in kitchenware:
#                 kitchenware.append(tmp_kitchenware)
#
#
# def initialize_verb_and_nouns_in_step(i, sentence, num_sentences):
#     token = sentence[i]
#     token_text = token.lemma_.lower()
#
#     if is_verb_or_pronoun(token) and token_text not in verbs_in_step:
#         verbs_in_step.append(token_text)
#     elif token.dep_ == "compound" and sentence[i + 1].pos_ == "NOUN":
#         compound_noun = str(token_text + " " + sentence[i + 1].lemma_.lower())
#         if compound_noun not in subjects_in_step[num_sentences]:
#             subjects_in_step[num_sentences].append(compound_noun)
#     elif (token.pos_ == "NOUN" and not token.dep_ == "compound"
#           and token_text not in subjects_in_step[num_sentences]):
#         subjects_in_step[num_sentences].append(token_text)
#     elif is_small_medium_or_large(token_text):
#         if is_size_bowl(sentence, i + 1):
#             subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 1].lemma_.lower())
#             i += 1
#         elif is_size_bowl(sentence, i + 2):
#             subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 2].lemma_.lower())
#             i += 2
#         elif is_size_bowl(sentence, i + 3):
#             subjects_in_step[num_sentences].append(token_text + " " + sentence[i + 3].lemma_.lower())
#             i += 3
#     return i + 1
#
#
# def loop_over_sentence_in_step(num_sentences, sentence):
#     i = 0
#     subjects_in_step[num_sentences] = []
#     while i < len(sentence):
#         i = initialize_verb_and_nouns_in_step(i, sentence, num_sentences)
#
#
# def find_kitchenware(num_sentences):
#     global cur_kitchenware
#     for noun in subjects_in_step[num_sentences]:
#         for tmp_kitchenware in kitchenware:
#             if noun == tmp_kitchenware:
#                 cur_kitchenware = noun
#
#
# def check_verb_to_verify_implied_kitchenware(verb):
#     global cur_kitchenware
#     for kb_row in entire_kitchenware_kb:
#         if kb_row[db.KitchenwareI.VERB] == verb:
#             list_of_kb_kitchenware = kb_row[db.KitchenwareI.KITCHENWARE].split(", ")
#             if cur_kitchenware is None or cur_kitchenware not in list_of_kb_kitchenware:
#                 print("[check_potential_kitchenware_change] changed cur_kitchenware from " +
#                       str(cur_kitchenware) + " to " + str(kb_row[db.KitchenwareI.DEFAULT]))
#                 cur_kitchenware = kb_row[db.KitchenwareI.DEFAULT]
#
#
# def match_noun_to_kitchenware(noun):
#     global cur_kitchenware, kitchenware
#     if not noun == cur_kitchenware and noun in kitchenware:
#         print("[match_noun_to_kitchenware] changed kitchenware from " + cur_kitchenware + " to " + noun)
#         cur_kitchenware = noun
#
# def check_explicit_change_in_kitchenware(token, token_text, sentence, index):
#     if token.pos_ == "NOUN":
#         if token.dep_ == "compound":
#             match_noun_to_kitchenware(token_text + " " + sentence[index + 1].text.lower())
#         else:
#             match_noun_to_kitchenware(token_text)
#     elif is_small_medium_or_large(token_text):
#         if is_size_bowl(sentence, index + 1):
#             index = found_bowl((token_text + " " + sentence[index + 1].text.lower()), index, 1)
#         elif is_size_bowl(sentence, index + 2):
#             index = found_bowl((token_text + " " + sentence[index + 2].text.lower()), index, 2)
#         elif is_size_bowl(sentence, index + 3):
#             index = found_bowl((token_text + " " + sentence[index + 3].text.lower()), index, 3)
#     return index + 1
#

# Dont delete these functions:
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
    def __init__(self):
        self.word_remainder = 0
        self.video_timestamp = 0
        self.counter = 0
        self.PATH_TO_VIDEOS = "/media/leander/1F1C-606E/videos/"
        self.videos = os.listdir(self.PATH_TO_VIDEOS)
        self.words_per_second = 0
        self.path_to_video = None

    def update_recipe_change(self, recipe):
        video_file = fetch_video_file(self.videos, recipe[db.RecipeWithVideoI.VIDEO_ID])
        self.path_to_video = self.PATH_TO_VIDEOS + video_file

        video_duration = fetch_video_length(self.PATH_TO_VIDEOS + video_file)
        word_count = fetch_number_of_words(recipe[db.RecipeWithVideoI.PREPARATION])
        self.words_per_second = word_count/video_duration

    def get_cv_detected_kitchenware(self):
        video_detected_kitchenware = None
        if self.counter >= int(self.words_per_second):

            self.word_remainder += self.words_per_second - self.counter
            self.counter = 0

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp)
            print(video_detected_kitchenware)
            self.video_timestamp += int(self.words_per_second)

        elif self.word_remainder >= 1:
            self.word_remainder -= 1

            video_detected_kitchenware = iterate_over_video(self.path_to_video, self.video_timestamp)
            print("\n\n\n[analysis_recipe_sentence] detected_kitchenware: ", video_detected_kitchenware)
            self.video_timestamp += 1

        self.counter += 1
        print("word_remainder: ", self.word_remainder)
        print("counter: ", self.counter)
        print("words_per_seconds: ", self.words_per_second)
        print("video_timestamp: ", self.video_timestamp)

        return video_detected_kitchenware
