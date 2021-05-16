import sqlite3
import pandas as pd

# if __name__ == "__main__":
#     conn = sqlite3.connect('recipes1.db')
#     c = conn.cursor()
#     c.execute("CREATE TABLE IF NOT EXISTS Recipes ("
#               "URL text Unique Primary Key, "
#               "Title text, "
#               "Rating integer, "
#               "Serving integer, "
#               "Time text, "
#               "Categories text, "
#               "Ingredients text, "
#               "Preparation text, "
#               "Nutritional_Info text);")
#     conn.commit()
#
#     r_recipes = pd.read_csv('recipes1.csv')
#     r_recipes.to_sql('Recipes', conn, if_exists='replace', index=False)


if __name__ == "__main__":
    conn = sqlite3.connect('../constructed_knowledge/tools.db')
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

    r_recipes = pd.read_csv('../constructed_knowledge/tools.csv')
    r_recipes.to_sql('Tools', conn, if_exists='replace', index=False)
