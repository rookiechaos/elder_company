import React from 'react'
import ReactDOM from 'react-dom/client'
import './i18n'
import App from './App'
import { AuthProvider } from './contexts/AuthContext'
import './index.css'
import { initWebVitals } from './utils/webVitals'

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

// Initialize Web Vitals tracking
initWebVitals()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)
