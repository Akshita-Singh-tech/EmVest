import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import {
  apiLogin,
  apiSignup,
  apiGetMe,
  getAuthToken,
  clearAuthToken,
  type AuthUser,
} from '../services/api'
import { syncPreferencesFromBackend, syncWatchlistFromBackend } from '../services/personalizationStore'

interface AuthContextType {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, pass: string) => Promise<{ success: boolean; error?: string }>
  signup: (fullName: string, email: string, pass: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  isAuthModalOpen: boolean
  authModalTab: 'login' | 'signup'
  openAuthModal: (tab?: 'login' | 'signup') => void
  closeAuthModal: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(getAuthToken())
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false)
  const [authModalTab, setAuthModalTab] = useState<'login' | 'signup'>('login')

  const verifySession = useCallback(async () => {
    const existingToken = getAuthToken()
    if (!existingToken) {
      setUser(null)
      setIsLoading(false)
      return
    }
    try {
      const userData = await apiGetMe()
      setUser(userData)
      setToken(existingToken)
      // Sync personal preferences and watchlist from database
      void syncPreferencesFromBackend()
      void syncWatchlistFromBackend()
    } catch {
      clearAuthToken()
      setUser(null)
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void verifySession()
  }, [verifySession])

  const login = async (email: string, pass: string) => {
    try {
      const res = await apiLogin(email, pass)
      setUser(res.user)
      setToken(res.access_token)
      setIsAuthModalOpen(false)
      void syncPreferencesFromBackend()
      void syncWatchlistFromBackend()
      return { success: true }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Invalid login credentials'
      return { success: false, error: msg }
    }
  }

  const signup = async (fullName: string, email: string, pass: string) => {
    try {
      const res = await apiSignup(fullName, email, pass)
      setUser(res.user)
      setToken(res.access_token)
      setIsAuthModalOpen(false)
      void syncPreferencesFromBackend()
      void syncWatchlistFromBackend()
      return { success: true }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to register account'
      return { success: false, error: msg }
    }
  }

  const logout = () => {
    clearAuthToken()
    setUser(null)
    setToken(null)
  }

  const openAuthModal = (tab: 'login' | 'signup' = 'login') => {
    setAuthModalTab(tab)
    setIsAuthModalOpen(true)
  }

  const closeAuthModal = () => {
    setIsAuthModalOpen(false)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: Boolean(user),
        isLoading,
        login,
        signup,
        logout,
        isAuthModalOpen,
        authModalTab,
        openAuthModal,
        closeAuthModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
