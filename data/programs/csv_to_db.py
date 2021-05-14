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
    conn = sqlite3.connect('utils.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS Utils ("
              "ID int AUTO_INCREMENT Primary Key, "
              "Utils text, "
              "Define text, "
              "Ambiguous_Verb"
              "Prep_Verb text, "
              "Title text, "
              "Location text, "
              "Ingredient text, "
              "Recipe text, "
              "Negation_recipe text,"
              "Negation_ingredient text,"
              "Subject text);")
    conn.commit()

    r_recipes = pd.read_csv('utils.csv')
    r_recipes.to_sql('Utils', conn, if_exists='replace', index=False)

# if __name__ == "__main__":
    # conn = sqlite3.connect('found_utils.db')
    # c = conn.cursor()
    # c.execute("CREATE TABLE IF NOT EXISTS Found_Utils ("
    #           "URL text Primary Key, "
    #           "Preparation text,"
    #           "Utils text);")
    # conn.commit()
    #
    # r_recipes = pd.read_csv('found_utils.csv')
    # r_recipes.to_sql('Found_Utils', conn, if_exists='replace', index=False)
