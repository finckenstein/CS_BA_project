#!/usr/bin/env python3

import sqlite3
import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
import time
import urllib.request
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('database_query'))))


def sql_fetch_recipe_db(url):
    print("\n\nHELLO: ", url)
    recipe_connection = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/recipes1.db')
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM Recipes;")
    else:
        query = "SELECT * FROM Recipes WHERE URL = " + url + ";"
        print(query)
        recipe_cursor.execute(query)
    return recipe_cursor.fetchall()


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


class SeleniumVideoSpider(scrapy.Spider):
    name = 'selenium_video'
    allowed_domains = ['tasty.co', 'vid.tasty.co']

    def start_requests(self):
        recipe_rows = sql_fetch_recipe_db("'https://tasty.co/recipe/ghanaian-jollof-rice-as-made-by-tei-hammond'")
        for recipe in recipe_rows:
            print(recipe)
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
                print(video_url)
                yield Request(video_url, callback=self.parse)
            driver.quit()

    def parse(self, response):
        print("\n\n\n RESPONSE: ", response, "\n\n\n")
        for string in str(response).split(" "):
            if "://vid.tasty.co" in string:
                if string[len(string)-1] == '>':
                    file_name = "../data/videos/" + string[:-1].replace('/', '|') + ".mp4"
                    urllib.request.urlretrieve(string[:-1], file_name)
                    yield {'VID_URL': string[:-1]}
                else:
                    file_name = "../data/videos/" + string + ".mp4"
                    urllib.request.urlretrieve(string, file_name)
                    yield {'VID_URL': string}
