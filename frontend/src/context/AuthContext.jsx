import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('friday_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      authAPI.me()
        .then((res) => {
          setUser(res.data)
        })
        .catch(() => {
          localStorage.removeItem('friday_token')
          localStorage.removeItem('friday_user')
          setToken(null)
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('friday_token', access_token)
    localStorage.setItem('friday_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const signup = async (email, username, fullName, password) => {
    const res = await authAPI.signup({
      email,
      username,
      full_name: fullName,
      password,
    })
    const { access_token, user: userData } = res.data
    localStorage.setItem('friday_token', access_token)
    localStorage.setItem('friday_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('friday_token')
    localStorage.removeItem('friday_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
