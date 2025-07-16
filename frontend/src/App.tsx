import { useState, useEffect } from 'react'
import { ThemeProvider } from '@/components/theme-provider'
import AppHeader from '@/components/layout/AppHeader'
import WelcomeScreen from '@/components/auth/WelcomeScreen'
import LoginDialog from '@/components/auth/LoginDialog'
import { useAuth } from '@/hooks/useAuth'

import './App.css'

function App() {
  const { user, login, logout, isLoading } = useAuth()
  const [showLogin, setShowLogin] = useState(false)

  // Show login dialog if user is not authenticated and not loading
  useEffect(() => {
    if (!isLoading && !user) {
      setShowLogin(true)
    }
  }, [isLoading, user])

  const handleLoginSuccess = (userData: {
    id: number
    email: string
    name: string
  }) => {
    login(userData)
    setShowLogin(false)
  }

  const handleLogout = () => {
    logout()
    setShowLogin(true)
  }

  if (isLoading) {
    return (
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <div className="h-[100svh] bg-background text-foreground flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>Loading...</p>
          </div>
        </div>
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="h-[100svh] bg-background text-foreground">
        <AppHeader user={user} onLogout={handleLogout} />

        <main className="container mx-auto p-4">
          <WelcomeScreen user={user} onLogin={() => setShowLogin(true)} />
        </main>

        <LoginDialog
          isOpen={showLogin}
          onClose={() => setShowLogin(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      </div>
    </ThemeProvider>
  )
}

export default App
