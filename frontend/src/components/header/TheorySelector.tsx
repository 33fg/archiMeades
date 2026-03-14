/**
 * Theory Selector - dropdown, GET /api/theories.
 * Frontend Component Hierarchy: Header.
 */

import { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { useApiQuery } from '@/hooks/useApi'
import { useSelection } from '@/contexts/SelectionContext'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface Theory {
  id: string
  name: string
  identifier?: string
}

export function TheorySelector() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const { theoryId, setTheoryId } = useSelection()
  const { data: theories = [], isLoading } = useApiQuery<Theory[]>(
    ['theories', 'list'],
    '/api/theories?limit=100'
  )
  const selected = theories.find((t) => t.id === theoryId)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    if (open) document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [open])

  return (
    <div ref={ref} className="relative">
      <Button
        variant="outline"
        size="sm"
        className="min-w-[140px] justify-between gap-1"
        disabled={isLoading}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="truncate">
          {selected ? selected.name || selected.identifier || selected.id.slice(0, 8) : 'Select theory'}
        </span>
        <ChevronDown className="h-4 w-4 shrink-0 opacity-50" />
      </Button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 max-h-60 w-full min-w-[180px] overflow-auto rounded-md border border-border bg-popover py-1 shadow-md">
          <button
            type="button"
            className={cn(
              'w-full px-3 py-2 text-left text-sm hover:bg-accent',
              !theoryId && 'bg-accent'
            )}
            onClick={() => { setTheoryId(null); setOpen(false) }}
          >
            None
          </button>
          {theories.map((t) => (
            <button
              key={t.id}
              type="button"
              className={cn(
                'w-full px-3 py-2 text-left text-sm hover:bg-accent',
                theoryId === t.id && 'bg-accent'
              )}
              onClick={() => { setTheoryId(t.id); setOpen(false) }}
            >
              {t.name || t.identifier || t.id.slice(0, 8)}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
