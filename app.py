"""Simple Chat API"""
import random
import sqlite3
from flask import Flask, jsonify, request, abort

import db
import util

app = Flask(__name__)
conn = sqlite3.connect("./chat.db", check_same_thread=False)
cursor = conn.cursor()

@app.route('/signup', methods=['GET'])
def signup():
    required_args = ('name', 'username', 'password')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    name = request.args['name']
    username = request.args['username']
    password = request.args['password']

    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE username = ?;
        """,
        (username,)
    )
    if db.exists(query):
        return jsonify(error=401, message="User with this username already exists")

    cursor.execute(
        """
        INSERT INTO users (
            id, name, username, password)
        VALUES (?, ?, ?, ?);
        """,
        (
            random.randrange(100_001, 1_000_000),
            name,
            username,
            password,
        )
    )
    conn.commit()

    return jsonify(success=True, message="Account successfully created")

@app.route('/login', methods=['GET'])
def login():
    required_args = ('username', 'password')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    username = request.args['username']
    password = request.args['password']

    print(username, password)

    query = cursor.execute(
        """
        SELECT password
        FROM users
        WHERE username = ?;
        """,
        (username,)
    )
    result = query.fetchone()
    if result is None:
        return jsonify(error=404, message="Invalid username or password")

    db_password = result[0]
    print(db_password)
    if password != db_password:
        return jsonify(error=404, message="Invalid password")

    new_token = util.generate_token()
    cursor.execute(
        """
        UPDATE users
        SET token = ?
        WHERE username = ?;
        """,
        (new_token, username)
    )
    conn.commit()

    return jsonify(token=new_token, message="Successfully logged in")


# @app.route('/chats', methods=['GET'])
# def get_chats():
#     query = cursor.execute()
#     return jsonify(list(CHATS.keys()))

# @app.route('/chats/<int:chat_id>', methods=['GET'])
# def get_chats_by_id(chat_id):
#     return jsonify(CHATS.get(chat_id))

# @app.route('/newchat', methods=['GET'])
# def new_chat():
#     while True:
#         new_id = random.randrange(0, 1_000_000)
#         if new_id not in CHATS:
#             break

#     CHATS[new_id] = []
#     return jsonify({'id': new_id})

# @app.route('/sendmessage/<int:chat_id>', methods=['GET'])
# def send_message(chat_id):
#     if chat_id not in CHATS:
#         return jsonify({'error': 404, 'message': "chat not found"})

#     msg_body = request.args.get('body') or ""
#     CHATS[chat_id].append({'type': "message", 'message': {'body': msg_body}})
#     return redirect(f'/chats/{chat_id}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
