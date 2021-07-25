#!/usr/bin/env python3

import csv
import scrapy
from selenium import webdriver
from scrapy.selector import Selector
import time
import os
import sys
from scrapy.http import Request

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('/home/leander/Desktop/automatic_KB/database_query'))))
from database_query import RecipeI
from database_query import sql_fetch_recipe_db


def write_to_csv(data):
    fields = ['URL', 'Title', 'Rating', 'Serving', 'Time', 'Category', 'Ingredients', 'Preparation', 'Nutritional Info',
              'Video_ID']
    filename = "recipe_with_video.csv"
    with open(filename, 'a+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(data)
        csvfile.close()


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


def fetch_video(video_url, video_stored):
    url_bits = video_url.split("/")
    media = url_bits[len(url_bits) - 1]
    print("\n\n\n[fetch_video]", video_url, media)

    for video in video_stored:
        if media in video:
            return video
    return None


def initialize_dictionary(recipe, vid_id):
    return {'URL': recipe[RecipeI.URL],
            'Title': recipe[RecipeI.TITLE],
            'Rating': recipe[RecipeI.RATING],
            'Serving': recipe[RecipeI.SERVING],
            'Time': recipe[RecipeI.TIME],
            'Category': recipe[RecipeI.CATEGORY],
            'Ingredients': recipe[RecipeI.INGREDIENTS],
            'Preparation': recipe[RecipeI.PREPARATION],
            'Nutritional Info': recipe[RecipeI.NUTRITION],
            'Video_ID': vid_id}


class MapTextToVideoSpider(scrapy.Spider):
    name = 'map_text_to_video'
    allowed_domains = ['tasty.co', 'vid.tasty.co']

    def start_requests(self):
        recipe_rows = sql_fetch_recipe_db("all")

        PATH_TO_USB_VIDEOS = "/media/leander/1F1C-606E/videos/"
        video_files = os.listdir(PATH_TO_USB_VIDEOS)

        for recipe in recipe_rows:
            driver = webdriver.Chrome('/home/leander/Documents/chromedriver')
            print("\n\n\n\n: ", driver)
            print("CHECKING NEW URL: ", recipe[RecipeI.URL], "\n\n")
            time.sleep(5)
            tmp = driver.get(recipe[RecipeI.URL])
            print(tmp)
            time.sleep(15)

            src_code = Selector(text=driver.page_source)
            print("SRC_CODE: ", src_code)
            video_urls = src_code.xpath('//video/@src').extract()
            print("VIDEO_URL: ", video_urls)

            for video_url in video_urls:
                video = fetch_video(video_url, video_files)
                if video is not None:
                    video_id = fetch_video_id(video)
                    write_to_csv(initialize_dictionary(recipe, video_id))
                else:
                    write_to_csv(initialize_dictionary(recipe, None))
                yield Request(video_url, callback=self.parse)

            driver.quit()

    def parse(self, response):
        pass