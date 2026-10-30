import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

from speech import transcribe_audio
from extractor import extract_expense
from sheets import append_expense

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_TOKEN in the environment or a .env file.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    if update.message.voice:
        file = await context.bot.get_file(update.message.voice.file_id)
        file_path = "voice.ogg"
        await file.download_to_drive(file_path)

        text = transcribe_audio(file_path)

        if os.path.exists(file_path):
            os.remove(file_path)

    elif update.message.text:
        text = update.message.text

    else:
        await update.message.reply_text("Send text or voice note.")
        return

    expense = extract_expense(text)

    if expense["amount"] == 0:
        await update.message.reply_text("Couldn't detect amount. Try again.")
        return

    append_expense(expense)

    reply = f"Logged: ₹{expense['amount']} - {expense['category']}"
    await update.message.reply_text(reply)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))

    print("Bot running...")
    app.run_polling()
