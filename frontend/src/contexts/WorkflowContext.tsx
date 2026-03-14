/**
 * Workflow context - mode switching for Explore/Scan/MCMC/Publish.
 * Frontend Component Hierarchy: AppShell mode-specific content.
 */

import { createContext, useContext, useState, type ReactNode } from 'react'

export type WorkflowMode = 'explore' | 'nbody' | 'scan' | 'mcmc' | 'publish'

interface WorkflowContextValue {
  mode: WorkflowMode
  setMode: (m: WorkflowMode) => void
}

const WorkflowContext = createContext<WorkflowContextValue | null>(null)

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<WorkflowMode>('explore')
  return (
    <WorkflowContext.Provider value={{ mode, setMode }}>
      {children}
    </WorkflowContext.Provider>
  )
}

export function useWorkflow() {
  const ctx = useContext(WorkflowContext)
  if (!ctx) throw new Error('useWorkflow must be used within WorkflowProvider')
  return ctx
}
