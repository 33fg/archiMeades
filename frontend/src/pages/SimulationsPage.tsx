/**
 * Simulations page - GPU-accelerated simulation runs.
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Cpu, Eye, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { QueryStateGuard } from '@/components/ui/QueryStateGuard'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'

interface Theory {
  id: string
  name: string
  identifier: string | null
}

interface SimulationCreatePayload {
  theory_id: string
  observable_type: string
  omega_m: number
  h0: number
  i_rel: number
  n_points: number
  n_particles?: number
  n_steps?: number
  dt?: number
}

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

const OBSERVABLE_OPTIONS = [
  { value: 'distance_modulus', label: 'Distance modulus (μ) — Hubble diagram for SNe Ia' },
  { value: 'nbody', label: 'N-body — particle simulation → distance modulus' },
  { value: 'angular_diameter', label: 'Angular diameter distance (coming soon)' },
  { value: 'luminosity', label: 'Luminosity distance (coming soon)' },
]

export function SimulationsPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [showForm, setShowForm] = useState(() => searchParams.get('create') === '1')
  const [theoryId, setTheoryId] = useState('')
  const [observableType, setObservableType] = useState('distance_modulus')
  const [omegaM, setOmegaM] = useState(0.31)
  const [h0, setH0] = useState(70)
  const [iRel, setIRel] = useState(1.451782)
  const [nPoints, setNPoints] = useState(50)
  const [nParticles, setNParticles] = useState(64)
  const [nSteps, setNSteps] = useState(100)

  const { data: simulations, isLoading, error, refetch } = useApiQuery<Simulation[]>(
    ['simulations'],
    '/api/simulations'
  )
  const { data: theories } = useApiQuery<Theory[]>(['theories'], '/api/theories')
  const createMutation = useApiMutation<Simulation, SimulationCreatePayload>(
    'post',
    () => '/api/simulations'
  )
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/simulations/${v.id}`
  )

  useEffect(() => {
    document.title = 'Simulations · Gravitational Physics'
  }, [])

  useEffect(() => {
    if (showForm && searchParams.get('create') === '1') {
      setSearchParams({}, { replace: true })
    }
  }, [showForm, searchParams, setSearchParams])

  return (
    <QueryStateGuard
      isLoading={isLoading}
      error={error}
      refetch={refetch}
      loadingMessage="Loading simulations..."
    >
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center gap-2">
        <Cpu className="h-6 w-6 text-muted-foreground" />
        <h1 className="text-2xl font-bold text-foreground">Simulations</h1>
      </div>
      <p className="text-muted-foreground">
        GPU-accelerated simulation runs for testing gravitational theories. Simulates{' '}
        <strong>distance modulus (μ)</strong> or <strong>N-body</strong> particle systems. Completed
        N-body simulations can be visualized in 3D — use &quot;View visualization&quot; or open the
        simulation detail.
      </p>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowForm((s) => !s)}
        className="w-fit gap-2"
      >
        <Plus className="h-4 w-4" />
        {showForm ? 'Cancel' : 'Create simulation'}
      </Button>
      {showForm && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (!theoryId) return
            createMutation.mutate(
              {
                theory_id: theoryId,
                observable_type: observableType,
                omega_m: omegaM,
                h0: h0,
                i_rel: iRel,
                n_points: nPoints,
                ...(observableType === 'nbody' && {
                  n_particles: nParticles,
                  n_steps: nSteps,
                  dt: 1e4,
                }),
              },
              {
                onSuccess: () => {
                  setTheoryId('')
                  setShowForm(false)
                },
              }
            )
          }}
          className="rounded-lg border border-border bg-card p-4 space-y-4"
        >
          <div>
            <label htmlFor="sim-theory" className="block text-sm font-medium text-foreground mb-1">
              Theory
            </label>
            <select
              id="sim-theory"
              value={theoryId}
              onChange={(e) => setTheoryId(e.target.value)}
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Select a theory...</option>
              {theories?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
            {(!theories || theories.length === 0) && !createMutation.isPending && (
              <p className="mt-1 text-xs text-muted-foreground">
                No theories yet. Create one in the Theories section first.
              </p>
            )}
          </div>

          <div>
            <label htmlFor="sim-observable" className="block text-sm font-medium text-foreground mb-1">
              Observable type
            </label>
            <select
              id="sim-observable"
              value={observableType}
              onChange={(e) => setObservableType(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {OBSERVABLE_OPTIONS.map((o) => (
                <option
                  key={o.value}
                  value={o.value}
                  disabled={!['distance_modulus', 'nbody'].includes(o.value)}
                >
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="sim-omega-m" className="block text-sm font-medium text-foreground mb-1">
                Ωₘ = {omegaM.toFixed(3)}
              </label>
              <input
                id="sim-omega-m"
                type="range"
                min={0.2}
                max={0.45}
                step={0.005}
                value={omegaM}
                onChange={(e) => setOmegaM(+e.target.value)}
                className="w-full"
              />
            </div>
            <div>
              <label htmlFor="sim-h0" className="block text-sm font-medium text-foreground mb-1">
                H₀ = {h0}
              </label>
              <input
                id="sim-h0"
                type="range"
                min={65}
                max={75}
                step={0.5}
                value={h0}
                onChange={(e) => setH0(+e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          {(() => {
            const theory = theories?.find((t) => t.id === theoryId)
            const isG4v =
              theory?.name?.toLowerCase().includes('g4v') ||
              theory?.identifier?.toLowerCase().includes('g4v')
            return isG4v ? (
              <div>
                <label htmlFor="sim-i-rel" className="block text-sm font-medium text-foreground mb-1">
                  i_rel = {iRel.toFixed(4)} (G4v)
                </label>
                <input
                  id="sim-i-rel"
                  type="range"
                  min={1.4}
                  max={1.5}
                  step={0.0005}
                  value={iRel}
                  onChange={(e) => setIRel(+e.target.value)}
                  className="w-full"
                />
              </div>
            ) : null
          })()}

          <div>
            <label htmlFor="sim-n-points" className="block text-sm font-medium text-foreground mb-1">
              Number of redshift points
            </label>
            <input
              id="sim-n-points"
              type="number"
              min={10}
              max={500}
              value={nPoints}
              onChange={(e) => setNPoints(Math.max(10, Math.min(500, +e.target.value)))}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>

          {observableType === 'nbody' && (
            <>
              <div className="rounded-md border border-primary/30 bg-primary/5 px-3 py-2">
                <p className="text-xs font-medium text-foreground">
                  Preview 3D visualization
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  After creating and completing an N-body simulation, open it to see the 3D particle
                  animation. If output is unavailable, a live preview will be shown instead.
                </p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="sim-n-particles" className="block text-sm font-medium text-foreground mb-1">
                  Particles
                </label>
                <input
                  id="sim-n-particles"
                  type="number"
                  min={16}
                  max={256}
                  value={nParticles}
                  onChange={(e) => setNParticles(Math.max(16, Math.min(256, +e.target.value)))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label htmlFor="sim-n-steps" className="block text-sm font-medium text-foreground mb-1">
                  Time steps
                </label>
                <input
                  id="sim-n-steps"
                  type="number"
                  min={10}
                  max={500}
                  value={nSteps}
                  onChange={(e) => setNSteps(Math.max(10, Math.min(500, +e.target.value)))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            </div>
            </>
          )}

          {theoryId && theories?.find((t) => t.id === theoryId) && (
            <p className="text-sm text-muted-foreground rounded-md bg-muted/50 px-3 py-2">
              <span className="font-medium text-foreground">Preview:</span> Simulating{' '}
              <strong>{OBSERVABLE_OPTIONS.find((o) => o.value === observableType)?.label?.split('—')[0].trim() ?? observableType}</strong>{' '}
              {observableType === 'nbody'
                ? `with ${nParticles} particles, ${nSteps} steps, n=${nPoints} points`
                : `with Ωₘ=${omegaM.toFixed(3)}, H₀=${h0}, n=${nPoints}`}{' '}
              using {theories.find((t) => t.id === theoryId)!.name}
            </p>
          )}

          {createMutation.error && (
            <p className="text-sm text-destructive">{createMutation.error.detail}</p>
          )}
          <Button type="submit" disabled={createMutation.isPending || !theoryId || !theories?.length}>
            {createMutation.isPending ? 'Creating...' : 'Create simulation'}
          </Button>
        </form>
      )}
      {!simulations || simulations.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border bg-muted/30 p-8 text-center">
          <p className="text-muted-foreground">No simulations yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Click Create simulation above to add one. Create a theory first if needed.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {simulations.map((sim) => (
            <li key={sim.id} className="flex gap-2">
              <div
                role="button"
                tabIndex={0}
                onClick={() => navigate(`/simulations/${sim.id}`)}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/simulations/${sim.id}`)}
                className="flex-1 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/50 cursor-pointer"
              >
                {(() => {
                  try {
                    const p = sim.params_json ? JSON.parse(sim.params_json) : {}
                    if (p.observable_type === 'nbody' && sim.status === 'completed') {
                      return (
                        <div className="mb-2 flex justify-end">
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 gap-1.5 text-xs"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/simulations/${sim.id}`)
                            }}
                          >
                            <Eye className="h-3.5 w-3.5" />
                            View visualization
                          </Button>
                        </div>
                      )
                    }
                  } catch { /* ignore */ }
                  return null
                })()}
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-muted-foreground">{sim.id.slice(0, 8)}…</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      sim.status === 'completed'
                        ? 'bg-green-500/20 text-green-700 dark:text-green-400'
                        : sim.status === 'failed'
                          ? 'bg-red-500/20 text-red-700 dark:text-red-400'
                          : sim.status === 'running'
                            ? 'bg-blue-500/20 text-blue-700 dark:text-blue-400'
                            : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {sim.status}
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  <span className="font-medium">
                    {(() => {
                      try {
                        const p = sim.params_json ? JSON.parse(sim.params_json) : {}
                        const obs = p.observable_type === 'distance_modulus' ? 'Distance modulus (μ)' : p.observable_type === 'nbody' ? 'N-body' : p.observable_type ?? 'Distance modulus (μ)'
                        const pm = p.omega_m != null ? ` Ωₘ=${Number(p.omega_m).toFixed(2)}` : ''
                        const ph = p.h0 != null ? ` H₀=${p.h0}` : ''
                        return `${obs}${pm}${ph}`
                      } catch {
                        return 'Distance modulus (μ)'
                      }
                    })()}
                  </span>
                  {theories?.find((t) => t.id === sim.theory_id) ? (
                    <>
                      {' · '}
                      <Link
                        to={`/theories/${sim.theory_id}`}
                        className="text-primary hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {theories.find((t) => t.id === sim.theory_id)!.name}
                      </Link>
                    </>
                  ) : (
                    ` · ${sim.theory_id.slice(0, 8)}…`
                  )}{' '}
                  • {sim.progress_percent}% complete
                </p>
                {sim.error_message && (
                  <p className="mt-1 text-xs text-destructive">{sim.error_message}</p>
                )}
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-muted-foreground hover:text-destructive"
                disabled={deleteMutation.isPending}
                onClick={() => {
                  if (window.confirm('Delete this simulation?')) {
                    deleteMutation.mutate({ id: sim.id })
                  }
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
    </QueryStateGuard>
  )
}
