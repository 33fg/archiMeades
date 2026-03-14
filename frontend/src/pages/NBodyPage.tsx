/**
 * N-body full center panel view.
 * 3D particle visualization with config in right sidebar.
 */

import { useEffect } from 'react'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { useNBody } from '@/contexts/NBodyContext'
import { NBodyVisualization } from '@/components/simulations/NBodyVisualization'

export function NBodyPage() {
  const { setMode } = useWorkflow()
  const { simulationId, paramsJson } = useNBody()

  useEffect(() => {
    setMode('nbody')
    document.title = 'N-body Simulation · Gravitational Physics'
  }, [setMode])

  return (
    <div className="flex h-full w-full min-h-0 flex-col">
      <div className="mb-4 shrink-0">
        <h1 className="text-2xl font-bold">N-body Simulation</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Interactive 3D gravitational particle simulation. Drag to rotate, scroll to zoom, use
          playback controls to animate.
        </p>
      </div>
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-border bg-card p-4">
        <NBodyVisualization
          simulationId={simulationId ?? ''}
          paramsJson={paramsJson}
          fullHeight
        />
      </div>
    </div>
  )
}
