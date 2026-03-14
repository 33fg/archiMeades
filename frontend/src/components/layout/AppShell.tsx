import { type ReactNode } from 'react'
import { useLayout } from '@/contexts/LayoutContext'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { Header } from './Header'
import { LeftSidebar } from './LeftSidebar'
import { RightSidebar } from './RightSidebar'
import { Footer } from './Footer'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const {
    leftCollapsed,
    rightCollapsed,
    leftWidth,
    rightWidth,
    mobileNavOpen,
    setMobileNavOpen,
  } = useLayout()
  const isDesktop = useMediaQuery('(min-width: 768px)')

  const leftW = leftCollapsed ? 56 : leftWidth
  const rightW = rightCollapsed ? 0 : rightWidth

  const gridCols = isDesktop
    ? `${leftW}px 1fr ${rightW}px`
    : '1fr'

  return (
    <div
      className="app-shell grid h-screen max-h-dvh w-full min-w-0 overflow-hidden transition-[grid-template-columns] duration-300 ease-in-out"
      style={{
        gridTemplateColumns: gridCols,
        gridTemplateRows: 'auto 1fr auto',
      }}
    >
      <header className="col-span-3 col-start-1 row-start-1">
        <Header />
      </header>
      {/* Left sidebar - hidden on mobile, drawer when mobileNavOpen */}
      <aside
        className={`row-start-2 overflow-hidden border-r border-border bg-sidebar transition-all duration-300 ${!isDesktop ? 'hidden' : ''}`}
        style={
          isDesktop
            ? { width: leftW, minWidth: leftCollapsed ? 56 : leftWidth }
            : undefined
        }
      >
        <LeftSidebar />
      </aside>
      {/* Mobile nav overlay */}
      {!isDesktop && mobileNavOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm"
            onClick={() => setMobileNavOpen(false)}
            aria-hidden
          />
          <aside
            className="fixed left-0 top-0 z-50 h-full w-64 border-r border-border bg-sidebar pt-14 shadow-xl"
            role="dialog"
            aria-label="Navigation menu"
          >
            <LeftSidebar />
          </aside>
        </>
      )}
      <main
        className={`row-start-2 flex min-h-0 w-full min-w-0 flex-col items-center justify-start overflow-y-auto overflow-x-hidden border-r border-border bg-background p-6 ${isDesktop ? 'col-span-1 col-start-2' : 'col-span-1 col-start-1'}`}
      >
        {children}
      </main>
      {/* Right sidebar - hidden on mobile */}
      <aside
        className={`row-start-2 overflow-auto border-l border-border bg-sidebar transition-all duration-300 ${!isDesktop ? 'hidden' : ''} ${rightCollapsed ? 'invisible w-0 min-w-0 overflow-hidden' : ''}`}
        style={
          isDesktop && !rightCollapsed
            ? { width: rightWidth, minWidth: rightWidth }
            : isDesktop && rightCollapsed
              ? { width: 0, minWidth: 0 }
              : undefined
        }
      >
        <RightSidebar />
      </aside>
      <footer className="col-span-3 col-start-1 row-start-3">
        <Footer />
      </footer>
    </div>
  )
}
