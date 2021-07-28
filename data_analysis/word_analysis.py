#!/usr/bin/env python3
import sqlite3


if __name__ == "__main__":
    conn = sqlite3.connect('/home/leander/Desktop/automatic_KB/recipes/db/recipes_with_1to1_video.db')
    c = conn.cursor()

    c.execute("SELECT * FROM RecipesWith1To1Video;")
    rows = c.fetchall()

    for row in rows:
        if " coat " in row[7].lower() and not (" toss " in row[7].lower()):
            print(row[0], row[7])
