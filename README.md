# Expenses Tracker

A Telegram bot that records expenses in Google Sheets. Send a text message or a
voice note describing a purchase; the bot extracts the amount and category and
adds the expense to your spreadsheet. Voice notes are transcribed locally with
faster-whisper.

## Requirements

- Python 3.10 or later
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Google Cloud service account with the Google Sheets and Google Drive APIs
  enabled
- FFmpeg installed and available on `PATH` (used to convert Telegram voice
  notes)

## Setup

1. Clone the repository and install its Python dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Create a Telegram bot with BotFather and save its token in a `.env` file in
   the project directory:

   ```dotenv
   TELEGRAM_TOKEN=your-telegram-bot-token
   ```

   Keep this file private; it is excluded from Git.

3. Create a Google Cloud service account, enable the Google Sheets and Google
   Drive APIs, and download its JSON key as `credentials.json` in the project
   directory. Share the target spreadsheet with the service account's email
   address, granting it edit access. Never commit the credentials file.

4. Create a Google spreadsheet named **Expenses Tracker**. The bot uses its
   first worksheet and appends rows with these fields:
   `date`, `amount`, `category`, `description`, and `raw_text`.

5. Install FFmpeg for your operating system and verify that the `ffmpeg`
   executable is available from the terminal.

## Run

Start the bot in polling mode:

```powershell
python bot.py
```

The first voice transcription may take longer because faster-whisper downloads
its model. Send text or a voice note to your bot in Telegram to log an expense.

To delete the bot's webhook and clear pending updates before polling, run:

```powershell
python reset_bot.py
```

## Configuration and security

- `TELEGRAM_TOKEN` is loaded from the process environment or `.env`.
- `sheets.py` reads the Google service-account key from `credentials.json`.
- Do not commit bot tokens, Google service-account keys, `.env` files, or other
  credentials. If a token or key has been exposed, revoke it and create a new
  one with its provider.
