/**
 * WO-47: Provenance viewer with verification status and JSON export.
 * Displays provenance metadata with green/red verification indicators.
 */

import { CheckCircle2, Download, GitBranch, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export type ProvenanceType = 'theory' | 'simulation'

export interface TheoryLineage {
  theory_id: string
  simulation_ids: string[]
  publication_ids: string[]
}

export interface SimulationChain {
  sim_id: string
  theory_id: string | null
  observation_ids: string[]
}

type ProvenanceData = TheoryLineage | SimulationChain

interface ProvenanceViewerProps {
  type: ProvenanceType
  data: ProvenanceData | null
  verified: boolean
  error?: boolean
  onExport?: () => void
  showExport?: boolean
  compact?: boolean
  showVerification?: boolean
}

function isTheoryLineage(d: ProvenanceData): d is TheoryLineage {
  return 'simulation_ids' in d
}

export function ProvenanceViewer({
  type,
  data,
  verified,
  error,
  onExport,
  showExport = true,
  compact = false,
  showVerification = true,
}: ProvenanceViewerProps) {
  const mt = compact ? 'mt-3' : 'mt-6'
  if (error) {
    return (
      <div className={`${mt} rounded-md border border-amber-500/50 bg-amber-500/10 p-4`}>
        <div className="flex items-center gap-2 text-amber-600 dark:text-amber-500">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span className="text-sm font-medium">Provenance unavailable (Neo4j not running)</span>
        </div>
      </div>
    )
  }

  if (!data) return null

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `provenance-${type}-${isTheoryLineage(data) ? data.theory_id : data.sim_id}.json`
    a.click()
    URL.revokeObjectURL(url)
    onExport?.()
  }

  return (
    <div className={`${mt} rounded-md border border-border bg-muted/30 p-4`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-medium text-foreground">Provenance (Neo4j)</h3>
          {showVerification &&
            (verified ? (
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-500" aria-label="Verified" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-500" aria-label="Unverified" />
            ))}
        </div>
        {showExport && (
          <Button variant="ghost" size="sm" className="gap-1.5 h-8" onClick={exportJson}>
            <Download className="h-3.5 w-3.5" />
            Export JSON
          </Button>
        )}
      </div>

      <div className="mt-3 space-y-2 text-sm">
        {isTheoryLineage(data) ? (
          <>
            <p>
              <span className="text-muted-foreground">Simulations:</span>{' '}
              {data.simulation_ids.length > 0 ? (
                <span className="flex flex-wrap gap-1">
                  {data.simulation_ids.map((sid) => (
                    <Link
                      key={sid}
                      to={`/simulations/${sid}`}
                      className="text-primary hover:underline"
                    >
                      {sid.slice(0, 8)}…
                    </Link>
                  ))}
                </span>
              ) : (
                'None'
              )}
            </p>
            <p>
              <span className="text-muted-foreground">Citations:</span>{' '}
              {data.publication_ids.length > 0 ? (
                <span className="text-sm">
                  {data.publication_ids.map((pid) => (
                    <span key={pid} className="inline-block rounded bg-muted/50 px-1.5 py-0.5 font-mono text-xs mr-1">
                      {pid.slice(0, 8)}…
                    </span>
                  ))}
                </span>
              ) : (
                'None'
              )}
            </p>
          </>
        ) : (
          <>
            <p>
              <span className="text-muted-foreground">Theory:</span>{' '}
              {data.theory_id ? (
                <Link
                  to={`/theories/${data.theory_id}`}
                  className="text-primary hover:underline"
                >
                  {data.theory_id.slice(0, 8)}…
                </Link>
              ) : (
                '—'
              )}
            </p>
            <p>
              <span className="text-muted-foreground">Observations:</span>{' '}
              {data.observation_ids.length > 0 ? (
                <span className="inline-flex flex-wrap gap-1">
                  {data.observation_ids.map((oid) => (
                    <Link
                      key={oid}
                      to={`/observations/${oid}`}
                      className="text-primary hover:underline"
                    >
                      {oid.slice(0, 8)}…
                    </Link>
                  ))}
                </span>
              ) : (
                'None'
              )}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
