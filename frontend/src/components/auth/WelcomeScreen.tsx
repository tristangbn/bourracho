import { useEffect, useState } from 'react'
import type { User, Conversation } from '@/api/generated'
import { conversationsApiApiListConversations } from '@/api/generated'
import AppHeader from '@/components/layout/AppHeader'
import { Button } from '@/components/ui/button'
import { MessageCircle, Users, Lock, Unlock } from 'lucide-react'
import { showToast } from '@/lib/toast'
import JoinChatModal from './JoinChatModal'
import NewChatModal from './NewChatModal'

interface WelcomeScreenProps {
  user: User | null
  onLogin: () => void
  onLogout: () => void
  onJoinChat?: ({ id, name }: Conversation) => void
  onGoToChat?: ({ id, name }: Conversation) => void
}

export default function WelcomeScreen({
  user,
  onLogin,
  onLogout,
  onJoinChat,
  onGoToChat,
}: WelcomeScreenProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchConversations = async () => {
    if (!user) return

    setIsLoading(true)
    try {
      const response = await conversationsApiApiListConversations({
        headers: {
          'User-Id': user.id,
        },
      })

      if (response.data) {
        setConversations(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      showToast.error(
        'Failed to load conversations',
        'Please try refreshing the page.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchConversations()
    }
  }, [user])

  const handleGoToConversation = (conversation: Conversation) => {
    if (conversation.id && onGoToChat) {
      onGoToChat({
        id: conversation.id,
        name: conversation.name,
      })
    }
  }

  if (user) {
    return (
      <div className="flex flex-col h-full">
        {/* App Header */}
        <AppHeader user={user} onLogout={onLogout} />

        {/* Conversation List Section */}
        <div className="flex-1 p-6 overflow-auto">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Your Conversations</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchConversations}
                disabled={isLoading}
              >
                {isLoading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">
                  Loading conversations...
                </p>
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-12">
                <MessageCircle className="h-16 w-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">
                  No conversations yet
                </h3>
                <p className="text-muted-foreground mb-4">
                  Create or join one before you're too wasted! 🤪
                </p>
                <div className="flex gap-4">
                  <NewChatModal
                    user={user}
                    onGoToChat={onGoToChat}
                    onConversationCreated={fetchConversations}
                  />
                  {onJoinChat && (
                    <JoinChatModal
                      user={user}
                      onJoinChat={onJoinChat}
                      onConversationJoined={fetchConversations}
                    />
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-0 border rounded-lg overflow-hidden bg-card">
                {conversations.map((conversation, index) => (
                  <div
                    key={conversation.id}
                    className="cursor-pointer hover:bg-muted/50 transition-colors duration-200"
                    onClick={() => handleGoToConversation(conversation)}
                  >
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2">
                              {conversation.is_locked ? (
                                <Lock className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <Unlock className="h-4 w-4 text-muted-foreground" />
                              )}
                              <h3 className="font-semibold truncate">
                                {conversation.name || 'Unnamed Chat'}
                              </h3>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Users className="h-4 w-4" />
                              <span>
                                {conversation.users_ids?.length || 0} member
                                {(conversation.users_ids?.length || 0) !== 1
                                  ? 's'
                                  : ''}
                              </span>
                            </div>
                            <span className="font-mono text-xs">
                              ID: {conversation.id}
                            </span>
                          </div>
                        </div>
                        <MessageCircle className="h-5 w-5 text-muted-foreground ml-4 flex-shrink-0" />
                      </div>
                    </div>
                    {index < conversations.length - 1 && (
                      <div className="border-t border-border mx-4" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons Section - Only show when there are conversations */}
        {conversations.length > 0 && (
          <div className="p-4 border-t bg-card flex gap-3 justify-center">
            <NewChatModal
              user={user}
              onGoToChat={onGoToChat}
              onConversationCreated={fetchConversations}
            />
            {onJoinChat && (
              <JoinChatModal
                user={user}
                onJoinChat={onJoinChat}
                onConversationJoined={fetchConversations}
              />
            )}
          </div>
        )}
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
