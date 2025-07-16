import md5 from 'blueimp-md5'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

interface User {
  id: number
  email: string
  name: string
}

interface UserHeaderProps {
  user: User
  onLogout: () => void
}

function getGravatarUrl(email: string, size: number = 200): string {
  const normalizedEmail = email.trim().toLowerCase()
  const hash = md5(normalizedEmail)
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=mp`
}

export default function UserHeader({ user, onLogout }: UserHeaderProps) {
  const gravatarUrl = getGravatarUrl(user.email)

  return (
    <div className="flex items-center gap-8">
      <div className="flex items-center gap-2">
        <Avatar>
          <AvatarImage src={gravatarUrl} alt={user.name} />
          <AvatarFallback>
            {user.name.substring(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <span className="text-md">Welcome, {user.name}!</span>
      </div>
      <Button variant="outline" size="sm" onClick={onLogout}>
        Logout
      </Button>
    </div>
  )
}
