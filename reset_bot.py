import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_TOKEN in the environment or a .env file.")

async def reset():
    bot = Bot(BOT_TOKEN)
    # Delete webhook (ensures polling works)
    await bot.delete_webhook()
    print("Webhook deleted. Now use polling.")

    # Get updates to clear queue
    updates = await bot.get_updates()
    print(f"Cleared {len(updates)} pending updates")

asyncio.run(reset())