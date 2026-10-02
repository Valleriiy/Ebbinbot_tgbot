#only database operations
import sqlite3
from scheduler import *
from datetime import datetime


# db = sqlite3.connect('vocabulary.db')
# c = db.cursor()
# c.execute("""CREATE TABLE demo (
#           id INTEGER PRIMARY KEY,
#           user_id TEXT,
#           word TEXT,
#           translation TEXT,
#           step INTEGER,
#           next_data TIMESTAMP
# )""")
# db.commit()
# db.close()



# SHOW ALL VOCABULARY
def all_the_words():
    db = sqlite3.connect('vocabulary.db')
    c = db.cursor()

    c.execute("SELECT * FROM vocabulary")
    data = c.fetchall()

    db.commit()
    db.close()

    return data



# ADD A NEW WORD TO DB
def add_new_word(w, chat_id):
    db = sqlite3.connect('vocabulary.db')
    c = db.cursor()

    c.execute("INSERT INTO vocabulary (user_id, word, translation, step, next_data) VALUES (?, ?, ?, ?, ?)",
              (chat_id, w[0], w[1], 0, next_time_to_repeat(0)) )

    db.commit()
    db.close()



# CHANGE A STEP OF LEARNING
def db_change_step_and_next_time(i_d, step):
    db = sqlite3.connect('vocabulary.db')
    c = db.cursor()

    c.execute("UPDATE vocabulary SET step = ? WHERE id = ?", (step, i_d))
    c.execute("UPDATE vocabulary SET next_data = ? WHERE id = ?", (next_time_to_repeat(step), i_d))

    db.commit()
    db.close()



# GET ANY DATA
def get_from_db(id, variable: int):
    db = sqlite3.connect('vocabulary.db')
    c = db.cursor()

    c.execute("SELECT * FROM vocabulary WHERE id = ?", ([id]))
    taken_data = c.fetchall()[0][variable]

    db.commit()
    db.close()

    return taken_data

# db = sqlite3.connect('vocabulary.db')
# c = db.cursor()

# c.execute("DELETE FROM vocabulary WHERE word = 'Treat'")

# db.commit()
# db.close()
