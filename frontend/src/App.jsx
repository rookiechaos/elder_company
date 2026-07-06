import React, { useState, useEffect, Suspense, lazy } from 'react'
import { useTranslation } from 'react-i18next'
import './App.css'
import { useAuth } from './contexts/AuthContext'
import { Languages, Users, Settings, Activity, Menu, X, Loader2, BarChart3, HelpCircle, MessageSquare, Moon, AlertTriangle, Info, LogIn } from 'lucide-react'

// Lazy load components for code splitting
const TranslationInterface = lazy(() => import('./components/TranslationInterface'))
const CustomerManagement = lazy(() => import('./components/CustomerManagement'))
const PersonalizationSettings = lazy(() => import('./components/PersonalizationSettings'))
const ActivityManagement = lazy(() => import('./components/ActivityManagement'))
const PerformanceDashboard = lazy(() => import('./components/PerformanceDashboard'))
const HelpCenter = lazy(() => import('./components/HelpCenter'))
const Onboarding = lazy(() => import('./components/Onboarding'))
const FeedbackForm = lazy(() => import('./components/FeedbackForm'))
const InstallPrompt = lazy(() => import('./components/InstallPrompt'))
const NotificationPermission = lazy(() => import('./components/NotificationPermission'))
const NightMode = lazy(() => import('./components/NightMode'))
const EmergencyRecord = lazy(() => import('./components/EmergencyRecord'))
const AboutDisclaimer = lazy(() => import('./components/AboutDisclaimer'))
const LoginRegister = lazy(() => import('./components/LoginRegister'))

function App() {
  const { t } = useTranslation(['app', 'common'])
  const { authStatus, user, refreshUser, logout, setAuthStatus } = useAuth()
  const [activePage, setActivePage] = useState('translation')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [showEmergencyRecord, setShowEmergencyRecord] = useState(false)
  const [showLoginRegister, setShowLoginRegister] = useState(false)

  useEffect(() => {
    if (authStatus !== 'authenticated') return
    const completed = localStorage.getItem('onboarding_completed')
    if (!completed) setShowOnboarding(true)
  }, [authStatus])

  const isAuthenticated = authStatus === 'authenticated'
  const currentUserId = user?.userId ?? null
  const currentUserType = user?.userType ?? 'elder'

  const pages = [
    { id: 'translation', nameKey: 'nav.translation', icon: Languages },
    { id: 'customers', nameKey: 'nav.customers', icon: Users },
    { id: 'activities', nameKey: 'nav.activities', icon: Activity },
    { id: 'settings', nameKey: 'nav.settings', icon: Settings },
    { id: 'night-mode', nameKey: 'nav.nightMode', icon: Moon },
    { id: 'performance', nameKey: 'nav.performance', icon: BarChart3 },
    { id: 'help', nameKey: 'nav.help', icon: HelpCircle },
    { id: 'about', nameKey: 'nav.about', icon: Info },
  ]

  const renderPage = () => {
    const LoadingFallback = () => (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        color: '#8b8b8b'
      }}>
        <Loader2 size={32} style={{ animation: 'spin 1s linear infinite' }} />
      </div>
    )

    switch (activePage) {
      case 'translation':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <TranslationInterface />
          </Suspense>
        )
      case 'customers':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <CustomerManagement />
          </Suspense>
        )
      case 'activities':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <ActivityManagement />
          </Suspense>
        )
      case 'settings':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <PersonalizationSettings />
          </Suspense>
        )
      case 'performance':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <PerformanceDashboard />
          </Suspense>
        )
      case 'help':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <HelpCenter />
          </Suspense>
        )
      case 'night-mode':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <NightMode userId={currentUserId} userType={currentUserType} />
          </Suspense>
        )
      case 'about':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <AboutDisclaimer />
          </Suspense>
        )
      default:
        return (
          <Suspense fallback={<LoadingFallback />}>
            <TranslationInterface />
          </Suspense>
        )
    }
  }

  if (authStatus === 'pending') {
    return (
      <div className="app-auth-loading" aria-label={t('app:verifyingSignInAria')}>
        <Loader2 size={40} style={{ animation: 'spin 1s linear infinite' }} />
        <p>{t('app:verifyingSignIn')}</p>
      </div>
    )
  }

  if (authStatus === 'unauthenticated') {
    return (
      <Suspense fallback={<div className="app-auth-loading"><Loader2 size={40} style={{ animation: 'spin 1s linear infinite' }} /></div>}>
        <LoginRegister
          isGate
          onSuccess={() => {
            setAuthStatus('authenticated')
            refreshUser()
          }}
        />
      </Suspense>
    )
  }

  if (showOnboarding) {
    return (
      <Suspense fallback={<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>{t('common:loading')}</div>}>
        <Onboarding
          onComplete={() => setShowOnboarding(false)}
          skipOnboarding={false}
        />
      </Suspense>
    )
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <button
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={t('app:toggleMenu')}
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <div className="header-title">
            <h1>{t('app:title')}</h1>
            <p>{t('app:subtitle')}</p>
          </div>
          <button
            className="header-login-button"
            onClick={() => {
              if (isAuthenticated) logout()
              else setShowLoginRegister(true)
            }}
            title={isAuthenticated ? t('app:signOut') : t('app:signInRegister')}
            aria-label={isAuthenticated ? t('app:signOut') : t('app:signInRegisterAria')}
          >
            <LogIn size={20} />
            <span>{isAuthenticated ? t('app:signOut') : t('app:signIn')}</span>
          </button>
        </div>
      </header>

      <div className="app-container">
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav className="sidebar-nav">
            {pages.map((page) => {
              const Icon = page.icon
              return (
                <button
                  key={page.id}
                  className={`nav-item ${activePage === page.id ? 'active' : ''}`}
                  onClick={() => {
                    setActivePage(page.id)
                    setSidebarOpen(false)
                  }}
                >
                  <Icon size={20} />
                  <span>{t(`app:${page.nameKey}`)}</span>
                </button>
              )
            })}
          </nav>
        </aside>

        <main className="app-main">
          {renderPage()}
        </main>
      </div>

      <button
        className="feedback-button"
        onClick={() => setShowFeedbackForm(true)}
        title={t('app:sendFeedback')}
      >
        <MessageSquare size={20} />
      </button>

      <button
        className="emergency-button"
        onClick={() => setShowEmergencyRecord(true)}
        title={t('app:recordEmergency')}
      >
        <AlertTriangle size={20} />
      </button>

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {showFeedbackForm && (
        <Suspense fallback={null}>
          <FeedbackForm onClose={() => setShowFeedbackForm(false)} />
        </Suspense>
      )}

      {showEmergencyRecord && (
        <Suspense fallback={null}>
          <EmergencyRecord
            elderId={currentUserId}
            caregiverId={currentUserId}
            onClose={() => setShowEmergencyRecord(false)}
          />
        </Suspense>
      )}

      {showLoginRegister && (
        <Suspense fallback={null}>
          <LoginRegister
            onClose={() => setShowLoginRegister(false)}
            onSuccess={() => {
              setAuthStatus('authenticated')
              refreshUser()
            }}
          />
        </Suspense>
      )}

      <Suspense fallback={null}>
        <InstallPrompt />
      </Suspense>

      <Suspense fallback={null}>
        <NotificationPermission />
      </Suspense>
    </div>
  )
}

export default App
