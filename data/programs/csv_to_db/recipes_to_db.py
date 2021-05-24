#!/usr/bin/env python3
import sqlite3
import pandas as pd


class RecipesToDB:
    def __init__(self):
        conn = sqlite3.connect('../raw_recipes/recipes1.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Recipes ("
                  "URL text Unique Primary Key, "
                  "Title text, "
                  "Rating integer, "
                  "Serving integer, "
                  "Time text, "
                  "Categories text, "
                  "Ingredients text, "
                  "Preparation text, "
                  "Nutritional_Info text);")
        conn.commit()

        r_recipes = pd.read_csv('../raw_recipes/recipes1.csv')
        r_recipes.to_sql('Recipes', conn, if_exists='replace', index=False)
