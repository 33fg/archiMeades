/**
 * WO-37/44: MCMC configuration controls for right sidebar.
 */

import { Loader2, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PriorPreview } from '@/components/mcmc/PriorPreview'
import { useMCMC, type PriorSpec } from '@/contexts/MCMCContext'

export function MCMCConfigControls() {
  const {
    theoryId,
    datasetId,
    effectivePriorSpec,
    sampler,
    setSampler,
    setTheoryId,
    setDatasetId,
    setPriorSpec,
    numSamples,
    numWarmup,
    numChains,
    runInBackground,
    setNumSamples,
    setNumWarmup,
    setNumChains,
    setRunInBackground,
    handleRun,
    runMCMC,
    submitJob,
    asyncJobId,
    asyncProgress,
    asyncStatus,
    asyncTargetBackend,
    asyncError,
    estimatedFlops,
  } = useMCMC()

  return (
    <div className="space-y-3 overflow-y-auto max-h-[60vh]">
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
        <label className="block text-xs text-muted-foreground">Sampler</label>
        <select
          value={sampler}
          onChange={(e) => setSampler(e.target.value as 'numpyro' | 'emcee')}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          <option value="numpyro">NumPyro (HMC-NUTS)</option>
          <option value="emcee">Emcee (gradient-free)</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground">Dataset</label>
        <select
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          <option value="synthetic">Synthetic</option>
          <option value="pantheon">Pantheon</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground mb-1">Priors</label>
        <div className="space-y-1.5">
          {Object.entries(effectivePriorSpec).map(([name, spec]) => (
            <PriorRow
              key={name}
              name={name}
              spec={spec}
              onChange={(next) =>
                setPriorSpec((p) => ({ ...p, [name]: next }))
              }
            />
          ))}
        </div>
        <PriorPreview priorSpec={effectivePriorSpec} />
      </div>
      <div className="flex flex-wrap gap-2">
        <div>
          <label className="block text-xs text-muted-foreground">Samples</label>
          <input
            type="number"
            value={numSamples}
            onChange={(e) => setNumSamples(+e.target.value || 500)}
            className="mt-1 w-16 rounded border border-input bg-background px-1.5 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground">Warmup</label>
          <input
            type="number"
            value={numWarmup}
            onChange={(e) => setNumWarmup(+e.target.value || 250)}
            className="mt-1 w-16 rounded border border-input bg-background px-1.5 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground">Chains</label>
          <select
            value={numChains}
            onChange={(e) => setNumChains(+e.target.value)}
            className="mt-1 w-14 rounded border border-input bg-background px-1.5 py-1 text-sm"
          >
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={4}>4</option>
          </select>
        </div>
      </div>
      <label className="flex items-center gap-2 cursor-pointer text-xs">
        <input
          type="checkbox"
          checked={runInBackground}
          onChange={(e) => setRunInBackground(e.target.checked)}
          className="rounded border-input"
        />
        Run in background
      </label>
      <div className="rounded-md border border-border bg-muted/30 px-2 py-1.5 text-xs">
        <span className="text-muted-foreground">Cost:</span> {(estimatedFlops / 1e9).toFixed(2)} GFLOP
        {estimatedFlops >= 1e11 && <span className="ml-1 text-muted-foreground">(→DGX)</span>}
      </div>
      <Button
        size="sm"
        className="w-full gap-2"
        onClick={handleRun}
        disabled={runMCMC.isPending || submitJob.isPending}
      >
        {(runMCMC.isPending || submitJob.isPending) ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <Play className="h-3.5 w-3.5" />
        )}
        Run MCMC
      </Button>
      {(runMCMC.isPending || asyncJobId) && (
        <div className="rounded-md border border-border bg-muted/30 p-2 space-y-1 text-xs">
          {asyncJobId ? (
            <>
              <p>
                {asyncStatus === 'pending' || asyncStatus === 'submitted'
                  ? 'Queued'
                  : asyncStatus === 'running'
                  ? 'Sampling…'
                  : asyncStatus}
                {asyncTargetBackend && (
                  <span className="ml-1 text-muted-foreground">
                    ({asyncTargetBackend === 'dgx_spark' ? 'DGX' : 'Mac'})
                  </span>
                )}
              </p>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${Math.max(asyncProgress, 2)}%` }}
                />
              </div>
            </>
          ) : (
            <p>Running…</p>
          )}
        </div>
      )}
      {asyncError && <p className="text-xs text-destructive">{asyncError}</p>}
    </div>
  )
}

function PriorRow({
  name,
  spec,
  onChange,
}: {
  name: string
  spec: PriorSpec
  onChange: (s: PriorSpec) => void
}) {
  return (
    <div className="flex flex-wrap gap-1 items-center text-xs">
      <span className="w-14 text-muted-foreground truncate">{name}</span>
      <select
        value={spec.type}
        onChange={(e) => onChange({ ...spec, type: e.target.value })}
        className="w-16 rounded border border-input bg-background px-1 py-0.5"
      >
        <option value="uniform">U</option>
        <option value="normal">N</option>
      </select>
      {spec.type === 'uniform' ? (
        <>
          <input
            type="number"
            step="any"
            placeholder="lo"
            value={spec.low ?? ''}
            onChange={(e) => onChange({ ...spec, low: +e.target.value })}
            className="w-12 rounded border border-input bg-background px-1 py-0.5"
          />
          <input
            type="number"
            step="any"
            placeholder="hi"
            value={spec.high ?? ''}
            onChange={(e) => onChange({ ...spec, high: +e.target.value })}
            className="w-12 rounded border border-input bg-background px-1 py-0.5"
          />
        </>
      ) : (
        <>
          <input
            type="number"
            step="any"
            placeholder="μ"
            value={spec.mean ?? ''}
            onChange={(e) => onChange({ ...spec, mean: +e.target.value })}
            className="w-12 rounded border border-input bg-background px-1 py-0.5"
          />
          <input
            type="number"
            step="any"
            placeholder="σ"
            value={spec.std ?? ''}
            onChange={(e) => onChange({ ...spec, std: +e.target.value })}
            className="w-12 rounded border border-input bg-background px-1 py-0.5"
          />
        </>
      )}
    </div>
  )
}
