#!/usr/bin/env python3
import sqlite3
import pandas as pd


class RecipesWith1To1VideoToDB:
    def __init__(self):
        PATH_TO_DB = '/home/leander/Desktop/automatic_KB/recipes/recipes_with_1to1_video.db'
        PATH_TO_CSV = '/home/leander/Desktop/automatic_KB/recipes/recipes_with_1to1_video.csv'
        DB_NAME = "RecipesWith1To1Video"
        conn = sqlite3.connect(PATH_TO_DB)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS " + DB_NAME + " ("
                  "URL text Unique Primary Key, "
                  "Title text, "
                  "Rating integer, "
                  "Serving integer, "
                  "Time text, "
                  "Categories text, "
                  "Ingredients text, "
                  "Preparation text, "
                  "Nutritional_Info text,"
                  "Video_ID int);")
        conn.commit()

        r_recipes = pd.read_csv(PATH_TO_CSV)
        r_recipes.to_sql(DB_NAME, conn, if_exists='replace', index=False)
