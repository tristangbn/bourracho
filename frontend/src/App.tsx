import { useState, useEffect } from 'react'

import { client } from '@/api/generated/client.gen'
import type { Conversation, User } from '@/api/generated'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'
import WelcomeScreen from '@/components/auth/WelcomeScreen'
import LoginDialog from '@/components/auth/LoginDialog'
import ChatPage from '@/components/chat/ChatPage'
import { useAuth } from '@/hooks/useAuth'

import './App.css'

client.setConfig({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', // Fallback
})

function App() {
  const { user, login, logout, isLoading } = useAuth()
  const [showLogin, setShowLogin] = useState(false)
  const [currentConversation, setCurrentConversation] =
    useState<Conversation | null>(null)

  // Show login dialog if user is not authenticated and not loading
  useEffect(() => {
    if (!isLoading && !user) {
      setShowLogin(true)
    }
  }, [isLoading, user])

  const handleLoginSuccess = (userData: User) => {
    login(userData)
    setShowLogin(false)
  }

  const handleLogout = () => {
    logout()
    setShowLogin(true)
    setCurrentConversation(null)
  }

  const handleJoinChat = ({ id, name }: Conversation) => {
    // For joining, we don't have the name yet, so we'll use a placeholder
    // In a real app, you'd fetch the conversation details from the API
    setCurrentConversation({
      id: id,
      name: name, // Placeholder name
    })
  }

  const handleGoToChat = ({ id, name }: Conversation) => {
    if (currentConversation && currentConversation.id === id) {
      // Already in the right conversation, just ensure it's set
      setCurrentConversation(currentConversation)
    } else {
      // This would typically fetch the conversation details from the API
      // For now, we'll use a placeholder name
      setCurrentConversation({
        id: id,
        name,
      })
    }
  }

  const handleBackToHome = () => {
    setCurrentConversation(null)
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
        <Toaster />
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="h-[100svh] bg-background text-foreground flex flex-col">
        <main className="flex-1 min-h-0">
          {currentConversation && user ? (
            <ChatPage
              conversation={currentConversation}
              user={user}
              onBackToHome={handleBackToHome}
              autoScroll={true}
            />
          ) : (
            <WelcomeScreen
              user={user}
              onLogin={() => setShowLogin(true)}
              onLogout={handleLogout}
              onJoinChat={handleJoinChat}
              onGoToChat={handleGoToChat}
            />
          )}
        </main>

        <LoginDialog
          isOpen={showLogin}
          onClose={() => setShowLogin(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      </div>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
