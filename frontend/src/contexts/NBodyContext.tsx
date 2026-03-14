/**
 * N-body context - shared state for N-body visualization mode.
 * Full center panel view with config in right sidebar.
 */

import { createContext, useContext, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { useApiQuery } from '@/hooks/useApi'

interface Simulation {
  id: string
  theory_id: string
  params_json: string | null
  status: string
  progress_percent: number
}

interface NBodyState {
  simulationId: string | null
  nParticles: number
  nSteps: number
  usePreview: boolean
}

interface NBodyContextValue extends NBodyState {
  setSimulationId: (v: string | null) => void
  setNParticles: (v: number) => void
  setNSteps: (v: number) => void
  setUsePreview: (v: boolean) => void
  simulations: Simulation[]
  selectedSimulation: Simulation | null
  paramsJson: string | null
}

const NBodyContext = createContext<NBodyContextValue | null>(null)

export function NBodyProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const isNbody = location.pathname === '/nbody'

  const [simulationId, setSimulationId] = useState<string | null>(null)
  const [nParticles, setNParticles] = useState(64)
  const [nSteps, setNSteps] = useState(100)
  const [usePreview, setUsePreview] = useState(true)

  const { data: simulations = [] } = useApiQuery<Simulation[]>(
    ['simulations', 'nbody'],
    '/api/simulations',
    { enabled: isNbody, staleTime: 30_000 }
  )

  const nbodySimulations = simulations.filter((s) => {
    try {
      const p = s.params_json ? JSON.parse(s.params_json) : {}
      return p.observable_type === 'nbody' && s.status === 'completed'
    } catch {
      return false
    }
  })

  const selectedSimulation = nbodySimulations.find((s) => s.id === simulationId) ?? null

  const paramsJson =
    !usePreview && selectedSimulation?.params_json
      ? selectedSimulation.params_json
      : JSON.stringify({
          observable_type: 'nbody',
          n_particles: nParticles,
          n_steps: nSteps,
        })

  const effectiveSimulationId = usePreview ? null : (simulationId || null)

  const value: NBodyContextValue = {
    simulationId: effectiveSimulationId,
    nParticles,
    nSteps,
    usePreview,
    setSimulationId,
    setNParticles,
    setNSteps,
    setUsePreview,
    simulations: nbodySimulations,
    selectedSimulation,
    paramsJson,
  }

  return (
    <NBodyContext.Provider value={value}>
      {children}
    </NBodyContext.Provider>
  )
}

export function useNBody() {
  const ctx = useContext(NBodyContext)
  if (!ctx) throw new Error('useNBody must be used within NBodyProvider')
  return ctx
}
