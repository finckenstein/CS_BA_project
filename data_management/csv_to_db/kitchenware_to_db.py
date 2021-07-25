#!/usr/bin/env python3
import sqlite3
import pandas as pd


class KitchenwareToDB:
    def __init__(self):
        conn = sqlite3.connect("../constructed_knowledge/kitchenware.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Kitchenware ("
                  "Verb text Unique Primary Key, "
                  "Kitchenware text, "
                  "Default_Kitchenware text);")
        conn.commit()

        r_recipes = pd.read_csv("../constructed_knowledge/kitchenware.csv")
        r_recipes.to_sql('Kitchenware', conn, if_exists='replace', index=False)
