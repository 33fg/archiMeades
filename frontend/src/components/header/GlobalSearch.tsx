/**
 * Global Search - debounced input, search theories/datasets.
 * Frontend Component Hierarchy: Header.
 */

import { Search } from 'lucide-react'
import { useState } from 'react'
import { useDebounce } from '@/hooks/useDebounce'

export function GlobalSearch() {
  const [q, setQ] = useState('')
  const debounced = useDebounce(q, 300)

  return (
    <div className="relative flex-1 max-w-md">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="search"
        placeholder="Search theories, datasets…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        aria-label="Global search"
      />
      {debounced && (
        <div className="absolute left-0 top-full z-50 mt-1 w-full rounded-md border border-border bg-popover py-1 shadow-md">
          <p className="px-3 py-2 text-xs text-muted-foreground">
            Search for &quot;{debounced}&quot; (placeholder)
          </p>
        </div>
      )}
    </div>
  )
}
