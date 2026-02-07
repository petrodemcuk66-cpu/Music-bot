import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import yt_dlp

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
        "cookiefile": "cookies.txt",  # якщо потрібні cookies для 18+
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # знайдемо згенерований mp3 файл
        audio_file = "audio.mp3"
        for f in os.listdir("."):
            if f.startswith("audio.") and f.endswith(".mp3"):
                audio_file = f
                break

        with open(audio_file, "rb") as f:
            await update.message.reply_audio(f)

        os.remove(audio_file)
        await update.message.reply_text("✅ Готово!")

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started")
    app.run_polling()
