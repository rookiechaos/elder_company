import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Bell, BellOff, X } from 'lucide-react'
import './NotificationPermission.css'

function NotificationPermission() {
  const { t } = useTranslation('notification')
  const [permission, setPermission] = useState('default')
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission)
      
      if (Notification.permission === 'default') {
        const dismissed = localStorage.getItem('notification-prompt-dismissed')
        if (!dismissed) {
          const timer = setTimeout(() => {
            setShowPrompt(true)
          }, 3000)
          return () => clearTimeout(timer)
        }
      }
    }
  }, [])

  const requestPermission = async () => {
    if (!('Notification' in window)) {
      alert(t('notSupported'))
      return
    }

    try {
      const result = await Notification.requestPermission()
      setPermission(result)
      setShowPrompt(false)

      if (result === 'granted') {
        if ('serviceWorker' in navigator) {
          await navigator.serviceWorker.ready
        }
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error)
    }
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    localStorage.setItem('notification-prompt-dismissed', Date.now().toString())
  }

  const handleDisable = async () => {
    alert(t('disableHint'))
  }

  if (!('Notification' in window)) {
    return null
  }

  if (permission === 'granted') {
    return (
      <div className="notification-status granted">
        <Bell size={16} />
        <span>{t('enabled')}</span>
        <button onClick={handleDisable} className="disable-button" title={t('disableTitle')}>
          <BellOff size={14} />
        </button>
      </div>
    )
  }

  if (permission === 'denied') {
    return (
      <div className="notification-status denied">
        <BellOff size={16} />
        <span>{t('disabled')}</span>
      </div>
    )
  }

  if (!showPrompt) {
    return null
  }

  return (
    <div className="notification-prompt">
      <div className="notification-prompt-content">
        <div className="notification-icon">
          <Bell size={20} />
        </div>
        <div className="notification-text">
          <strong>{t('promptTitle')}</strong>
          <p>{t('promptDescription')}</p>
        </div>
        <div className="notification-actions">
          <button onClick={requestPermission} className="enable-button">
            {t('enable')}
          </button>
          <button onClick={handleDismiss} className="dismiss-button" aria-label={t('close')}>
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default NotificationPermission
