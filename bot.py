import os
import json
import httpx
import threading
import base64
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== GigaChat данные =====
CLIENT_ID = "019f0552-a332-7a2e-802b-62e96b6c8c02"
CLIENT_SECRET = "MDE5ZjA1NTItYTMzMi03YTJlLTgwMmItNjJlOTZiNmM4YzAyOmZhNmYzN2JmLWFjMDItNDQ4Ni04ODg1LWY5YmEzNDE1MjE0ZA=="
SCOPE = "GIGACHAT_API_PERS"

# ===== Telegram токен =====
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ===== Веб-сервер для Render =====
app_flask = Flask(__name__)

@app_flask.route('/')
def health():
    return "🐕 Бот Loli работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port, threaded=False)

# ===== Получение токена GigaChat =====
async def get_giga_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            data={
                "scope": "GIGACHAT_API_PERS",
                "grant_type": "client_credentials"
            },
            headers={
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "12345678-1234-1234-1234-1234567890ab"
            }
        )
        data = response.json()
        print("🔍 Ответ GigaChat (token):", data)
        return data.get("access_token")

# ===== Запрос к GigaChat =====
async def ask_giga(prompt: str):
    token = await get_giga_token()
    if not token:
        return "❌ Не удалось получить токен GigaChat. Проверь ключи."

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
                    {"role": "system", "content": "Ты — Лоли, собака. Отвечай коротко, весело, с эмодзи 🐾. Всегда добавляй совет про ветеринара, если вопрос про здоровье."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        data = response.json()
        print("🔍 Ответ GigaChat (chat):", data)

        if "error" in data:
            return f"❌ Ошибка GigaChat: {data['error']}"
        if "choices" not in data:
            return f"⚠️ Странный ответ от GigaChat:\n{data}"

        return data["choices"][0]["message"]["content"]

# ===== Команда /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐕 Гав! Я Лоли! Спрашивай что хочешь — я отвечу так, что даже кошки поймут! 🦴"
    )

# ===== Обработка сообщений =====
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🐶 Дай подумать...")
    try:
        answer = await ask_giga(user_text)
    except Exception as e:
        answer = f"🐾 Ой, лапки устали... Ошибка: {e}"
    await update.message.reply_text(answer)

# ===== Запуск (НОВЫЙ КОД) =====
if __name__ == "__main__":
    # Создаем Application (бота) один раз
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Добавляем хендлеры в приложение
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # --- ДОБАВЬТЕ ЭТОТ МАРШРУТ ДЛЯ ВЕБХУКА ---
    @app_flask.route('/webhook', methods=['POST'])
    def webhook():
        """
        Принимает обновления от Telegram и передает их боту на обработку.
        """
        if request.method == "POST":
            # Получаем JSON из тела запроса
            update_data = request.get_json(force=True)
            # Создаем объект Update
            update = Update.de_json(update_data, application.bot)
            # Передаем обновление в диспетчер бота для обработки
            application.process_update(update)
        return 'ok'
    
    # Запускаем только Flask-приложение.
    # Процесс бота теперь встроен в него и будет работать внутри него.
    run_flask()
