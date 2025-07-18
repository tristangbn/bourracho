import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, ArrowLeft, Copy, Check, RefreshCw } from 'lucide-react'
import { showToast } from '@/lib/toast'
import type { User, Message, Conversation } from '@/api/generated'
import {
  conversationsApiApiGetMessages,
  conversationsApiApiPostMessage,
  conversationsApiApiGetUsers,
} from '@/api/generated'

interface ChatPageProps {
  conversation: Conversation
  user: User
  onSendMessage?: (message: string) => void
  onBackToHome: () => void
  messages?: Message[]
}

export default function ChatPage({
  conversation,
  user,
  onSendMessage,
  onBackToHome,
  messages: initialMessages = [],
}: ChatPageProps) {
  const [messageInput, setMessageInput] = useState('')
  const [copied, setCopied] = useState(false)
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [isLoading, setIsLoading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [users, setUsers] = useState<Record<string, User>>({})

  // Fetch messages when component mounts
  useEffect(() => {
    fetchMessages()
    fetchUsers()
  }, [conversation.id])

  const fetchMessages = async () => {
    setIsLoading(true)
    try {
      const response = await conversationsApiApiGetMessages({
        path: {
          conversation_id: conversation.id || '',
        },
        headers: {
          'User-Id': user.id,
        },
      })

      if (response.data && Array.isArray(response.data)) {
        setMessages(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error)
      showToast.error(
        'Failed to load messages',
        'Please try refreshing the page.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await conversationsApiApiGetUsers({
        headers: {
          'User-Id': user.id,
        },
      })

      if (response.data && Array.isArray(response.data)) {
        const usersMap: Record<string, User> = {}
        response.data.forEach(user => {
          usersMap[user.id] = user
        })
        setUsers(usersMap)
      }
    } catch (error) {
      console.error('Failed to fetch users:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (messageInput.trim() && !isSending) {
      setIsSending(true)
      try {
        const messageData: Message = {
          content: messageInput.trim(),
          conversation_id: conversation.id || '',
          issuer_id: user.id,
        }

        const response = await conversationsApiApiPostMessage({
          path: {
            conversation_id: conversation.id || '',
          },
          body: messageData,
          headers: {
            'User-Id': user.id,
          },
        })

        if (response.data) {
          // Add the new message to the list
          setMessages(prev => [...prev, response.data])
          setMessageInput('')

          // Call the optional callback
          if (onSendMessage) {
            onSendMessage(messageInput.trim())
          }
        }
      } catch (error) {
        console.error('Failed to send message:', error)
        showToast.error('Failed to send message', 'Please try again.')
      } finally {
        setIsSending(false)
      }
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const copyConversationId = async () => {
    try {
      await navigator.clipboard.writeText(conversation.id || '')
      setCopied(true)
      showToast.success(
        'Conversation ID copied!',
        'Share this ID with others to join.'
      )
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error(error)
      showToast.error(
        'Failed to copy to clipboard',
        'Please copy the ID manually.'
      )
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-card">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={onBackToHome}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex items-center gap-2">
            <div className="flex items-baseline gap-2">
              <h2 className="text-xl font-semibold">{conversation.name}</h2>
              <p className="text-sm text-muted-foreground">
                (#{conversation.id})
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={copyConversationId}
              className="h-6 w-6 p-0"
            >
              {copied ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={fetchMessages}
          disabled={isLoading}
          className="h-8 w-8 p-0"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
              <p>Loading messages...</p>
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <p className="text-lg">Welcome to the party! 🎉</p>
              <p className="text-sm">
                Start the conversation by sending a message below.
              </p>
            </div>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={`flex ${message.issuer_id === user.id ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                  message.issuer_id === user.id
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">
                    {message.issuer_id === user.id
                      ? 'You'
                      : users[message.issuer_id]?.username ||
                        (Object.keys(users).length > 0
                          ? 'Unknown User'
                          : '...')}
                  </span>
                  {message.timestamp && (
                    <span className="text-xs opacity-70">
                      {formatTime(message.timestamp)}
                    </span>
                  )}
                </div>
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Message Input */}
      <div className="border-t bg-card p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={messageInput}
            onChange={e => setMessageInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1"
            autoFocus
            disabled={isSending}
          />
          <Button type="submit" disabled={!messageInput.trim() || isSending}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
