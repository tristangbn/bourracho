import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, ArrowLeft, Copy, Check } from 'lucide-react'
import { showToast } from '@/lib/toast'
import type { User } from '@/api/generated'

interface Message {
  id: string
  content: string
  sender: User
  timestamp: Date
}

interface ChatPageProps {
  conversationId: string
  conversationName: string
  user: User
  onSendMessage?: (message: string) => void
  onBackToHome: () => void
  messages?: Message[]
}

export default function ChatPage({
  conversationId,
  conversationName,
  user,
  onSendMessage,
  onBackToHome,
  messages = [],
}: ChatPageProps) {
  const [messageInput, setMessageInput] = useState('')
  const [copied, setCopied] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (messageInput.trim()) {
      if (onSendMessage) {
        onSendMessage(messageInput.trim())
      } else {
        console.log('Sending message:', messageInput.trim())
        // TODO: Implement actual message sending
      }
      setMessageInput('')
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const copyConversationId = async () => {
    try {
      await navigator.clipboard.writeText(conversationId)
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
              <h2 className="text-xl font-semibold">{conversationName}</h2>
              <p className="text-sm text-muted-foreground">
                (#{conversationId})
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
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.length === 0 ? (
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
              className={`flex ${message.sender.id === user.id ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                  message.sender.id === user.id
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">
                    {message.sender.id === user.id
                      ? 'You'
                      : message.sender.username}
                  </span>
                  <span className="text-xs opacity-70">
                    {formatTime(message.timestamp)}
                  </span>
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
          />
          <Button type="submit" disabled={!messageInput.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
