import os
import json
import io
import requests
from datetime import date
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

app = Flask(__name__)

# Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Expenses")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "google-credentials.json")

openai.api_key = OPENAI_API_KEY

# Google Sheets setup (service account)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # assumes first worksheet

# Global application (we'll initialize once)
application = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    if message.voice:
        try:
            # Download voice file
            file = await context.bot.get_file(message.voice.file_id)
            audio_bytes = await file.download_as_bytearray()
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "voice.ogg"

            # Transcribe with Whisper (multilingual)
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            text = transcript_response.text

            await message.reply_text("Transcribed: " + text)

            # Extract with GPT-4o-mini (cheap & fast, multilingual)
            extraction_prompt = f"""
From this spoken text (in any language): "{text}"
Extract:
- amount: number only (e.g. 450)
- currency: code or symbol (e.g. INR, $, ₹) - default INR if unclear
- category: one word or short phrase (e.g. food, transport, shopping)
- description: short note (optional)
- date: YYYY-MM-DD or "today"

Output **JSON only**, no extra text:
{{
  "amount": float,
  "currency": str,
  "category": str,
  "description": str or null,
  "date": str
}}
"""
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.1
            )
            json_str = response.choices[0].message.content.strip()
            data = json.loads(json_str)

            # Default/fix date
            data_date = data.get("date", date.today().isoformat())
            if data_date.lower() == "today":
                data_date = date.today().isoformat()

            # Append to Google Sheet
            row = [
                data_date,
                data["amount"],
                data["currency"],
                data["category"],
                data.get("description", ""),
                text  # original transcription for reference
            ]
            sheet.append_row(row)

            reply = f"✅ Logged!\n{data['amount']} {data['currency']} → {data['category']}\nDate: {data_date}"
            if data.get("description"):
                reply += f"\nNote: {data['description']}"

            await message.reply_text(reply)

        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            print(e)

    elif message.text:
        await message.reply_text("Please send a voice note describing your expense 😊")

# -----------------------------
# Webhook Route
# -----------------------------
@app.route("/telegram-webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update_dict = request.get_json()
        update = Update.de_json(update_dict, application.bot)
        application.update_queue.put_nowait(update)
        return jsonify(success=True), 200
    return "OK", 200

# -----------------------------
# Set Webhook (call once after deploy)
# -----------------------------
@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    url = f"https://{request.host}/telegram-webhook"   # auto-detects host (Railway/Render/PythonAnywhere)
    try:
        webhook_info = application.bot.get_webhook_info()
        if webhook_info.url != url:
            application.bot.set_webhook(url=url)
            return f"Webhook set to: {url}"
        return "Webhook already set correctly"
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize bot application (once at startup)
def init_bot():
    global application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.VOICE | filters.TEXT, handle_message))

if __name__ == "__main__":
    init_bot()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)