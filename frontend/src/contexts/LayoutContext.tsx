/**
 * Layout context - panel state, persist to localStorage.
 * WO-15: Five-Panel Layout and AppShell
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

const STORAGE_KEY = 'gravitational_layout'

export type RightPanelMode = 'ai' | 'details'

interface LayoutState {
  leftCollapsed: boolean
  rightCollapsed: boolean
  rightPanelMode: RightPanelMode
  leftWidth: number
  rightWidth: number
  mobileNavOpen: boolean
}

const DEFAULT: LayoutState = {
  leftCollapsed: false,
  rightCollapsed: false,
  rightPanelMode: 'ai',
  leftWidth: 192,
  rightWidth: 224,
  mobileNavOpen: false,
}

function loadStored(): Partial<LayoutState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}
    return JSON.parse(raw) as Partial<LayoutState>
  } catch {
    return {}
  }
}

function saveStored(state: LayoutState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // ignore
  }
}

interface LayoutContextValue extends LayoutState {
  setLeftCollapsed: (v: boolean) => void
  setRightCollapsed: (v: boolean) => void
  setRightPanelMode: (v: RightPanelMode) => void
  setLeftWidth: (v: number) => void
  setRightWidth: (v: number) => void
  setMobileNavOpen: (v: boolean) => void
  toggleLeft: () => void
  toggleRight: () => void
  toggleMobileNav: () => void
}

const LayoutContext = createContext<LayoutContextValue | null>(null)

export function LayoutProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<LayoutState>(() => ({
    ...DEFAULT,
    ...loadStored(),
  }))

  useEffect(() => {
    saveStored(state)
  }, [state])

  const toggleLeft = useCallback(() => {
    setState((s) => ({ ...s, leftCollapsed: !s.leftCollapsed }))
  }, [])

  const toggleRight = useCallback(() => {
    setState((s) => ({ ...s, rightCollapsed: !s.rightCollapsed }))
  }, [])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault()
        toggleLeft()
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
        e.preventDefault()
        toggleRight()
      }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [toggleLeft, toggleRight])

  const setLeftCollapsed = useCallback((v: boolean) => {
    setState((s) => ({ ...s, leftCollapsed: v }))
  }, [])

  const setRightCollapsed = useCallback((v: boolean) => {
    setState((s) => ({ ...s, rightCollapsed: v }))
  }, [])

  const setRightPanelMode = useCallback((v: RightPanelMode) => {
    setState((s) => ({ ...s, rightPanelMode: v }))
  }, [])

  const setLeftWidth = useCallback((v: number) => {
    setState((s) => ({ ...s, leftWidth: Math.max(120, Math.min(320, v)) }))
  }, [])

  const setRightWidth = useCallback((v: number) => {
    setState((s) => ({ ...s, rightWidth: Math.max(160, Math.min(400, v)) }))
  }, [])

  const setMobileNavOpen = useCallback((v: boolean) => {
    setState((s) => ({ ...s, mobileNavOpen: v }))
  }, [])

  const toggleMobileNav = useCallback(() => {
    setState((s) => ({ ...s, mobileNavOpen: !s.mobileNavOpen }))
  }, [])

  const value: LayoutContextValue = {
    ...state,
    setLeftCollapsed,
    setRightCollapsed,
    setRightPanelMode,
    setLeftWidth,
    setRightWidth,
    setMobileNavOpen,
    toggleLeft,
    toggleRight,
    toggleMobileNav,
  }

  return (
    <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
  )
}

export function useLayout() {
  const ctx = useContext(LayoutContext)
  if (!ctx) throw new Error('useLayout must be used within LayoutProvider')
  return ctx
}
