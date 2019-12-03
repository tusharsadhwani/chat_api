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
                password TEXT NOT NULL
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
                type INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                body TEXT,
                chat_id INTEGER NOT NULL,
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

        # cursor.execute(
        #     """
        #     INSERT INTO users
        #     VALUES (?, ?, ?, ?);
        #     """,
        #     (random.randrange(100_001, 1_000_000), "Tushar", "tusharsadhwani", "abcd1234")
        # )

        # query = cursor.execute("SELECT (id) FROM users WHERE username = ?;", ("tusharsadhwani",))
        # user_id = query.fetchone()[0]

        # cursor.execute(
        #     """
        #     INSERT INTO chats
        #     VALUES (?, ?, ?);
        #     """,
        #     (random.randrange(-1_999_999, -1_000_000), "Test Chat", "test")
        # )

        # query = cursor.execute("SELECT (id) FROM chats WHERE address = ?;", ("test",))
        # chat_id = query.fetchone()[0]

        # cursor.execute(
        #     """
        #     INSERT INTO updates (
        #         id,
        #         type,
        #         timestamp,
        #         body,
        #         chat_id)
        #     VALUES (?, ?, ?, ?, ?);
        #     """,
        #     (1, 0, time.time_ns(), "Testing", chat_id)
        # )

        # cursor.execute(
        #     """
        #     INSERT INTO likes
        #     VALUES (?, ?, ?);
        #     """,
        #     (chat_id, 1, user_id)
        # )

        # for i in cursor.execute("select * from chats;"):
        #     print(i)
        # for i in cursor.execute("select * from users;"):
        #     print(i)
        # for i in cursor.execute("select * from updates;"):
        #     print(i)
        # for i in cursor.execute("select * from likes;"):
        #     print(i)

        # for i in cursor.execute(
        #     """
        #     SELECT likes.chat_id, likes.user_id, updates.timestamp
        #     FROM likes JOIN updates
        #     ON likes.update_id = updates.id;
        #     """
        # ):
        #     print(i)

        conn.commit()
        conn.close()

    except sqlite3.Error as ex:
        print("Error: ", ex.args[0])
        sys.exit(1)

    finally:
        if conn:
            conn.close()
