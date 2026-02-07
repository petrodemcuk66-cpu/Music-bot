import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

ALLOWED_USERS = [650258742, 935498213, 1419884435]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Немає доступу")
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Це не YouTube лінк")
        return

    await update.message.reply_text("⏳ Завантажую...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "cookiefile": "cookies.txt",  # переконайся, що файл дійсний
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("audio.mp3", "rb") as f:
            await update.message.reply_audio(f)

        os.remove("audio.mp3")
        await update.message.reply_text("✅ Готово")

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started")
    app.run_polling()
