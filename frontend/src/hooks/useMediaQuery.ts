/**
 * useMediaQuery - respond to CSS media query changes.
 * WO-15: Responsive breakpoint handling
 * Initialize with actual value to avoid layout flash / content disappearing on first render.
 */

import { useEffect, useState } from 'react'

function getInitialMatch(query: string): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia(query).matches
}

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => getInitialMatch(query))

  useEffect(() => {
    const mq = window.matchMedia(query)
    setMatches(mq.matches)
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [query])

  return matches
}
