"""Simple Chat API"""
import configparser
import random
import sqlite3
import time
import httplib2
from flask import Flask, jsonify, request, abort

import db
import util
import verify

app = Flask(__name__)
conn = sqlite3.connect("./chat.db", check_same_thread=False)
cursor = conn.cursor()


@app.route('/signup', methods=['GET'])
def signup():
    '''Creates a new user via email, username and password'''
    required_args = ('name', 'email', 'username', 'password')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    name = request.args['name']
    email = request.args['email']
    username = request.args['username'].lower()
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
        return jsonify(
            error=401, message="User with this username already exists")

    config = configparser.ConfigParser()
    config.read('./.settings')

    domain = config['settings']['domain'].rstrip('/')
    verification_code = util.generate_token()
    link = f'{domain}/verify?token={verification_code}'
    try:
        verify.send_verification_email(email, link)
    except httplib2.ServerNotFoundError:
        return jsonify(error=404, message="Unable to reach Server")

    cursor.execute(
        """
        INSERT INTO users (
            id, name, email, username, password, verification_code)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            random.randrange(100_001, 1_000_000),
            name,
            email,
            username,
            password,
            verification_code
        )
    )
    conn.commit()

    return jsonify(success=True, message="Verification email sent")


@app.route('/verify', methods=['GET'])
def verify_email():
    '''Verifies a user account by the verification code'''
    required_args = ('token',)
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    verificaton_code = request.args['token']

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE verification_code = ?;
        """,
        (verificaton_code,)
    )
    result = query.fetchone()

    if result is None:
        return jsonify(error=401, message="Invalid verification code")

    user_id = result[0]

    cursor.execute(
        """
        UPDATE users
        SET verified = 1
        WHERE id = ?;
        """,
        (user_id,)
    )
    conn.commit()

    return jsonify(success=True, message="Email verified")


@app.route('/login', methods=['GET'])
def login():
    '''Logs a user in by username and password, and returns an access token'''
    required_args = ('username', 'password')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    username = request.args['username'].lower()
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

    query = cursor.execute(
        """
        SELECT verified
        FROM users
        WHERE username = ?;
        """,
        (username,)
    )
    verified = bool(query.fetchone()[0])

    if not verified:
        return jsonify(error=401, message="Your email isn't verified yet")

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


@app.route('/newchat', methods=['GET'])
def new_chat():
    '''Creates a new group chat and adds you in it'''
    required_args = ('token', 'name', 'address')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    token = request.args['token']
    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    if not db.exists(query):
        return jsonify(error=401, message="Invalid token")

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    user_id = query.fetchone()[0]

    name = request.args['name']
    address = request.args['address'].lower()

    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM chats
        WHERE address = ?;
        """,
        (address,)
    )
    if db.exists(query):
        return jsonify(error=401, message="Chat address already in use")

    while True:
        chat_id = random.randrange(-1_999_999, -1_000_000)
        query = cursor.execute(
            """
            SELECT COUNT(*)
            FROM chats
            WHERE id = ?;
            """,
            (chat_id,)
        )
        if not db.exists(query):
            break

    cursor.execute(
        """
        INSERT INTO chats
        VALUES (?, ?, ?);
        """,
        (chat_id, name, address)
    )
    cursor.execute(
        """
        INSERT INTO updates (
            id, user_id, chat_id, type, timestamp)
        VALUES (?, ?, ?, ?, ?);
        """,
        (1, user_id, chat_id, 1, time.time_ns())
    )
    conn.commit()

    return jsonify(id=chat_id)


@app.route('/chats', methods=['GET'])
def get_chats():
    '''Returns a list of the chats' information a user is in'''
    required_args = ('token',)
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    token = request.args['token']
    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    if not db.exists(query):
        return jsonify(error=401, message="Invalid token")

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    user_id = query.fetchone()[0]

    query = cursor.execute(
        """
        SELECT updates.chat_id, chats.name
        FROM updates
        INNER JOIN chats
        ON updates.chat_id = chats.id
        WHERE updates.user_id = ?
        GROUP BY chat_id;
        """,
        (user_id,)
    )
    result = [[row[0], row[1]] for row in query.fetchall()]
    return jsonify(result)


@app.route('/chats/<string:chat_id>', methods=['GET'])
def get_chats_by_id(chat_id):
    '''Returns a chat's list of messages'''
    try:
        chat_id = int(chat_id)
    except ValueError:
        return abort(401)

    required_args = ('token',)
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    token = request.args['token']
    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    if not db.exists(query):
        return jsonify(error=401, message="Invalid token")

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    user_id = query.fetchone()[0]

    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM updates
        WHERE chat_id = ?
        AND user_id = ?;
        """,
        (chat_id, user_id)
    )
    if not db.exists(query):
        return jsonify(error=401, message="You are unauthorized to view this chat")

    query = cursor.execute(
        """
        SELECT
            updates.id, updates.timestamp, updates.type, updates.body,
            users.id, users.name, users.username
        FROM updates
        INNER JOIN users
        ON updates.user_id = users.id
        WHERE chat_id = ?
        ORDER BY updates.id;
        """,
        (chat_id,)
    )
    updates = query.fetchall()
    return jsonify(list(updates))


@app.route('/joinchat/<string:address>', methods=['GET'])
def join_chat(address):
    '''Joins the user into a chat'''
    required_args = ('token',)
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    token = request.args['token']
    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    if not db.exists(query):
        return jsonify(error=401, message="Invalid token")

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    user_id = query.fetchone()[0]

    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM chats
        WHERE address = ?;
        """,
        (address,)
    )
    if not db.exists(query):
        return jsonify(error=404, message="This chat does not exist")

    query = cursor.execute(
        """
        SELECT id
        FROM chats
        WHERE address = ?;
        """,
        (address,)
    )
    chat_id = query.fetchone()[0]

    query = cursor.execute(
        """
        SELECT id
        FROM updates
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT 1;
        """,
        (chat_id,)
    )
    latest_update_id = query.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO updates (
            id, user_id, chat_id, type, timestamp)
        VALUES (?, ?, ?, ?, ?);
        """,
        (latest_update_id+1, user_id, chat_id, 1, time.time_ns())
    )
    conn.commit()

    return jsonify(success=True)


@app.route('/sendmessage', methods=['GET'])
def send_message():
    '''Sends a message in a chat'''
    required_args = ('token', 'chat_id', 'message')
    if any(arg not in request.args for arg in required_args):
        return abort(401)

    token = request.args['token']
    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    if not db.exists(query):
        return jsonify(error=401, message="Invalid token")

    query = cursor.execute(
        """
        SELECT id
        FROM users
        WHERE token = ?;
        """,
        (token,)
    )
    user_id = query.fetchone()[0]

    chat_id = request.args['chat_id']
    try:
        chat_id = int(chat_id)
    except ValueError:
        return abort(401)

    msg_body = request.args['message']

    query = cursor.execute(
        """
        SELECT COUNT(*)
        FROM updates
        WHERE chat_id = ?
        AND user_id = ?;
        """,
        (chat_id, user_id)
    )
    if not db.exists(query):
        return jsonify(error=401, message="You are unauthorized to view this chat")

    query = cursor.execute(
        """
        SELECT id
        FROM updates
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT 1;
        """,
        (chat_id,)
    )
    latest_update_id = query.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO updates (
            id, user_id, chat_id, type, timestamp, body)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (latest_update_id+1, user_id, chat_id, 0, time.time_ns(), msg_body)
    )
    conn.commit()

    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
