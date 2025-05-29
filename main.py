# Импорты
from flask import Flask, jsonify, send_file
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import uuid
import qrcode
from io import BytesIO
import asyncio

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_FOLDER = 'sessions'

app = Flask(__name__)
os.makedirs(SESSION_FOLDER, exist_ok=True)


@app.route('/auth/create', methods=['GET'])
def create_session():
    session_name = str(uuid.uuid4())

    async def generate_qr():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        qr_login = await client.qr_login()
        qr = qrcode.make(qr_login.url)
        img_io = BytesIO()
        qr.save(img_io, format='PNG')
        img_io.seek(0)

        # Сохраняем сессию
        with open(os.path.join(SESSION_FOLDER, session_name), 'w') as f:
            f.write(client.session.save())

        await client.disconnect()
        return img_io

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        img_io = loop.run_until_complete(generate_qr())
    finally:
        loop.close()

    return send_file(img_io, mimetype='image/png')


@app.route('/auth/status/<session_name>', methods=['GET'])
def check_session(session_name):
    session_path = os.path.join(SESSION_FOLDER, session_name)
    if not os.path.exists(session_path):
        return jsonify({'status': 'error', 'message': 'Session not found'}), 404

    session_string = open(session_path).read()

    async def check():
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        try:
            me = await client.get_me()
            return {
                'status': 'authenticated',
                'user': {
                    'id': me.id,
                    'username': me.username,
                    'first_name': me.first_name
                }
            }
        except Exception:
            return {'status': 'waiting'}
        finally:
            await client.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = loop.run_until_complete(check())
    finally:
        loop.close()

    return jsonify(data)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)