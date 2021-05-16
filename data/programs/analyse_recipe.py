#!/usr/bin/env python3
import sqlite3


if __name__ == "__main__":
    conn = sqlite3.connect('../raw_recipes/recipes1.db')
    c = conn.cursor()

    c.execute("SELECT * FROM Recipes;")
    rows = c.fetchall()

    for row in rows:
        if " top " in row[7].lower() and "dough" in row[7].lower():
            print(row[0], row[7])
