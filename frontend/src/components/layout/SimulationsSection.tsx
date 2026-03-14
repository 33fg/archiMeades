/**
 * Simulations section for left sidebar - recent simulations per Frontend blueprint.
 * "The left sidebar provides contextual navigation... simulation history"
 */

import { Cpu, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useApiQuery } from '@/hooks/useApi'

interface Simulation {
  id: string
  theory_id: string
  status: string
  progress_percent: number
  started_at: string | null
}

export function SimulationsSection() {
  const { data: simulations, isLoading } = useApiQuery<Simulation[]>(
    ['simulations', 'sidebar'],
    '/api/simulations',
    { staleTime: 30_000 }
  )

  const recent = (simulations ?? []).slice(0, 5)

  return (
    <div className="border-t border-sidebar-border px-2 pt-2">
      <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
        Simulations
      </p>
      {isLoading ? (
        <p className="px-3 py-2 text-xs text-muted-foreground">Loading…</p>
      ) : recent.length === 0 ? (
        <div className="flex flex-col gap-0.5">
          <p className="px-3 py-1.5 text-xs text-muted-foreground">No simulations yet</p>
          <Link
            to="/simulations"
            className="flex items-center gap-2 rounded-md px-3 py-1.5 text-xs text-sidebar-foreground hover:bg-sidebar-accent"
          >
            <Plus className="h-3.5 w-3.5" />
            Create simulation
          </Link>
        </div>
      ) : (
        <nav className="flex flex-col gap-0.5">
          {recent.map((sim) => (
            <Link
              key={sim.id}
              to={`/simulations/${sim.id}`}
              className="rounded-md px-3 py-1.5 text-xs text-sidebar-foreground hover:bg-sidebar-accent"
            >
              <span className="font-mono">{sim.id.slice(0, 8)}…</span>
              <span className="ml-1 text-muted-foreground">
                {sim.status === 'completed' ? '✓' : sim.status === 'failed' ? '✗' : `${sim.progress_percent}%`}
              </span>
            </Link>
          ))}
          <div className="mt-1 flex flex-col gap-0.5">
            <Link
              to="/simulations"
              className="flex items-center gap-2 rounded-md px-3 py-1.5 text-xs text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-foreground"
            >
              <Cpu className="h-3.5 w-3.5" />
              View all
            </Link>
            <Link
              to="/simulations?create=1"
              className="flex items-center gap-2 rounded-md px-3 py-1.5 text-xs text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-foreground"
            >
              <Plus className="h-3.5 w-3.5" />
              Create new
            </Link>
          </div>
        </nav>
      )}
    </div>
  )
}
