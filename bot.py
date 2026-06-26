from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 8894519316:AAEhDEDI4uGdBDhzfmV6kPEqA7fUEWYMKkA /revoke) 
BOT_TOKEN = "8894519316:AAEhDEDI4uGdBDhzfmV6kPEqA7fUEWYMKkA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот! 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Ты написал: {user_text}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("✅ Бот запущен и слушает сообщения!")
app.run_polling()
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

#8894519316:AAEhDEDI4uGdBDhzfmV6kPEqA7fUEWYMKkA 
BOT_TOKEN = "8894519316:AAEhDEDI4uGdBDhzfmV6kPEqA7fUEWYMKkA"

# Настройка прокси (если используешь VPN)
# Для большинства VPN настройки такие:
proxy_url = "socks5://127.0.0.1:1080"  # или http://127.0.0.1:10808

# Создаём запрос с прокси
request = HTTPXRequest(proxy_url=proxy_url)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот! 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Ты написал: {user_text}")

# Подключаем бота с прокси
app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("✅ Бот запущен и слушает сообщения!")
app.run_polling()
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import httpx

BOT_TOKEN = "8894519316:AAEhDEDI4uGdBDhzfmV6kPEqA7fUEWYMKkA"

# Прокси для твоего VPN (HTTP, порт 1080 - самый частый)
proxy_url = "http://127.0.0.1:1080"

# Создаём клиент с прокси
transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
http_client = httpx.AsyncClient(transport=transport)

# Передаём клиент в бота
request = HTTPXRequest(client=http_client)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот! 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Ты написал: {user_text}")

app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("✅ Бот запущен и слушает сообщения!")
app.run_polling()