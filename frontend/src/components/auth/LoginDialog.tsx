import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogOverlay,
  DialogPortal,
} from '@/components/ui/dialog'
import type { User } from '@/api/generated'
import LoginForm from './LoginForm'

interface LoginDialogProps {
  isOpen: boolean
  onClose: () => void
  onLoginSuccess: (user: User) => void
}

export default function LoginDialog({
  isOpen,
  onClose,
  onLoginSuccess,
}: LoginDialogProps) {
  const handleSubmit = (user: User) => {
    onLoginSuccess(user)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogPortal>
        {/* Custom overlay with backdrop blur and higher opacity */}
        <DialogOverlay className="bg-background/95 backdrop-blur-md" />
        <DialogContent className="sm:max-w-md" showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="text-center">
              Welcome to Bourracho 👋
            </DialogTitle>
            <DialogDescription className="text-center">
              Enter your credentials to access your account
            </DialogDescription>
          </DialogHeader>

          <LoginForm onSubmit={handleSubmit} />
        </DialogContent>
      </DialogPortal>
    </Dialog>
  )
}
