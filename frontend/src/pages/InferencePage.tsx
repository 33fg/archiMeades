/**
 * MCMC Analysis View - posterior visualization, trace plots, triangle plot.
 * WO-37: MCMC Configuration and Posterior Visualization UI
 * WO-44: Config in right panel (MCMCContext).
 */

import { useEffect } from 'react'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { useMCMC } from '@/contexts/MCMCContext'
import { MCMCResultView } from '@/components/mcmc/MCMCResultView'

export function InferencePage() {
  const { setMode } = useWorkflow()
  const { lastResult, setLastResult, asyncTargetBackend } = useMCMC()

  useEffect(() => {
    setMode('mcmc')
    document.title = 'MCMC Inference · Gravitational Physics'
  }, [setMode])

  return (
    <div className="w-full max-w-5xl space-y-6">
      <h1 className="text-2xl font-bold">MCMC Inference</h1>
      <p className="text-muted-foreground">
        Configure HMC-NUTS sampling in the right panel, run chains, and explore posteriors below.
      </p>

      {lastResult ? (
        <MCMCResultView
          result={lastResult}
          onClear={() => setLastResult(null)}
          targetBackend={asyncTargetBackend ?? 'mac_gpu'}
        />
      ) : (
        <div className="rounded-lg border border-dashed border-border bg-muted/20 p-12 text-center">
          <p className="text-muted-foreground">
            No results yet. Configure priors and run MCMC in the right panel.
          </p>
        </div>
      )}
    </div>
  )
}
