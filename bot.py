import asyncio
import httpx
import base64
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CLIENT_ID = os.getenv("GIGA_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGA_CLIENT_SECRET")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_giga_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()
    
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            data={"scope": "GIGACHAT_API_PERS", "grant_type": "client_credentials"},
            headers={
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        return r.json().get("access_token")

async def ask_giga(prompt: str):
    token = await get_giga_token()
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            json={
                "model": "GigaChat:lite",
                "messages": [
                    {"role": "system", "content": "Ты — Лоли, добрая весёлая собака. Отвечай мило, коротко, с эмодзи 🐾. Если вопрос про здоровье — посоветуй ветеринара."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return r.json()["choices"][0]["message"]["content"]

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🐕 Гав! Я Лоли! Спрашивай меня о чём угодно! 🦴")

@dp.message()
async def chat(message: types.Message):
    thinking = await message.answer("🐶 Лоли думает...")
    try:
        answer = await ask_giga(message.text)
    except Exception as e:
        answer = f"🐾 Ой, лапки запутались... {str(e)}"
    await thinking.edit_text(answer)

async def main():
    print("🤖 Бот Лоли запущен! Напиши ему /start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
