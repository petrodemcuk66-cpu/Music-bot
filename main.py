import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

ALLOWED_USERS = [650258742, 935498213, 1419884435]

# Створюємо папку downloads, якщо її немає
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Немає доступу")
        return

    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Це не YouTube посилання")
        return

    await update.message.reply_text("⏳ Завантажую... (може зайняти 10–60 сек)")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",  # зберігаємо з назвою відео
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",  # 128 / 192 / 256 / 320 — на вибір
        }],
        "ffmpeg_location": r"C:\ffmpeg\bin",  # ← шлях до ПАПКИ з ffmpeg.exe та ffprobe.exe
        "cookiefile": "cookies.txt",        # розкоментуй, якщо потрібні куки
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "retries": 10,
        "noplaylist": True,  # не завантажувати плейлисти
    }

    audio_file = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # filename після шаблону outtmpl (без розширення)
            base_filename = ydl.prepare_filename(info)
            # після конвертації буде .mp3
            audio_file = base_filename.rsplit(".", 1)[0] + ".mp3"

            # Завантажуємо
            ydl.download([url])

        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Файл не знайдено: {audio_file}")

        with open(audio_file, "rb") as f:
            # Можна додати title/performer/thumbnail — якщо хочеш
            await update.message.reply_audio(
                audio=f,
                title=info.get("title", "Аудіо з YouTube"),
                performer=info.get("uploader", "YouTube"),
                # thumbnail=... (потрібно завантажити обкладинку окремо)
                timeout=90
            )

        await update.message.reply_text("✅ Готово!")

    except yt_dlp.utils.DownloadError as de:
        await update.message.reply_text(f"❌ Помилка завантаження: {str(de)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {str(e)}")

    finally:
        # Прибираємо всі можливі тимчасові файли
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass
        # Якщо щось залишилося з .webm / .m4a / .opus тощо
        for ext in [".webm", ".m4a", ".opus", ".mp4", ".part"]:
            temp_file = audio_file.replace(".mp3", ext) if audio_file else None
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


if __name__ == "__main__":
    if not TOKEN:
        print("ПОМИЛКА: TOKEN не знайдено в .env файлі!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущено...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)