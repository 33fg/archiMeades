/**
 * N-body config controls for right sidebar.
 * Simulation selector or live preview with params.
 */

import { Link } from 'react-router-dom'
import { useNBody } from '@/contexts/NBodyContext'

export function NBodyConfigControls() {
  const {
    usePreview,
    setUsePreview,
    simulationId,
    setSimulationId,
    simulations,
    nParticles,
    setNParticles,
    nSteps,
    setNSteps,
  } = useNBody()

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground">Source</p>
        <div className="flex gap-1 rounded-md border border-border p-0.5" role="tablist">
          <button
            type="button"
            onClick={() => setUsePreview(true)}
            className={`flex-1 rounded px-2 py-1.5 text-xs font-medium transition-colors ${
              usePreview ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            Live preview
          </button>
          <button
            type="button"
            onClick={() => setUsePreview(false)}
            className={`flex-1 rounded px-2 py-1.5 text-xs font-medium transition-colors ${
              !usePreview ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            Simulation
          </button>
        </div>
      </div>

      {usePreview ? (
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">
              Particles
            </label>
            <input
              type="number"
              min={16}
              max={128}
              value={nParticles}
              onChange={(e) => setNParticles(Math.max(16, Math.min(128, +e.target.value)))}
              className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">
              Time steps
            </label>
            <input
              type="number"
              min={20}
              max={200}
              value={nSteps}
              onChange={(e) => setNSteps(Math.max(20, Math.min(200, +e.target.value)))}
              className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Preview runs on-demand. Change params and the view updates.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <label className="block text-xs font-medium text-muted-foreground">
            Completed N-body simulation
          </label>
          <select
            value={simulationId ?? ''}
            onChange={(e) => setSimulationId(e.target.value || null)}
            className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
          >
            <option value="">Select…</option>
            {simulations.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id.slice(0, 8)}… ({s.progress_percent}%)
              </option>
            ))}
          </select>
          {simulations.length === 0 && (
            <p className="text-xs text-muted-foreground">
              No completed N-body simulations. Create one in{' '}
              <Link to="/simulations?create=1" className="text-primary hover:underline">
                Simulations
              </Link>
              .
            </p>
          )}
        </div>
      )}
    </div>
  )
}
