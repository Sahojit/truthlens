import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('tl_user')) } catch { return null }
  })
  const [token, setToken] = useState(() => localStorage.getItem('tl_token'))

  useEffect(() => {
    if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    else delete api.defaults.headers.common['Authorization']
  }, [token])

  const login = (userData, accessToken) => {
    setUser(userData)
    setToken(accessToken)
    localStorage.setItem('tl_user', JSON.stringify(userData))
    localStorage.setItem('tl_token', accessToken)
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('tl_user')
    localStorage.removeItem('tl_token')
    delete api.defaults.headers.common['Authorization']
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
