// Service Worker — Кухня 54 PWA
const CACHE_NAME = 'kuhnya54-v1';

// Файлы для кэширования (оффлайн-доступ)
const PRECACHE = [
  '/',
  '/dashboard',
  '/crm',
];

// Установка: кэшируем основные страницы
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// Активация: удаляем старые кэши
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Запросы: сначала сеть, потом кэш (network-first)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Сохраняем успешный ответ в кэш
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
