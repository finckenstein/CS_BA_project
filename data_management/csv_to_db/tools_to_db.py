#!/usr/bin/env python3
import sqlite3
import pandas as pd


class ToolsToDB:
    def __init__(self):
        conn = sqlite3.connect('/home/leander/Desktop/automatic_KB/constructed_knowledge/tools.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Tools ("
                  "ID int AUTO_INCREMENT Primary Key, "
                  "Tool text, "
                  "Location text, "
                  "Direct_Verb text, "
                  "Ambiguous_Verb text, "
                  "Implied text, "
                  "Define text, "
                  "Title text, "
                  "IsA_rel text, "
                  "Not_IsA_rel text, "
                  "Size text, "
                  "Not_size text, "
                  "Subject text, "
                  "Not_subject text, "
                  "Ingredient text, "
                  "Not_ingredient text);")
        conn.commit()

        r_recipes = pd.read_csv('/home/leander/Desktop/automatic_KB/constructed_knowledge/tools.csv')
        r_recipes.to_sql('Tools', conn, if_exists='replace', index=False)
