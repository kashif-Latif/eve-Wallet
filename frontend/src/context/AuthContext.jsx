import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const { data } = await authApi.getProfile()
        const userData = data.data || data
        setUser(userData)
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
        setIsAuthenticated(false)
      }
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (credentials) => {
    const { data } = await authApi.login(credentials)
    const responseData = data.data || data
    localStorage.setItem('access_token', responseData.access)
    localStorage.setItem('refresh_token', responseData.refresh)
    if (responseData.user) {
      setUser(responseData.user)
      localStorage.setItem('user', JSON.stringify(responseData.user))
    }
    setIsAuthenticated(true)
    return responseData
  }

  const register = async (userData) => {
    const { data } = await authApi.register(userData)
    const responseData = data.data || data
    if (responseData.access) {
      localStorage.setItem('access_token', responseData.access)
      localStorage.setItem('refresh_token', responseData.refresh)
      if (responseData.user) {
        setUser(responseData.user)
        localStorage.setItem('user', JSON.stringify(responseData.user))
      }
      setIsAuthenticated(true)
    }
    return responseData
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch {
      // ignore
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
  }

  const isAdmin = user?.role === 'admin' || user?.role === 'superadmin'

  return (
    <AuthContext.Provider value={{
      user, setUser, loading, isAuthenticated, isAdmin,
      login, register, logout, checkAuth
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

export default AuthContext
