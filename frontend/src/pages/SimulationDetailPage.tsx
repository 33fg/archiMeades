/**
 * Simulation detail page - view simulation status and cancel/delete.
 * WO-20: Provenance chain from Neo4j.
 */

import { useEffect, useState } from 'react'
import { ArrowLeft, AlertTriangle, CheckCircle2, Cpu, Download, Database, ShieldCheck, XCircle } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'
import { apiRequest } from '@/lib/api'
import { ProvenanceViewer } from '@/components/ProvenanceViewer'
import { NBodyVisualization } from '@/components/simulations/NBodyVisualization'
import { useProvenanceSettings } from '@/contexts/ProvenanceSettingsContext'

interface Simulation {
  id: string
  theory_id: string
  params_json: string | null
  status: string
  progress_percent: number
  error_message: string | null
  started_at: string | null
  completed_at: string | null
}

interface Theory {
  id: string
  name: string
  description: string | null
  equation_spec: string | null
}

interface SimulationOutput {
  id: string
  simulation_id: string
  s3_key: string
  file_size: number
  content_type: string | null
  checksum?: string | null
}

function OutputsWithVerification({ outputs }: { outputs: SimulationOutput[] }) {
  const [verified, setVerified] = useState<Record<string, boolean | null>>({})
  const [verifying, setVerifying] = useState<string | null>(null)
  const verify = async (out: SimulationOutput) => {
    setVerifying(out.id)
    try {
      const r = await apiRequest<{ verified: boolean | null; message: string }>(
        `/api/outputs/${out.id}/verify`
      )
      setVerified((prev) => ({ ...prev, [out.id]: r.verified }))
    } finally {
      setVerifying(null)
    }
  }
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
        Outputs
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {outputs.map((out) => {
          const v = verified[out.id]
          return (
            <div
              key={out.id}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-secondary px-3 py-1.5"
            >
              <a
                href={`/api/outputs/${out.id}/download`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 text-sm hover:underline"
              >
                <Download className="h-4 w-4" />
                {Math.round(out.file_size / 1024)} KB
              </a>
              {out.checksum && (
                <button
                  type="button"
                  onClick={() => verify(out)}
                  disabled={verifying === out.id}
                  className="rounded p-0.5 hover:bg-muted"
                  title={v === true ? 'Verified' : v === false ? 'File modified' : 'Verify integrity'}
                >
                  {verifying === out.id ? (
                    <span className="text-xs">…</span>
                  ) : v === true ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600" aria-label="Verified" />
                  ) : v === false ? (
                    <AlertTriangle className="h-4 w-4 text-destructive" aria-label="File modified" />
                  ) : (
                    <ShieldCheck className="h-4 w-4 text-muted-foreground" aria-label="Verify" />
                  )}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function SimulationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: simulation, isLoading, error } = useApiQuery<Simulation>(
    ['simulation', id!],
    `/api/simulations/${id}`,
    {
      enabled: !!id,
      refetchInterval: (q) =>
        ['pending', 'running'].includes(q.state.data?.status ?? '') ? 2000 : false,
    }
  )
  const { data: outputs } = useApiQuery<SimulationOutput[]>(
    ['outputs', id!],
    `/api/outputs?simulation_id=${id}`,
    { enabled: !!id && simulation?.status === 'completed' }
  )
  const { data: theory } = useApiQuery<Theory>(
    ['theory', simulation?.theory_id ?? ''],
    `/api/theories/${simulation?.theory_id}`,
    { enabled: !!simulation?.theory_id }
  )
  const { data: chain, error: chainError } = useApiQuery<{
    sim_id: string
    theory_id: string | null
    observation_ids: string[]
  }>(
    ['provenance', 'chain', id!],
    `/api/provenance/simulation/${id}/chain`,
    { enabled: !!id && !!simulation, retry: false }
  )
  const { settings: provSettings } = useProvenanceSettings()
  const queryClient = useQueryClient()
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/simulations/${v.id}`
  )
  const cancelMutation = useApiMutation<
    Simulation,
    { id: string; status: string }
  >('patch', (v) => `/api/simulations/${v.id}`)
  const registerMutation = useApiMutation<
    { dataset_id: string; name: string; num_points: number; observable_type: string },
    void
  >('post', () => `/api/simulations/${id!}/register-as-dataset`)

  useEffect(() => {
    document.title = simulation
      ? `Simulation ${simulation.id.slice(0, 8)}… · Gravitational Physics`
      : 'Simulation · Gravitational Physics'
  }, [simulation])

  const canCancel =
    simulation && (simulation.status === 'pending' || simulation.status === 'running')

  if (!id) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/simulations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Simulations
          </Button>
        </Link>
        <p className="text-destructive">Invalid simulation ID</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center p-8">
        <p className="text-muted-foreground">Loading simulation...</p>
      </div>
    )
  }

  if (error || !simulation) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/simulations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Simulations
          </Button>
        </Link>
        <p className="text-destructive">{error?.detail ?? 'Simulation not found'}</p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <Link to="/simulations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Simulations
          </Button>
        </Link>
        <div className="flex gap-2">
          {canCancel && (
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              disabled={cancelMutation.isPending}
              onClick={() => {
                if (window.confirm('Cancel this simulation?')) {
                  cancelMutation.mutate({ id: simulation.id, status: 'cancelled' })
                }
              }
            }
            >
              <XCircle className="h-4 w-4" />
              {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
            </Button>
          )}
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (window.confirm('Delete this simulation? This cannot be undone.')) {
                deleteMutation.mutate({ id: simulation.id }, { onSuccess: () => navigate('/simulations') })
              }
            }}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        <div className="flex items-center gap-2">
          <Cpu className="h-6 w-6 text-muted-foreground" />
          <h1 className="text-lg font-semibold text-foreground font-mono">
            {simulation.id}
          </h1>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              simulation.status === 'completed'
                ? 'bg-green-500/20 text-green-700 dark:text-green-400'
                : simulation.status === 'failed'
                  ? 'bg-red-500/20 text-red-700 dark:text-red-400'
                  : simulation.status === 'running'
                    ? 'bg-blue-500/20 text-blue-700 dark:text-blue-400'
                    : simulation.status === 'cancelled'
                      ? 'bg-amber-500/20 text-amber-700 dark:text-amber-400'
                      : 'bg-muted text-muted-foreground'
            }`}
          >
            {simulation.status}
          </span>
        </div>

        <div className="mt-6 space-y-3">
          <div className="rounded-md border border-border bg-muted/30 px-3 py-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              What this simulation produces
            </p>
            <p className="mt-1 text-sm">
              {(() => {
                try {
                  const p = simulation.params_json ? JSON.parse(simulation.params_json) : {}
                  if (p.observable_type === 'nbody') {
                    return (
                      <>
                        <strong>N-body</strong> — particle simulation → distance modulus
                        {theory && <> using <strong>{theory.name}</strong></>}
                      </>
                    )
                  }
                } catch { /* ignore */ }
                return (
                  <>
                    <strong>Distance modulus (μ)</strong> — Hubble diagram for supernovae
                    {theory && <> using <strong>{theory.name}</strong></>}
                  </>
                )
              })()}
            </p>
            {simulation.params_json && (() => {
              try {
                const p = JSON.parse(simulation.params_json)
                const parts = []
                if (p.observable_type === 'nbody') {
                  if (p.n_particles != null) parts.push(`${p.n_particles} particles`)
                  if (p.n_steps != null) parts.push(`${p.n_steps} steps`)
                }
                if (p.omega_m != null) parts.push(`Ωₘ=${Number(p.omega_m).toFixed(3)}`)
                if (p.h0 != null) parts.push(`H₀=${p.h0}`)
                if (p.i_rel != null) parts.push(`i_rel=${Number(p.i_rel).toFixed(4)}`)
                if (p.n_points != null) parts.push(`n=${p.n_points} points`)
                if (parts.length) {
                  return (
                    <p className="mt-1 text-xs text-muted-foreground">
                      Parameters: {parts.join(', ')}
                    </p>
                  )
                }
              } catch {
                /* ignore */
              }
              return null
            })()}
            <p className="mt-0.5 text-xs text-muted-foreground">
              μ(z) predicted by the theory. Can be registered as a dataset for Explore, Scan, or MCMC.
            </p>
          </div>

          {(() => {
            try {
              const p = simulation.params_json ? JSON.parse(simulation.params_json) : {}
              if (p.observable_type === 'nbody' && simulation.status === 'completed') {
                return (
                  <NBodyVisualization
                    simulationId={simulation.id}
                    paramsJson={simulation.params_json}
                    className="mt-2"
                  />
                )
              }
            } catch { /* ignore */ }
            return null
          })()}

          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Theory
            </p>
            <p className="mt-1">
              {theory ? (
                <Link
                  to={`/theories/${simulation.theory_id}`}
                  className="text-primary hover:underline"
                >
                  {theory.name}
                </Link>
              ) : (
                <span className="font-mono text-sm">{simulation.theory_id}</span>
              )}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Progress
            </p>
            <p className="mt-1">{simulation.progress_percent}%</p>
          </div>
          {simulation.started_at && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Started at
              </p>
              <p className="mt-1 text-sm">{simulation.started_at}</p>
            </div>
          )}
          {simulation.completed_at && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Completed at
              </p>
              <p className="mt-1 text-sm">{simulation.completed_at}</p>
            </div>
          )}
          {simulation.error_message && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Error
              </p>
              <p className="mt-1 text-sm text-destructive">{simulation.error_message}</p>
            </div>
          )}
          {/* WO-20, WO-47: Provenance viewer with verification and export */}
          <ProvenanceViewer
            type="simulation"
            data={chain ?? null}
            verified={!!chain}
            error={chainError?.status === 503}
            showExport={provSettings.showExportButton}
            showVerification={provSettings.verificationEnabled}
            compact
          />

          {simulation.status === 'completed' && outputs && outputs.length > 0 && (
            <>
              <OutputsWithVerification outputs={outputs} />
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  WO-67: Register as Dataset
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Use this simulation output in Explore, Scan, or MCMC by registering it as an
                  observational dataset.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2 gap-2"
                  disabled={registerMutation.isPending}
                  onClick={() =>
                    registerMutation.mutate(undefined as never, {
                      onSuccess: (res) => {
                        queryClient.invalidateQueries({ queryKey: ['observations', 'datasets'] })
                        navigate(`/observations/datasets/${res.dataset_id}`, { replace: true })
                      },
                    })
                  }
                >
                  <Database className="h-4 w-4" />
                  {registerMutation.isPending ? 'Registering...' : 'Register as dataset'}
                </Button>
                {registerMutation.isSuccess && (
                  <p className="mt-2 text-sm text-green-600">
                    Registered. Redirecting to dataset…
                  </p>
                )}
                {registerMutation.error && (
                  <p className="mt-2 text-sm text-destructive">{registerMutation.error.detail}</p>
                )}
              </div>
            </>
          )}
        </div>

        {deleteMutation.error && (
          <p className="mt-4 text-sm text-destructive">{deleteMutation.error.detail}</p>
        )}
        {cancelMutation.error && (
          <p className="mt-4 text-sm text-destructive">{cancelMutation.error.detail}</p>
        )}
      </div>
    </div>
  )
}
