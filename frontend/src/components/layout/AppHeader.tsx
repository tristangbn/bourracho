import { useEffect, useState } from 'react'
import md5 from 'blueimp-md5'
import { LogOut, User } from 'lucide-react'
import { ModeToggle } from '@/components/mode-toggle'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface User {
  id: number
  email: string
  name: string
}

interface AppHeaderProps {
  user: User | null
  onLogout: () => void
}

function getGravatarUrl(email: string, size: number = 200): string {
  const normalizedEmail = email.trim().toLowerCase()
  const hash = md5(normalizedEmail)
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=mp`
}

export default function AppHeader({ user, onLogout }: AppHeaderProps) {
  const [showThemeToggle, setShowThemeToggle] = useState(false)

  useEffect(() => {
    // Check if #theme parameter exists in the URL
    const hasThemeParam = window.location.hash.includes('#theme')
    setShowThemeToggle(hasThemeParam)
  }, [])

  return (
    <header className="flex items-center justify-between px-4 py-2 border-b">
      <div>
        <span className="text-2xl font-bold text-primary">
          {'Bourracho'.toLocaleLowerCase()}
        </span>
      </div>
      <div className="flex items-center gap-4">
        {showThemeToggle && <ModeToggle />}

        {/* Avatar positioned absolutely in top right */}
        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-8 w-8 rounded-full p-0"
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage
                    src={getGravatarUrl(user.email)}
                    alt={user.name}
                  />
                  <AvatarFallback>
                    {user.name.substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user.name}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  )
}
