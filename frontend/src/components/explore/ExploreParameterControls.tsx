/**
 * WO-42: Parameter controls for Theory Exploration mode.
 * Rendered in left sidebar per IRE blueprint.
 */

import { useExplore } from '@/contexts/ExploreContext'

export function ExploreParameterControls() {
  const {
    theoryId,
    datasetId,
    omegaM,
    h0,
    iRel,
    setTheoryId,
    setDatasetId,
    setOmegaM,
    setH0,
    setIRel,
    datasets,
    chi2,
    loadingPrediction,
  } = useExplore()

  return (
    <div className="space-y-3 px-2">
      <div>
        <label className="block text-xs text-muted-foreground">Theory</label>
        <select
          value={theoryId}
          onChange={(e) => setTheoryId(e.target.value)}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          <option value="lcdm">Lambda-CDM</option>
          <option value="g4v">G4v</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground">Dataset</label>
        <select
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          {datasets.map((ds) => (
            <option key={ds.id} value={ds.id}>
              {ds.name}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground">
          Ωₘ = {omegaM.toFixed(3)}
        </label>
        <input
          type="range"
          min={0.2}
          max={0.45}
          step={0.005}
          value={omegaM}
          onChange={(e) => setOmegaM(+e.target.value)}
          className="mt-1 w-full"
        />
      </div>
      <div>
        <label className="block text-xs text-muted-foreground">H₀ = {h0}</label>
        <input
          type="range"
          min={65}
          max={75}
          step={0.5}
          value={h0}
          onChange={(e) => setH0(+e.target.value)}
          className="mt-1 w-full"
        />
      </div>
      {theoryId === 'g4v' && (
        <>
          <div className="rounded-md border border-amber-500/50 bg-amber-500/10 px-2 py-1.5 text-xs text-amber-700 dark:text-amber-400">
            G4v valid only at z &lt; 0.01.
          </div>
          <div>
            <label className="block text-xs text-muted-foreground">
              i_rel = {iRel.toFixed(4)}
            </label>
            <input
              type="range"
              min={1.4}
              max={1.5}
              step={0.0005}
              value={iRel}
              onChange={(e) => setIRel(+e.target.value)}
              className="mt-1 w-full"
            />
          </div>
        </>
      )}
      <div className="rounded-md bg-muted/50 px-3 py-2">
        <p className="text-xs text-muted-foreground">χ²</p>
        <p className="text-lg font-semibold tabular-nums">
          {loadingPrediction ? '…' : chi2 != null && Number.isFinite(chi2) ? chi2.toFixed(2) : '—'}
        </p>
      </div>
    </div>
  )
}
