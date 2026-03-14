/**
 * Dataset Selector - dropdown, GET /api/observations.
 * Frontend Component Hierarchy: Header.
 */

import { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { useApiQuery } from '@/hooks/useApi'
import { useSelection } from '@/contexts/SelectionContext'
import { Button } from '@/components/ui/button'

interface Observation {
  id: string
  name: string
}

export function DatasetSelector() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const { observationIds, toggleObservation } = useSelection()
  const { data: observations = [], isLoading } = useApiQuery<Observation[]>(
    ['observations', 'list'],
    '/api/observations?limit=100'
  )

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
          {observationIds.length === 0
            ? 'Select dataset'
            : `${observationIds.length} selected`}
        </span>
        <ChevronDown className="h-4 w-4 shrink-0 opacity-50" />
      </Button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 max-h-60 w-full min-w-[180px] overflow-auto rounded-md border border-border bg-popover py-1 shadow-md">
          {observations.map((obs) => (
            <label
              key={obs.id}
              className="flex cursor-pointer items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
            >
              <input
                type="checkbox"
                checked={observationIds.includes(obs.id)}
                onChange={() => toggleObservation(obs.id)}
                className="rounded"
              />
              {obs.name || obs.id.slice(0, 8)}
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
