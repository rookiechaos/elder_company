import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { X, LogIn, UserPlus } from 'lucide-react'
import './LoginRegister.css'

/**
 * Login / registration modal.
 * On success, stores auth_token and user_id in localStorage and calls onSuccess.
 * isGate: gate mode — user must sign in before using the app; close button is hidden.
 */
const LoginRegister = ({ onClose, onSuccess, isGate = false }) => {
  const { t } = useTranslation(['auth', 'common'])
  const [mode, setMode] = useState('login')
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [userId, setUserId] = useState('')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    if (!identifier.trim() || !password) {
      setError(t('auth:credentialsRequired'))
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', {
        identifier: identifier.trim(),
        password
      })
      if (data.token) {
        localStorage.setItem('auth_token', data.token)
        if (data.user?.user_id) localStorage.setItem('user_id', data.user.user_id)
        onSuccess?.(data.user)
        onClose?.()
      }
    } catch (err) {
      setError(err.message || t('auth:loginFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    const uid = userId.trim()
    if (!uid) {
      setError(t('auth:userIdRequired'))
      return
    }
    if (!password) {
      setError(t('auth:passwordRequired'))
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', {
        user_id: uid,
        email: email.trim() || undefined,
        username: username.trim() || undefined,
        password,
        auth_method: 'password'
      })
      if (data.token) {
        localStorage.setItem('auth_token', data.token)
        if (data.user?.user_id) localStorage.setItem('user_id', data.user.user_id)
        onSuccess?.(data.user)
        onClose?.()
      }
    } catch (err) {
      setError(err.message || t('auth:registrationFailed'))
    } finally {
      setLoading(false)
    }
  }

  const submit = mode === 'login' ? handleLogin : handleRegister

  return (
    <div className={`login-register-overlay ${isGate ? 'login-register-gate' : ''}`} onClick={isGate ? undefined : onClose}>
      <div className="login-register-container" onClick={e => e.stopPropagation()}>
        <div className="login-register-header">
          <h2>{mode === 'login' ? t('auth:signIn') : t('auth:register')}</h2>
          {!isGate && onClose && (
            <button type="button" className="login-register-close" onClick={onClose} aria-label={t('auth:close')}>
              <X size={20} />
            </button>
          )}
        </div>
        <form onSubmit={submit} className="login-register-form">
          {error && <div className="login-register-error">{error}</div>}
          {mode === 'login' ? (
            <>
              <div className="form-group">
                <label>{t('auth:emailUsernamePhone')}</label>
                <input
                  type="text"
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                  placeholder={t('auth:enterIdentifier')}
                  autoComplete="username"
                />
              </div>
              <div className="form-group">
                <label>{t('auth:password')}</label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={t('auth:enterPassword')}
                  autoComplete="current-password"
                />
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>{t('auth:userId')} <span className="required">*</span></label>
                <input
                  type="text"
                  value={userId}
                  onChange={e => setUserId(e.target.value)}
                  placeholder={t('auth:userIdPlaceholder')}
                />
              </div>
              <div className="form-group">
                <label>{t('auth:username')}</label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder={t('common:optional')}
                />
              </div>
              <div className="form-group">
                <label>{t('auth:email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder={t('common:optional')}
                />
              </div>
              <div className="form-group">
                <label>{t('auth:password')} <span className="required">*</span></label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={t('auth:passwordPlaceholder')}
                  autoComplete="new-password"
                />
              </div>
            </>
          )}
          <div className="login-register-actions">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t('auth:processing') : (mode === 'login' ? t('auth:signIn') : t('auth:register'))}
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
            >
              {mode === 'login' ? (
                <> <UserPlus size={16} /> {t('auth:createAccount')} </>
              ) : (
                <> <LogIn size={16} /> {t('auth:signIn')} </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginRegister
