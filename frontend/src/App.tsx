import { useState, useEffect } from 'react'

import { client } from '@/api/generated/client.gen'
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

interface Conversation {
  id: string
  name: string
}

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
    setCurrentConversation(null)
  }

  const handleJoinChat = (conversationId: string) => {
    // For joining, we don't have the name yet, so we'll use a placeholder
    // In a real app, you'd fetch the conversation details from the API
    setCurrentConversation({
      id: conversationId,
      name: `Chat ${conversationId}`, // Placeholder name
    })
  }

  const handleCreateChat = async (
    conversationName: string
  ): Promise<string> => {
    // Mock implementation for testing - generates a 6-digit ID
    console.log('Creating new chat with name:', conversationName)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    const mockId = Math.floor(100000 + Math.random() * 900000).toString()
    console.log('Generated conversation ID:', mockId)
    setCurrentConversation({
      id: mockId,
      name: conversationName,
    })
    return mockId
  }

  const handleSendMessage = (message: string) => {
    console.log(
      'Sending message to conversation',
      currentConversation?.id,
      ':',
      message
    )
    // TODO: Implement actual message sending
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
              conversationId={currentConversation.id}
              conversationName={currentConversation.name}
              user={user}
              onSendMessage={handleSendMessage}
              onBackToHome={handleBackToHome}
            />
          ) : (
            <WelcomeScreen
              user={user}
              onLogin={() => setShowLogin(true)}
              onLogout={handleLogout}
              onJoinChat={handleJoinChat}
              onCreateChat={handleCreateChat}
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
