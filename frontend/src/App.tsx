import { useState, useEffect } from 'react'

import { client } from '@/api/generated/client.gen'
import type { User } from '@/api/generated'
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
  const [createdConversations, setCreatedConversations] = useState<
    Map<string, string>
  >(new Map())

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
    setCreatedConversations(new Map())
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

    // Store the conversation name for later use
    setCreatedConversations(prev => new Map(prev).set(mockId, conversationName))

    return mockId
  }

  const handleGoToChat = (conversationId: string) => {
    // Check if this is a newly created conversation
    const conversationName = createdConversations.get(conversationId)

    if (conversationName) {
      // This is a newly created conversation
      setCurrentConversation({
        id: conversationId,
        name: conversationName,
      })
      // Remove from temporary storage
      setCreatedConversations(prev => {
        const newMap = new Map(prev)
        newMap.delete(conversationId)
        return newMap
      })
    } else if (
      currentConversation &&
      currentConversation.id === conversationId
    ) {
      // Already in the right conversation, just ensure it's set
      setCurrentConversation(currentConversation)
    } else {
      // This would typically fetch the conversation details from the API
      // For now, we'll use a placeholder name
      setCurrentConversation({
        id: conversationId,
        name: `Chat ${conversationId}`,
      })
    }
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
