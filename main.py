# Импорты
from flask import Flask, jsonify, request, send_file
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
import uuid
import qrcode
from io import BytesIO

# Настройки приложения
API_ID = os.getenv('API_ID')  # Get from https://my.telegram.org/apps   
API_HASH = os.getenv('API_HASH')  # "
SESSION_FOLDER = 'sessions'

app = Flask(__name__)
os.makedirs(SESSION_FOLDER, exist_ok=True)

# Маршруты
@app.route('/auth/create', methods=['GET'])
def create_session():
    session_name = str(uuid.uuid4())
    session_path = f"{SESSION_FOLDER}/{session_name}"
    client = TelegramClient(StringSession(), API_ID, API_HASH)

    async def generate_qr():
        await client.connect()
        qr_login = await client.qr_login()
        qr = qrcode.make(qr_login.url)
        img_io = BytesIO()
        qr.save(img_io, format='PNG')
        img_io.seek(0)
        return {
            'session': session_name,
            'qr': img_io
        }

    with client:
        data = client.loop.run_until_complete(generate_qr())
    
    return send_file(data['qr'], mimetype='image/png')

@app.route('/auth/status/<session_name>', methods=['GET'])
def check_session(session_name):
    session_path = os.path.join(SESSION_FOLDER, session_name)
    if not os.path.exists(session_path):
        return jsonify({'status': 'error', 'message': 'Session not found'}), 404

    client = TelegramClient(StringSession(open(session_path).read()), API_ID, API_HASH)

    async def check():
        await client.connect()
        try:
            me = await client.get_me()
            return {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name
            }
        except Exception as e:
            return {'status': 'waiting'}

    with client:
        data = client.loop.run_until_complete(check())
    
    if 'id' in data:
        return jsonify({'status': 'authenticated', 'user': data})
    else:
        return jsonify({'status': 'waiting'})

# Запуск сервера
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))  # Используем PORT из переменных окружения, если он есть
    app.run(debug=True, host='0.0.0.0', port=port)