import { Button } from '@/components/ui/button'

interface User {
  id: number
  email: string
  name: string
}

interface WelcomeScreenProps {
  user: User | null
  onLogin: () => void
}

export default function WelcomeScreen({ user, onLogin }: WelcomeScreenProps) {
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
            <Button>New party chat</Button>
            <Button variant="outline">Join party chat</Button>
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
