'use client'

import { useAuth } from '@/providers/auth-provider'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LogOut, User, ChevronDown } from 'lucide-react'

interface HeaderProps {
  title: string
}

export function Header({ title }: HeaderProps) {
  const { user, logout } = useAuth()

  const initials =
    user
      ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase() || user.email[0].toUpperCase()
      : '?'

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6 flex-shrink-0">
      <h1 className="text-sm font-semibold text-foreground">{title}</h1>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="gap-2 h-8">
            <span className="w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs font-semibold flex items-center justify-center">
              {initials}
            </span>
            <span className="text-sm hidden sm:inline">
              {user ? `${user.first_name} ${user.last_name}`.trim() || user.email : 'Usuario'}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel className="text-xs text-muted-foreground font-normal truncate">
            {user?.email}
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem disabled>
            <User className="w-4 h-4 mr-2" />
            Mi perfil
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={logout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Cerrar sesión
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
