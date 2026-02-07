import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

# Отримуємо токен з Environment Variable
TOKEN = os.getenv("TOKEN")

# Список користувачів, яким дозволено користуватися ботом
ALLOWED_USERS = [650258742, 935498213, 1419884435]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("У тебе немає доступу до бота.")
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Введи правильний YouTube лінк.")
        return

    await update.message.reply_text("Завантаження аудіо... 🎵")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': 'www.youtube.com_cookies.txt',
        'quiet': True,
        'ffmpeg_location': r'C:\Users\xps\OneDrive\Desktop\music\bin\ffmpeg.exe'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Відправка аудіо у Telegram
        with open("audio.mp3", "rb") as f:
            await update.message.reply_audio(audio=f)

        os.remove("audio.mp3")
        await update.message.reply_text("Готово! ✅")
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка: {e}")

# Створення бота
app = ApplicationBuilder().token(TOKEN).build()

# Додаємо обробник повідомлень
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущено...")
app.run_polling()
