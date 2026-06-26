import os
import json
import httpx
import base64
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== GigaChat данные =====
CLIENT_ID = "019f0552-a332-7a2e-802b-62e96b6c8c02"
CLIENT_SECRET = "MDE5ZjA1NTItYTMzMi03YTJlLTgwMmItNjJlOTZiNmM4YzAyOmZhNmYzN2JmLWFjMDItNDQ4Ni04ODg1LWY5YmEzNDE1MjE0ZA=="

# ===== Инициализация Flask и Telegram =====
app_flask = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") # Токен берем из переменной окружения Render

# ===== Функции для работы с GigaChat =====

async def get_giga_token():
    """Получает access-токен от GigaChat API."""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

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

async def ask_giga(prompt: str):
    """Отправляет запрос к GigaChat и возвращает ответ."""
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
        if "choices" not in data or not data["choices"]:
            return f"⚠️ Странный ответ от GigaChat:\n{data}"

        return data["choices"][0]["message"]["content"]


# ===== Хендлеры для Telegram бота =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "🐕 Гав! Я Лоли! Спрашивай что хочешь — я отвечу так, что даже кошки поймут! 🦴"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    user_text = update.message.text
    # Сначала отправляем сообщение, что бот думает, чтобы пользователь не ждал молча
    thinking_msg = await update.message.reply_text("🐶 Дай подумать...")
    
    try:
        answer = await ask_giga(user_text)
    except Exception as e:
        answer = f"🐾 Ой, лапки устали... Ошибка: {e}"
        
    # Редактируем предыдущее сообщение или отправляем новое с ответом
    await thinking_msg.edit_text(answer)


# ===== Маршруты Flask (Вебхук) =====

@app_flask.route('/')
def health():
    """Проверка работоспособности сервера для Render."""
    return "🐕 Бот Loli работает!"

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    """
    Точка входа для всех обновлений от Telegram.
    Принимает POST-запрос, преобразует его в объект Update и передает на обработку боту.
    """
    if request.method == "POST":
        # Создаем приложение бота здесь, чтобы оно было в области видимости
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Добавляем хендлеры (это можно вынести в глобальную область, но для простоты так)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        # Парсим JSON из запроса и обрабатываем его
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
        
    return 'ok'


# ===== Запуск приложения =====

if __name__ == "__main__":
    # При локальном запуске можно использовать polling для отладки
    # app = ApplicationBuilder().token(BOT_TOKEN).build()
    # app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # app.run_polling()
    
    # При запуске на сервере (Render) запускаем только Flask-приложение.
    # Процесс бота теперь встроен в него через маршрут /webhook.
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
