import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import yt_dlp

# Завантажуємо .env локальн
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не заданий")

ALLOWED_USERS = [650258742, 935498213, 1419884435]

# Створюємо пул потоків для блокуючих операцій
executor = ThreadPoolExecutor(max_workers=2)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Немає доступу")
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Це не YouTube лінк")
        return

    await update.message.reply_text("Завантажую...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "cookiefile": "cookies.txt",  # ставимо свій файл cookies, якщо потрібно
        "quiet": True,
    }

    loop = asyncio.get_event_loop()

    try:
        # yt-dlp виконується у окремому потоці, щоб не блокувати бота
        await loop.run_in_executor(executor, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        # Відправляємо аудіо
        with open("audio.mp3", "rb") as f:
            await update.message.reply_audio(f)

        os.remove("audio.mp3")
        await update.message.reply_text("Готово")

    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
