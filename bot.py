import os
import json
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== GigaChat данные =====
CLIENT_ID = "019f0552-a332-7a2e-802b-62e96b6c8c02"
CLIENT_SECRET = "MDE5ZjA1NTItYTMzMi03YTJlLTgwMmItNjJlOTZiNmM4YzAyOjc0MzJmNTcyLTdmMDAtNDljYi1hMzhiLTY4MzZiZDE0MzhjOA=="
SCOPE = "GIGACHAT_API_PERS"  # обычно оставляют так

# ===== Telegram токен =====
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ===== Получение токена GigaChat =====
async def get_giga_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            data={
                "scope": SCOPE,
                "grant_type": "client_credentials"
            },
            auth=(CLIENT_ID, CLIENT_SECRET),
            headers={"RqUID": "12345678-1234-1234-1234-1234567890ab"}
        )
        return response.json().get("access_token")

# ===== Запрос к GigaChat =====
async def ask_giga(prompt: str):
    token = await get_giga_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "RqUID": "12345678-1234-1234-1234-1234567890ab"
            },
            json={
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": "Ты — Лоли, собака. Отвечай коротко, весело, с эмодзи 🐾. Всегда добавляй совет про ветеринара, если вопрос про здоровье."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        data = response.json()
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

# ===== Запуск =====
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("✅ Бот с GigaChat и Лоли запущен!")
app.run_polling()
