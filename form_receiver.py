# bohdi1/kosa-bot/form_receiver.py
from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

app = Flask(__name__)

# Беремо токен та ID чату з оточення
TELEGRAM_BOT_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

@app.route('/send_form', methods=['POST'])
def send_form():
    # Перевіряємо, чи є токен та ID
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        return 'Error: Telegram Bot Token or Chat ID is not configured.', 500

    name = request.form.get('name')
    phone = request.form.get('phone')
    message = request.form.get('message')
    text = f"Нова заявка з сайту:\nІм'я: {name}\nТелефон: {phone}\nПовідомлення: {message}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={'chat_id': CHAT_ID, 'text': text})
        response.raise_for_status()  # Перевірка на помилки HTTP
        return 'OK'
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        return 'Error sending message', 500

if __name__ == '__main__':
    app.run(port=5000)
