from telegram.ext import Application
import asyncio
import os

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")  # или вставь вручную

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    await application.bot.set_webhook("https://loli-assistantbot.onrender.com/webhook")
    print("Webhook успешно установлен!")

if __name__ == "__main__":
    asyncio.run(main())
