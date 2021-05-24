import sqlite3
import pandas as pd
import csv


if __name__ == '__main__':
    conn = sqlite3.connect('../raw_recipes/Nouns_in_Ingredients.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS NounsIngredients ("
              "ID int AUTO_INCREMENT Primary Key, "
              "Noun text"
              "Occurrence int);")
    conn.commit()

    r_recipes = pd.read_csv('../raw_recipes/Nouns_in_ingredients.csv')
    r_recipes.to_sql('NounsIngredients', conn, if_exists='replace', index=False)

    nouns_conn = sqlite3.connect('../raw_recipes/Nouns_in_Ingredients.db')
    nouns_cursor = nouns_conn.cursor()
    nouns_cursor.execute("SELECT * FROM NounsIngredients;")
    noun_rows = nouns_cursor.fetchall()
    all_food = []

    for noun in noun_rows:
        if noun[0] is not None:
            food = {'Food': noun[0], 'Occurrence': noun[1]}
            all_food.append(food)

    fields = ['Food', 'Occurrence']
    filename = "../constructed_knowledge/food.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_food)
