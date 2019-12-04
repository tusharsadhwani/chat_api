"""Functions for the backend database"""
# import random
import sqlite3
import sys
# import time

def initialize():
    """Initializes the backend database"""
    conn = None
    try:
        conn = sqlite3.connect("./chat.db")
        cursor = conn.cursor()

        cursor.executescript(
            """
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS chats;
            DROP TABLE IF EXISTS updates;
            DROP TABLE IF EXISTS likes;
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                token TEXT
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS updates (
                id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                type INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                body TEXT,
                FOREIGN KEY (chat_id)
                    REFERENCES chats (id),
                PRIMARY KEY (id, chat_id)
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS likes (
                chat_id INTEGER NOT NULL,
                update_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (chat_id)
                    REFERENCES chats (id),
                FOREIGN KEY (update_id)
                    REFERENCES updates (id),
                FOREIGN KEY (user_id)
                    REFERENCES users (id),
                PRIMARY KEY (chat_id, update_id, user_id)
            );
            """
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as ex:
        print("Error: ", ex.args[0])
        sys.exit(1)

    finally:
        if conn:
            conn.close()

def exists(query):
    """Acts as a boolean for a COUNT(*) query"""
    return bool(query.fetchone()[0])

if __name__ == "__main__":
    initialize()
