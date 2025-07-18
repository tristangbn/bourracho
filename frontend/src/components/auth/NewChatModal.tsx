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
import { Copy, Check } from 'lucide-react'

interface NewChatModalProps {
  onCreateChat: (conversationName: string) => Promise<string> | string
}

export default function NewChatModal({ onCreateChat }: NewChatModalProps) {
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
        const id = await onCreateChat(conversationName.trim())
        setConversationId(id)
        showToast.success(
          'Chat created successfully!',
          'Share the conversation ID with others to join.'
        )
      } catch (error) {
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
      } catch (error) {
        showToast.error(
          'Failed to copy to clipboard',
          'Please copy the ID manually.'
        )
      }
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
            <DialogFooter>
              <Button onClick={handleClose}>Done</Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
