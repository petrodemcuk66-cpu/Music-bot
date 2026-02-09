import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from yt_dlp import YoutubeDL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Змінні оточення ────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("BOT_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")
PORT         = int(os.getenv("PORT", "8443"))
COOKIES_PATH = os.getenv("COOKIES_PATH", "cookies.txt")  # fallback на файл у репозиторії

logger.info(f"DEBUG: BOT_TOKEN exists? {'yes' if BOT_TOKEN else 'NO'}")
logger.info(f"DEBUG: WEBHOOK_URL = {WEBHOOK_URL}")
logger.info(f"DEBUG: PORT = {PORT}")
logger.info(f"DEBUG: COOKIES_PATH = {COOKIES_PATH}")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не знайдено!")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не знайдено!")

# ─── Налаштування yt-dlp ────────────────────────────────────────────
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'continuedl': True,
    'retries': 10,
    'sleep_interval': 5,
    'max_sleep_interval': 15,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web', 'ios', 'web_safari'],
        }
    },
    'user_agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 14) gzip',
}

if COOKIES_PATH and os.path.isfile(COOKIES_PATH):
    ydl_opts['cookiefile'] = COOKIES_PATH
    logger.info(f"✅ Кукі підключено з: {COOKIES_PATH}")
else:
    logger.warning("⚠️ Кукі файл НЕ знайдено! Можливі помилки на age-restricted або bot-check відео.")

os.makedirs("downloads", exist_ok=True)

# ─── Хендлери ───────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Кидай посилання на відео/плейлист/шортс — завантажу як mp3 🎧\n"
        "Якщо помилка 'Sign in to confirm you’re not a bot' — онови кукі.txt"
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = " ".join(context.args)
    else:
        if update.message.text and "http" in update.message.text:
            url = update.message.text.strip()
        else:
            await update.message.reply_text("Кидай посилання 🎥")
            return

    msg = await update.message.reply_text("Завантажую... ⏳")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith(".mp3"):
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        if size_mb > 50:
            await msg.edit_text("Файл >50 МБ — Telegram не дозволяє 😔")
            os.remove(filename)
            return

        await msg.edit_text("Готово! Надсилаю... 🎧")
        await update.message.reply_audio(
            audio=open(filename, 'rb'),
            title=info.get('title', 'audio'),
            performer=info.get('uploader', 'Unknown'),
            duration=int(info.get('duration', 0) or 0),
        )

        os.remove(filename)
        await msg.delete()

    except Exception as e:
        err = str(e)
        logger.error(f"Помилка {url}: {err}", exc_info=True)
        if "Sign in to confirm" in err or "not a bot" in err:
            await msg.edit_text(
                "YouTube блокує запит: 'Sign in to confirm you’re not a bot'\n\n"
                "Рішення:\n"
                "1. Онови cookies.txt (експортуй свіжі з браузера)\n"
                "2. Поклади файл у папку проєкту → git add → commit → push → redeploy\n"
                "Або спробуй інше відео."
            )
        else:
            await msg.edit_text(f"Помилка: {err[:200]}")


def main():
    logger.info("Запускаємо бот...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    webhook_url_clean = WEBHOOK_URL.rstrip('/')
    full_webhook = f"{webhook_url_clean}/{BOT_TOKEN}"

    logger.info(f"Webhook: {full_webhook}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=full_webhook,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()