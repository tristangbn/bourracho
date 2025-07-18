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
import { conversationsApiApiJoinConversation } from '@/api/generated'
import { showToast } from '@/lib/toast'
import type { Conversation, User } from '@/api/generated'

interface JoinChatModalProps {
  user: User
  onJoinChat: ({ id, name }: Conversation) => void
  onConversationJoined?: () => void
}

export default function JoinChatModal({
  user,
  onJoinChat,
  onConversationJoined,
}: JoinChatModalProps) {
  const [conversationId, setConversationId] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (conversationId.trim() && !isLoading) {
      setIsLoading(true)
      try {
        const response = await conversationsApiApiJoinConversation({
          path: {
            conversation_id: conversationId.trim(),
          },
          headers: {
            'User-Id': user.id,
          },
        })

        if (response.data) {
          const conversation = response.data
          onJoinChat({
            id: conversation.id,
            name: conversation.name || 'Unnamed Chat',
          })
          onConversationJoined?.()
          setConversationId('')
          setIsOpen(false)

          // Check if user was already in the conversation
          const wasAlreadyMember = conversation.users_ids?.includes(user.id)
          if (wasAlreadyMember) {
            showToast.success(
              'Already in chat!',
              `You're already a member of "${conversation.name || 'Unnamed Chat'}"`
            )
          } else {
            showToast.success(
              'Successfully joined chat!',
              `You're now part of "${conversation.name || 'Unnamed Chat'}"`
            )
          }
        }
      } catch (error) {
        console.error('Failed to join conversation:', error)

        // Try to provide more specific error messages
        let errorMessage = 'Please check the conversation ID and try again.'
        let errorTitle = 'Failed to join conversation'

        if (error && typeof error === 'object' && 'response' in error) {
          const response = (
            error as {
              response?: { status?: number; data?: { error?: string } }
            }
          ).response
          if (response?.status === 500) {
            const errorData = response?.data
            if (errorData?.error) {
              if (
                errorData.error.includes('not found') ||
                errorData.error.includes('does not exist')
              ) {
                errorTitle = 'Conversation not found'
                errorMessage =
                  'The conversation ID you entered does not exist. Please check and try again.'
              } else if (errorData.error.includes('already')) {
                errorTitle = 'Already joined'
                errorMessage = 'You are already a member of this conversation.'
              } else {
                errorMessage = errorData.error
              }
            }
          }
        } else if (error && typeof error === 'object' && 'message' in error) {
          const message = (error as { message?: string }).message
          if (
            message?.includes('Network Error') ||
            message?.includes('fetch')
          ) {
            errorTitle = 'Connection error'
            errorMessage =
              'Unable to connect to the server. Please check your internet connection.'
          }
        }

        showToast.error(errorTitle, errorMessage)
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      setConversationId('')
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline">Join party chat</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Join Party Chat</DialogTitle>
          <DialogDescription>
            Enter the conversation ID to join an existing party chat.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="conversation-id">Conversation ID</Label>
              <Input
                id="conversation-id"
                value={conversationId}
                onChange={e => setConversationId(e.target.value)}
                placeholder="Enter conversation ID..."
                autoFocus
                disabled={isLoading}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!conversationId.trim() || isLoading}
            >
              {isLoading ? 'Joining...' : 'Join Chat'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
