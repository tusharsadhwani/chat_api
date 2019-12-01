"""Simple Chat API"""
import random
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

CHATS = {}

@app.route('/chats', methods=['GET'])
def get_chats():
    return jsonify(list(CHATS.keys()))

@app.route('/chats/<int:chat_id>', methods=['GET'])
def get_chats_by_id(chat_id):
    return jsonify(CHATS.get(chat_id))

@app.route('/newchat', methods=['GET'])
def new_chat():
    while True:
        new_id = random.randrange(0, 1_000_000)
        if new_id not in CHATS:
            break

    CHATS[new_id] = []
    return jsonify({'id': new_id})

@app.route('/sendmessage/<int:chat_id>', methods=['GET'])
def send_message(chat_id):
    if chat_id not in CHATS:
        return jsonify({'error': 404, 'message': "chat not found"})

    msg_body = request.args.get('body') or ""
    CHATS[chat_id].append({'type': "message", 'body': msg_body})
    return redirect(f'/chats/{chat_id}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
