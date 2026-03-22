#!/bin/bash
# Деплой всего проекта на сервер одной командой
# Использование: ./deploy.sh

set -e

echo "🚀 Деплой content-zavod (бот + лендинг + nginx)..."

# Остановить старые контейнеры
echo "⏹️ Останавливаю старые контейнеры..."
docker-compose down 2>/dev/null || true

# Подтянуть последние изменения
echo "📥 Подтягиваю код из GitHub..."
git pull origin main

# Пересобрать и запустить всё
echo "🔨 Пересобираю Docker-образы..."
docker-compose up -d --build

# Проверить статус
echo "✅ Проверяю статус..."
sleep 5
docker-compose ps
echo ""
echo "📋 Логи бота (последние 10 строк):"
docker-compose logs --tail=10 bot
echo ""
echo "📋 Логи лендинга (последние 10 строк):"
docker-compose logs --tail=10 landing

echo ""
echo "🎉 Деплой завершён!"
echo "📋 Все логи: docker-compose logs -f"
echo "📋 Логи бота: docker-compose logs -f bot"
echo "📋 Логи лендинга: docker-compose logs -f landing"
echo "⏹️ Остановить: docker-compose down"
