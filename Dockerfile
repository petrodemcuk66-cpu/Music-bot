# Візьмемо Python 3.11
FROM python:3.11-slim

# Робоча директорія
WORKDIR /app

# Копіюємо файли
COPY main.py .
COPY .env .
COPY cookies.txt /app/cookies.txt

# Встановлюємо залежності
RUN pip install --no-cache-dir python-telegram-bot[webhooks] yt-dlp

# Створюємо папку для завантажень
RUN mkdir downloads

# Запуск бота
CMD ["python", "main.py"]
