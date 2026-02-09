FROM python:3.11-slim

WORKDIR /app

# Встановлюємо ffmpeg (потрібен для yt-dlp)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Створюємо папку для завантажень
RUN mkdir -p downloads

CMD ["python", "main.py"]