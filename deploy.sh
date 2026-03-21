#!/bin/bash
# Деплой бота на сервер одной командой
# Использование: ./deploy.sh

set -e

echo "🚀 Деплой content-zavod бота..."

# Остановить старый контейнер
echo "⏹️ Останавливаю старый контейнер..."
docker-compose down 2>/dev/null || true

# Подтянуть последние изменения
echo "📥 Подтягиваю код из GitHub..."
git pull origin main

# Пересобрать и запустить
echo "🔨 Пересобираю Docker-образ..."
docker-compose up -d --build

# Проверить статус
echo "✅ Проверяю статус..."
sleep 3
docker-compose ps
docker-compose logs --tail=20

echo ""
echo "🎉 Деплой завершён!"
echo "📋 Логи: docker-compose logs -f"
echo "⏹️ Остановить: docker-compose down"
