import { useState } from 'react'
import { Circle, ListTodo, Trash2, X } from 'lucide-react'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'
import { Button } from '@/components/ui/button'

type HealthResponse = {
  status: string
  database: string
  redis: string
  s3: string
  neo4j: string
  dgx: string
  dgx_cluster_size?: number
}

type WorkersHealthResponse = {
  status: string
  workers: string[]
}

type JobStatus = {
  id: string
  job_type: string
  status: string
  progress_percent: number
  error_message: string | null
  target_backend?: string | null
}

function StatusDot({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className="flex items-center gap-1">
      <Circle
        className={`h-1.5 w-1.5 shrink-0 fill-current ${ok ? 'text-green-600' : 'text-amber-600'}`}
        aria-hidden
      />
      <span>{label}</span>
    </span>
  )
}

export function Footer() {
  const [jobModalOpen, setJobModalOpen] = useState(false)
  const { data: health, isLoading } = useApiQuery<HealthResponse>(
    ['health'],
    '/health',
    { retry: false, refetchInterval: 30_000 }
  )
  const { data: workersHealth } = useApiQuery<WorkersHealthResponse>(
    ['workers-health'],
    '/api/jobs/workers/health',
    { retry: false, refetchInterval: 30_000 }
  )
  const { data: jobs = [] } = useApiQuery<JobStatus[]>(
    ['jobs', 'active'],
    '/api/jobs',
    { refetchInterval: jobModalOpen ? 2000 : 30_000 }
  )

  const connected = health?.status === 'ok' || health?.status === 'degraded'
  const statusColor = connected ? 'text-green-600' : 'text-amber-600'
  const statusLabel = isLoading ? 'Checking…' : connected ? 'Connected' : 'Disconnected'
  const activeCount = jobs.filter((j) => j.status === 'pending' || j.status === 'running').length

  return (
    <>
      <footer
        className="flex h-10 flex-wrap items-center justify-center gap-x-4 gap-y-1 border-t border-border bg-card px-4 py-1.5 text-xs text-muted-foreground"
        style={{ gridColumn: '1 / -1' }}
      >
        <span className="flex items-center gap-1.5">
          <Circle
            className={`h-1.5 w-1.5 fill-current ${statusColor}`}
            aria-hidden
          />
          {statusLabel}
        </span>
        {health && (
          <span className="flex items-center gap-3" aria-label="Component status">
            <StatusDot ok={health.database === 'ok'} label="DB" />
            <StatusDot ok={health.redis === 'ok'} label="Redis" />
            <StatusDot ok={health.neo4j === 'ok'} label="Neo4j" />
            <StatusDot ok={health.s3 === 'ok'} label="S3" />
            <StatusDot
              ok={['ok', 'at_capacity', 'disabled'].includes(health.dgx ?? 'disabled')}
              label={`DGX Cluster (${health.dgx === 'disabled' ? '—' : Math.max(1, health.dgx_cluster_size ?? 1)})`}
            />
            <StatusDot ok={workersHealth?.status === 'ok'} label="Workers" />
          </span>
        )}
        <button
          type="button"
          onClick={() => setJobModalOpen(true)}
          className="flex items-center gap-1 hover:text-foreground"
        >
          <ListTodo className="h-3.5 w-3.5" />
          Jobs {activeCount > 0 && `(${activeCount})`}
        </button>
        <span>ArchiMeades v0.1.0</span>
        <span>Research · Simulate · Infer · Publish</span>
      </footer>
      {jobModalOpen && (
        <JobMonitorModal onClose={() => setJobModalOpen(false)} jobs={jobs} />
      )}
    </>
  )
}

function JobMonitorModal({ onClose, jobs }: { onClose: () => void; jobs: JobStatus[] }) {
  const cancelMutation = useApiMutation<{ message: string; status: string }, { id: string }>(
    'post',
    (v) => `/api/jobs/${v.id}/cancel`
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-lg border border-border bg-card p-4 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Job Monitor</h3>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="max-h-60 overflow-auto space-y-2">
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No active jobs</p>
          ) : (
            jobs.map((j) => (
              <div
                key={j.id}
                className="flex items-center justify-between gap-2 rounded-md border border-border p-2 text-sm"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{j.job_type}</p>
                  <p className="text-xs text-muted-foreground">
                    {j.status}
                    {j.target_backend && (
                      <span className="ml-1.5 text-muted-foreground/80">
                        · {(j.target_backend === 'dgx_spark' ? 'DGX' : 'Mac')}
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  {(j.status === 'pending' || j.status === 'running') && (
                    <>
                      <div className="w-20">
                        <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${j.progress_percent}%` }}
                          />
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8 shrink-0 gap-1 text-destructive hover:bg-destructive/10 hover:text-destructive"
                        onClick={() => cancelMutation.mutate({ id: j.id })}
                        disabled={cancelMutation.isPending}
                        aria-label="Cancel job"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Cancel
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
