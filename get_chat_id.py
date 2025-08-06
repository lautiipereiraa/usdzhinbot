import asyncio
from telegram import Bot

BOT_TOKEN = "8220183785:AAE44NwafMabzAfKl_2glYhlLXA0OdagUoI"

async def main():
    bot = Bot(BOT_TOKEN)
    updates = await bot.get_updates()
    
    for u in updates:
        if u.message:
            print("Chat ID:", u.message.chat.id)

if __name__ == '__main__':
    asyncio.run(main())
