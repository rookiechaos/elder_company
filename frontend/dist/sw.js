// Service Worker for Elder Company - 照护协同平台
const CACHE_VERSION = 'v2.1.1'
const CACHE_NAME = `elder-company-${CACHE_VERSION}`
const STATIC_CACHE = `elder-company-static-${CACHE_VERSION}`
const API_CACHE = `elder-company-api-${CACHE_VERSION}`
const API_CACHE_TTL = 5 * 60 * 1000 // 5 minutes

// Resources to cache on install
const urlsToCache = [
  '/',
  '/index.html',
  '/offline.html',
  '/src/main.jsx',
  '/src/App.jsx',
  '/src/App.css',
  '/src/index.css'
]

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...')
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static resources')
        return cache.addAll(urlsToCache)
      })
      .then(() => self.skipWaiting())
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...')
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== STATIC_CACHE && 
              cacheName !== API_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    }).then(() => self.clients.claim())
  )
})

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }

  // Skip API calls (they should always go to network first)
  if (url.pathname.startsWith('/api/')) {
    // Network-first strategy with cache fallback
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Only cache successful GET responses
          if (response.status === 200 && request.method === 'GET') {
            const responseClone = response.clone()
            caches.open(API_CACHE).then((cache) => {
              // Store with timestamp in headers for TTL checking
              const headers = new Headers(responseClone.headers)
              headers.set('sw-cached-at', Date.now().toString())
              cache.put(request, new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: headers
              }))
            })
          }
          return response
        })
        .catch(() => {
          // If network fails, try cache
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              const cachedAt = cachedResponse.headers.get('sw-cached-at')
              // Check if cache is still valid (within TTL)
              if (cachedAt && (Date.now() - parseInt(cachedAt)) < API_CACHE_TTL) {
                return cachedResponse
              }
            }
            // Return offline response for API calls
            return new Response(
              JSON.stringify({ error: 'Offline', message: '网络不可用，请检查连接' }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
              }
            )
          })
        })
    )
    return
  }

  // For static resources, use cache-first strategy
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse
        }

        return fetch(request).then((response) => {
          // Don't cache if not a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response
          }

          // Clone the response
          const responseToCache = response.clone()

          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(request, responseToCache)
          })

          return response
        })
      })
      .catch(() => {
        // Return offline page if available
        if (request.destination === 'document') {
          return caches.match('/offline.html').catch(() => {
            return caches.match('/index.html')
          })
        }
        return new Response('Offline', { status: 503 })
      })
  )
})

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag)
  
  if (event.tag === 'sync-translations') {
    event.waitUntil(syncTranslations())
  }
})

// Sync translations when back online
async function syncTranslations() {
  // This would sync any pending translations
  console.log('[SW] Syncing translations...')
}

// Push notifications (for future use)
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received')
  
  const options = {
    body: event.data ? event.data.text() : '新消息',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png', // Use icon as badge fallback
    vibrate: [200, 100, 200],
    tag: 'elder-company-notification'
  }

  event.waitUntil(
    self.registration.showNotification('Elder Company', options)
  )
})

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked')
  event.notification.close()

  event.waitUntil(
    clients.openWindow('/')
  )
})
