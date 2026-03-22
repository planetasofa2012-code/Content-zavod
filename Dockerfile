FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код проекта
COPY bot/ ./bot/
COPY ai/ ./ai/
COPY db/ ./db/
COPY publishers/ ./publishers/
COPY knowledge_base.json .

# Папка для логов
RUN mkdir -p /app/logs/dialogs

# Запуск бота
CMD ["python", "-m", "bot.main"]
