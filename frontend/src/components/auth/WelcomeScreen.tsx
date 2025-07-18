import { Button } from '@/components/ui/button'
import JoinChatModal from './JoinChatModal'
import NewChatModal from './NewChatModal'

interface User {
  id: number
  email: string
  name: string
}

interface WelcomeScreenProps {
  user: User | null
  onLogin: () => void
  onJoinChat?: (conversationId: string) => void
  onCreateChat?: (conversationName: string) => Promise<string> | string
}

export default function WelcomeScreen({
  user,
  onLogin,
  onJoinChat,
  onCreateChat,
}: WelcomeScreenProps) {
  const handleJoinChat = (conversationId: string) => {
    if (onJoinChat) {
      onJoinChat(conversationId)
    } else {
      console.log('Joining chat with ID:', conversationId)
      // TODO: Implement actual join chat functionality
    }
  }

  const handleCreateChat = async (
    conversationName: string
  ): Promise<string> => {
    if (onCreateChat) {
      return await onCreateChat(conversationName)
    } else {
      // Mock implementation for testing - generates a 6-digit ID
      console.log('Creating new chat with name:', conversationName)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      const mockId = Math.floor(100000 + Math.random() * 900000).toString()
      console.log('Generated conversation ID:', mockId)
      return mockId
    }
  }

  if (user) {
    return (
      <div className="flex min-h-[calc(100vh-120px)] flex-col items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">
            You are now logged in to Bourracho!
          </h2>
          <p className="text-muted-foreground">
            You are logged in as{' '}
            <span className="italic font-bold">{user.email}</span>
          </p>
          <div className="flex gap-2 justify-center">
            <NewChatModal onCreateChat={handleCreateChat} />
            <JoinChatModal onJoinChat={handleJoinChat} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-[calc(100vh-120px)] flex-col items-center justify-center">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold">Welcome to Bourracho</h2>
        <p className="text-muted-foreground">Please log in to start chatting</p>
        <Button onClick={onLogin}>Login</Button>
      </div>
    </div>
  )
}
