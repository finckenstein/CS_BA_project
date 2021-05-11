import sqlite3
import ast

# def ingredients_are_pizza(ingredients):
#     for ing_list in ingredients:
#         for ingredient in ingredients[ing_list]:
#             if "pizza dough" in ingredient.lower():
#                 return True
#             elif "pizza crust" in ingredient.lower():
#                 return True
#             elif "flour" in ingredient.lower():
#                 return True
#             elif "yeast" in ingredient.lower():
#                 return True
#
#     return False


if __name__ == "__main__":
    conn = sqlite3.connect('found_utils.db')
    c = conn.cursor()

    c.execute("SELECT * FROM Found_Utils;")
    rows = c.fetchall()
    s = 0
    temp_sentence = ""

    for row in rows:
        print(s)
        if s == 25:
            break
        else:
            print(row[0])
            for char in row[1]:
                temp_sentence += char
                if char == '.':
                    print(temp_sentence)
                    temp_sentence = ""
            print(row[2] + "\n")
        s += 1

# if __name__ == "__main__":
#     conn = sqlite3.connect('utils.db')
#     c = conn.cursor()
#
#     c.execute("SELECT * FROM Utils;")
#     rows = c.fetchall()
#
#     print(str(rows))
