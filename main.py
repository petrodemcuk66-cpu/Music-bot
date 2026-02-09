import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Завантаження токена з .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Список користувачів, які можуть користуватися ботом
ALLOWED_USERS = [650258742, 935498213, 1419884435]

# Папка для завантажень
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Немає доступу")
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Це не YouTube посилання")
        return

    await update.message.reply_text("⏳ Завантажую... (може зайняти 10–60 сек)")

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ffmpeg_location": r"C:\Users\xps\OneDrive\Desktop\music\ffmpeg.exe",  # шлях до ffmpeg на Windows
        "quiet": True,
        "no_warnings": True,
        "retries": 10,
        "noplaylist": True,
        "ignoreerrors": True,
    }

    audio_file = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise ValueError("Не вдалося отримати інформацію про відео")
            base = ydl.prepare_filename(info)
            audio_file = base.rsplit(".", 1)[0] + ".mp3"
            ydl.download([url])

        if not os.path.exists(audio_file):
            raise FileNotFoundError("MP3 файл не створився")

        if os.path.getsize(audio_file) > 50 * 1024 * 1024:
            raise ValueError("Файл > 50MB (ліміт Telegram)")

        # Відправка аудіо без аргументу timeout
        with open(audio_file, "rb") as f:
            await update.message.reply_audio(
                audio=f,
                title=info.get("title", "YouTube Audio"),
                performer=info.get("uploader", "YouTube")
            )

        await update.message.reply_text("✅ Готово!")

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")

    finally:
        # Видаляємо файл після відправки
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass


if __name__ == "__main__":
    if not TOKEN:
        print("❌ TOKEN не знайдено")
        exit(1)

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(30)
        .write_timeout(180)
        .connect_timeout(15)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot started")
    app.run_polling()
