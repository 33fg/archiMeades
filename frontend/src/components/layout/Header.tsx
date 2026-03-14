import {
  ChevronLeft,
  ChevronRight,
  LogOut,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  User,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/AuthContext'
import { useLayout } from '@/contexts/LayoutContext'
import { useTheme } from '@/contexts/ThemeContext'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { TheorySelector, DatasetSelector, GlobalSearch } from '@/components/header'

export function Header() {
  const { user, logout } = useAuth()
  const { resolved, setTheme } = useTheme()
  const {
    leftCollapsed,
    rightCollapsed,
    toggleLeft,
    toggleRight,
    toggleMobileNav,
    mobileNavOpen,
  } = useLayout()
  const isDesktop = useMediaQuery('(min-width: 768px)')

  return (
    <header
      className="col-span-3 flex h-14 items-center justify-between gap-4 border-b border-border bg-card px-4"
      style={{ gridColumn: '1 / -1' }}
    >
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={isDesktop ? toggleLeft : toggleMobileNav}
          aria-label={
            isDesktop
              ? leftCollapsed
                ? 'Expand sidebar'
                : 'Collapse sidebar'
              : mobileNavOpen
                ? 'Close menu'
                : 'Open menu'
          }
        >
          {isDesktop ? (
            leftCollapsed ? (
              <PanelLeftOpen className="h-5 w-5" />
            ) : (
              <PanelLeftClose className="h-5 w-5" />
            )
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </Button>
        <Link to="/" className="text-lg font-semibold text-foreground hover:underline">
          ArchiMeades
        </Link>
      </div>
      {isDesktop && (
        <div className="flex flex-1 items-center justify-center gap-2">
          <TheorySelector />
          <DatasetSelector />
          <GlobalSearch />
        </div>
      )}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(resolved === 'dark' ? 'light' : 'dark')}
          aria-label={resolved === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {resolved === 'dark' ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
        {isDesktop && (
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleRight}
            aria-label={rightCollapsed ? 'Expand panel' : 'Collapse panel'}
          >
            {rightCollapsed ? (
              <ChevronLeft className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </Button>
        )}
        {user ? (
          <div className="flex items-center gap-2 border-l border-border pl-3">
            <User className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{user.email}</span>
            <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        ) : null}
      </div>
    </header>
  )
}
