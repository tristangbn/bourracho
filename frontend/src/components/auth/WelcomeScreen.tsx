import type { User } from '@/api/generated'
import AppHeader from '@/components/layout/AppHeader'
import { Button } from '@/components/ui/button'
import JoinChatModal from './JoinChatModal'
import NewChatModal from './NewChatModal'

interface WelcomeScreenProps {
  user: User | null
  onLogin: () => void
  onLogout: () => void
  onJoinChat?: (conversationId: string) => void
  onGoToChat?: (conversationId: string) => void
}

export default function WelcomeScreen({
  user,
  onLogin,
  onLogout,
  onJoinChat,
  onGoToChat,
}: WelcomeScreenProps) {
  if (user) {
    return (
      <div className="flex flex-col h-full">
        {/* App Header */}
        <AppHeader user={user} onLogout={onLogout} />

        {/* Conversation List Section */}
        <div className="flex-1 p-6">
          <div className="text-center text-muted-foreground">
            <p className="text-sm">No conversations yet...</p>
            <p className="text-sm">
              Create or join one before you're too wasted! 🤪
            </p>
            {/* TODO: Add conversation list here */}
          </div>
        </div>

        {/* Action Buttons Section */}
        <div className="p-4 border-t bg-card flex gap-3 justify-center">
          <NewChatModal user={user} onGoToChat={onGoToChat} />
          {onJoinChat && <JoinChatModal onJoinChat={onJoinChat} />}
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-full flex-col items-center justify-center p-6">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold">Welcome to Bourracho</h2>
        <p className="text-muted-foreground">Please log in to start chatting</p>
        <Button onClick={onLogin}>Login</Button>
      </div>
    </div>
  )
}
