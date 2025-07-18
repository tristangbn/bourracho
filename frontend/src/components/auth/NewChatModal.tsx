import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { showToast } from '@/lib/toast'
import { Copy, Check, MessageCircle } from 'lucide-react'
import { conversationsApiApiCreateConversation } from '@/api/generated'
import type { User, Conversation } from '@/api/generated'

interface NewChatModalProps {
  user: User
  onGoToChat?: (conversationId: string) => void
}

export default function NewChatModal({ user, onGoToChat }: NewChatModalProps) {
  const [conversationName, setConversationName] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (conversationName.trim()) {
      setIsLoading(true)
      try {
        const conversationData: Conversation = {
          name: conversationName.trim(),
        }

        const response = await conversationsApiApiCreateConversation({
          body: conversationData,
          headers: {
            user_id: user.id,
          },
        })

        if (response.data && 'id' in response.data) {
          const id = response.data.id!
          setConversationId(id)
          showToast.success(
            'Chat created successfully!',
            'Share the conversation ID with others to join.'
          )
        } else {
          throw new Error('Invalid response from server')
        }
      } catch (error) {
        console.error('Failed to create chat:', error)
        showToast.error('Failed to create chat', 'Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      setConversationName('')
      setConversationId(null)
      setCopied(false)
    }
  }

  const copyToClipboard = async () => {
    if (conversationId) {
      try {
        await navigator.clipboard.writeText(conversationId)
        setCopied(true)
        showToast.success(
          'Conversation ID copied!',
          'Share this ID with others to join your chat.'
        )
        setTimeout(() => setCopied(false), 2000)
      } catch {
        showToast.error(
          'Failed to copy to clipboard',
          'Please copy the ID manually.'
        )
      }
    }
  }

  const handleGoToChat = () => {
    if (conversationId && onGoToChat) {
      onGoToChat(conversationId)
      setIsOpen(false)
    }
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>New party chat</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        {!conversationId ? (
          <>
            <DialogHeader>
              <DialogTitle>Create New Party Chat</DialogTitle>
              <DialogDescription>
                Give your new party chat a name to get started.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="conversation-name">Chat Name</Label>
                  <Input
                    id="conversation-name"
                    value={conversationName}
                    onChange={e => setConversationName(e.target.value)}
                    placeholder="Enter chat name..."
                    autoFocus
                    disabled={isLoading}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={!conversationName.trim() || isLoading}
                >
                  {isLoading ? 'Creating...' : 'Create Chat'}
                </Button>
              </DialogFooter>
            </form>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Chat Created Successfully! 🎉</DialogTitle>
              <DialogDescription>
                Your party chat has been created. Share the conversation ID
                below with others to join.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="conversation-id">Conversation ID</Label>
                <div className="flex gap-2">
                  <Input
                    id="conversation-id"
                    value={conversationId}
                    readOnly
                    className="font-mono text-lg text-center"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={copyToClipboard}
                    className="shrink-0"
                  >
                    {copied ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  {copied
                    ? 'Copied to clipboard!'
                    : 'Click the copy button to share this ID'}
                </p>
              </div>
            </div>
            <DialogFooter className="flex gap-2">
              <Button variant="outline" onClick={handleClose}>
                Done
              </Button>
              <Button onClick={handleGoToChat}>
                <MessageCircle className="h-4 w-4 mr-2" />
                Go to Chat
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
