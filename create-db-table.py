import sqlite3
conn = sqlite3.connect("project.db")
cur = conn.cursor()
# create table

query1 = """ CREATE TABLE cards (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    deckname TEXT NOT NULL,
    front TEXT,
    back TEXT
    
    
)"""

query = """CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT NOT NULL UNIQUE,
    password TEXT
)"""

# to execute the query
cur.execute(query1)
cur.execute(query)
