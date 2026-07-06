import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [authStatus, setAuthStatus] = useState('pending')
  const [user, setUser] = useState({ userId: null, userType: 'elder' })

  const refreshUser = useCallback(() => {
    const userId = localStorage.getItem('user_id')
    const userType = localStorage.getItem('user_type') || 'elder'
    setUser({ userId: userId || null, userType })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_id')
    setUser({ userId: null, userType: 'elder' })
    setAuthStatus('unauthenticated')
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      setAuthStatus('unauthenticated')
      return
    }
    api.get('/auth/me')
      .then((res) => {
        if (res.data?.user_id) {
          localStorage.setItem('user_id', res.data.user_id)
          refreshUser()
        }
        setAuthStatus('authenticated')
      })
      .catch(() => {
        logout()
      })
  }, [refreshUser, logout])

  // React to 401 from api layer (token cleared there; sync UI state)
  useEffect(() => {
    const onLogout = () => logout()
    window.addEventListener('auth:logout', onLogout)
    return () => window.removeEventListener('auth:logout', onLogout)
  }, [logout])

  const value = {
    authStatus,
    user,
    refreshUser,
    logout,
    setAuthStatus,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
