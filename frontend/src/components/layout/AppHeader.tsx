import { useEffect, useState } from 'react'
import { ModeToggle } from '@/components/mode-toggle'
import UserHeader from '@/components/auth/UserHeader'

interface User {
  id: number
  email: string
  name: string
}

interface AppHeaderProps {
  user: User | null
  onLogout: () => void
}

export default function AppHeader({ user, onLogout }: AppHeaderProps) {
  const [showThemeToggle, setShowThemeToggle] = useState(false)

  useEffect(() => {
    // Check if #theme parameter exists in the URL
    const hasThemeParam = window.location.hash.includes('#theme')
    setShowThemeToggle(hasThemeParam)
  }, [])

  return (
    <header className="flex items-baseline justify-around p-4 border-b">
      <div className="flex items-center gap-4">
        {user && <UserHeader user={user} onLogout={onLogout} />}
        {showThemeToggle && <ModeToggle />}
      </div>
    </header>
  )
}
