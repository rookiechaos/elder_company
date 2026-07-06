import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Download, X } from 'lucide-react'
import './InstallPrompt.css'

function InstallPrompt() {
  const { t } = useTranslation('installPrompt')
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return
    }

    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setShowPrompt(true)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    const dismissed = localStorage.getItem('pwa-install-dismissed')
    if (dismissed) {
      const dismissedTime = parseInt(dismissed)
      const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24)
      if (daysSinceDismissed < 7) {
        setShowPrompt(false)
      }
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) return

    deferredPrompt.prompt()
    await deferredPrompt.userChoice

    setDeferredPrompt(null)
    setShowPrompt(false)
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    localStorage.setItem('pwa-install-dismissed', Date.now().toString())
  }

  if (!showPrompt) return null

  return (
    <div className="install-prompt">
      <div className="install-prompt-content">
        <div className="install-icon">
          <Download size={24} />
        </div>
        <div className="install-text">
          <strong>{t('title')}</strong>
          <p>{t('description')}</p>
        </div>
        <div className="install-actions">
          <button onClick={handleInstall} className="install-button">
            {t('install')}
          </button>
          <button onClick={handleDismiss} className="dismiss-button" aria-label={t('close')}>
            <X size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default InstallPrompt
