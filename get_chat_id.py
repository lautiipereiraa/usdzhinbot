import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(BOT_TOKEN)
    updates = await bot.get_updates()
    
    for u in updates:
        if u.message:
            print("Chat ID:", u.message.chat.id)

if __name__ == '__main__':
    asyncio.run(main())
