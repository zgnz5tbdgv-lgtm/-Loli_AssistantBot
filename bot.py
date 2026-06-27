import os
import json
import httpx
import base64
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== GigaChat данные =====
CLIENT_ID = "019f0552-a332-7a2e-802b-62e96b6c8c02"
CLIENT_SECRET = "MDE5ZjA1NTItYTMzMi03YTJlLTgwMmItNjJlOTZiNmM4YzAyOmZhNmYzN2JmLWFjMDItNDQ4Ni04ODg1LWY5YmEzNDE1MjE0ZA=="

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Глобальное приложение бота (инициализируем один раз)
application = None

async def get_giga_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            data={"scope": "GIGACHAT_API_PERS", "grant_type": "client_credentials"},
            headers={
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "12345678-1234-1234-1234-1234567890ab"
            }
        )
        data = response.json()
        return data.get("access_token")

async def ask_giga(prompt: str):
    token = await get_giga_token()
    if not token:
        return "❌ Не удалось получить токен."

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "RqUID": "12345678-1234-1234-1234-1234567890ab"
            },
            json={
                "model": "GigaChat:lite",
                "messages": [
                    {"role": "system", "content": "Ты — Лоли, собака. Отвечай коротко, весело, с эмодзи 🐾."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "⚠️ Ошибка от GigaChat."

# Хендлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🐕 Гав! Я Лоли! Спрашивай что хочешь! 🦴")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    thinking = await update.message.reply_text("🐶 Дай подумать...")
    try:
        answer = await ask_giga(user_text)
    except Exception as e:
        answer = f"🐾 Ошибка: {str(e)}"
    await thinking.edit_text(answer)

# Инициализация бота
def init_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Flask routes
@app.route('/')
def health():
    return "🐕 Бот Loli работает!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)  # Лучше использовать queue
    return 'ok'

if __name__ == "__main__":
    init_bot()
    # Для локального тестирования можно добавить polling
    # application.run_polling()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
