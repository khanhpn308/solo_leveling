import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import * as authApi from '../api/auth'
import { clearTokens, getToken, setTokens } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [account, setAccount] = useState(null)
  const [onboardingCompleted, setOnboardingCompleted] = useState(false)
  const [loading, setLoading] = useState(true)

  const hydrateFromToken = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const me = await authApi.getMe()
      setAccount(me.account)
      setOnboardingCompleted(Boolean(me.account?.onboarding_completed))
    } catch {
      clearTokens()
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    hydrateFromToken()
  }, [hydrateFromToken])

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password)
    setTokens(data.access_token)
    const me = await authApi.getMe()
    setAccount(me.account)
    setOnboardingCompleted(Boolean(me.account?.onboarding_completed))
    return me
  }, [])

  const register = useCallback(async (email, password, displayName) => {
    const data = await authApi.register(email, password, displayName)
    setTokens(data.access_token)
    const me = await authApi.getMe()
    setAccount(me.account)
    setOnboardingCompleted(Boolean(me.account?.onboarding_completed))
    return me
  }, [])

  const logoutFn = useCallback(async () => {
    try {
      await authApi.logout()
    } catch {
      // ignore logout errors
    }
    clearTokens()
    setAccount(null)
    setOnboardingCompleted(false)
  }, [])

  const refreshAuth = useCallback(async () => {
    const me = await authApi.getMe()
    setAccount(me.account)
    setOnboardingCompleted(Boolean(me.account?.onboarding_completed))
    return me
  }, [])

  const isAuthenticated = Boolean(account)

  return (
    <AuthContext.Provider
      value={{ account, onboardingCompleted, loading, isAuthenticated, login, register, logout: logoutFn, refreshAuth }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
