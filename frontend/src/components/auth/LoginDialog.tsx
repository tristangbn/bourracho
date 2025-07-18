import { useState } from 'react'
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
import SignupForm from './SignupForm'

interface LoginDialogProps {
  isOpen: boolean
  onClose: () => void
  onLoginSuccess: (user: User) => void
}

type AuthMode = 'login' | 'signup'

export default function LoginDialog({
  isOpen,
  onClose,
  onLoginSuccess,
}: LoginDialogProps) {
  const [mode, setMode] = useState<AuthMode>('login')

  const handleLoginSuccess = (user: User) => {
    onLoginSuccess(user)
    onClose()
    // Reset to login mode when dialog closes
    setMode('login')
  }

  const handleSignupSuccess = () => {
    // Switch to login mode after successful signup
    setMode('login')
  }

  const handleSwitchToSignup = () => {
    setMode('signup')
  }

  const handleSwitchToLogin = () => {
    setMode('login')
  }

  const getDialogContent = () => {
    if (mode === 'signup') {
      return {
        title: 'Create Your Account',
        description: 'Join Bourracho and start chatting with friends',
        form: (
          <SignupForm
            onSignupSuccess={handleSignupSuccess}
            onSwitchToLogin={handleSwitchToLogin}
          />
        ),
      }
    }

    return {
      title: 'Welcome to Bourracho 👋',
      description: 'Enter your credentials to access your account',
      form: (
        <LoginForm
          onSubmit={handleLoginSuccess}
          onSwitchToSignup={handleSwitchToSignup}
        />
      ),
    }
  }

  const { title, description, form } = getDialogContent()

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogPortal>
        {/* Custom overlay with backdrop blur and higher opacity */}
        <DialogOverlay className="bg-background/95 backdrop-blur-md" />
        <DialogContent className="sm:max-w-md" showCloseButton={false}>
          <DialogHeader>
            <DialogTitle className="text-center">{title}</DialogTitle>
            <DialogDescription className="text-center">
              {description}
            </DialogDescription>
          </DialogHeader>

          {form}
        </DialogContent>
      </DialogPortal>
    </Dialog>
  )
}
