import { useState, useEffect } from 'react'

interface User {
  id: number
  email: string
  name: string
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = (userData: User) => {
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('user')
    setUser(null)
  }

  return {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  }
}
