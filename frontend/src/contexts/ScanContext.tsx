/**
 * Scan context - shared state for Parameter Scanning mode.
 * WO-43: Grid configuration in left sidebar per IRE blueprint.
 */

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from 'react'
import { useLocation } from 'react-router-dom'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'

export type AxisConfig = { name: string; min: number; max: number; n: number; scale: string }
export type ScanSummary = {
  id: string
  theory_id: string
  dataset_id: string
  status: string
  total_points: number
  created_at: string | null
}

const DEFAULT_AXES: AxisConfig[] = [
  { name: 'omega_m', min: 0.25, max: 0.35, n: 11, scale: 'linear' },
  { name: 'h0', min: 68, max: 72, n: 9, scale: 'linear' },
]

interface ScanContextValue {
  theoryId: string
  datasetId: string
  axes: AxisConfig[]
  setTheoryId: (v: string) => void
  setDatasetId: (v: string) => void
  setAxes: (v: AxisConfig[] | ((prev: AxisConfig[]) => AxisConfig[])) => void
  handleSubmit: () => void
  createScan: { mutate: (vars: { body: object }, opts?: { onSuccess?: () => void; onError?: (err: { detail?: string }) => void }) => void; isPending: boolean }
  scans: ScanSummary[]
  refetch: () => void
}

const ScanContext = createContext<ScanContextValue | null>(null)

export function ScanProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const isScan = location.pathname === '/scan'

  const [theoryId, setTheoryId] = useState('lcdm')
  const [datasetId, setDatasetId] = useState('synthetic')
  const [axes, setAxes] = useState<AxisConfig[]>(DEFAULT_AXES)

  const { data: scans = [], refetch } = useApiQuery<ScanSummary[]>(
    ['scans'],
    '/api/scans',
    { enabled: isScan }
  )

  const createScan = useApiMutation<{ id: string; status: string; total_points: number }, { body: object }>(
    'post',
    () => '/api/scans'
  )

  const handleSubmit = useCallback(() => {
    const total = axes.reduce((acc, a) => acc * a.n, 1)
    if (total > 100_000) {
      alert('Grid too large (max 100k points)')
      return
    }
    createScan.mutate(
      {
        body: {
          theory_id: theoryId,
          dataset_id: datasetId,
          axes,
          fixed_params: {},
        },
      },
      {
        onSuccess: () => refetch(),
        onError: (err) => alert(err?.detail ?? 'Scan failed'),
      }
    )
  }, [theoryId, datasetId, axes, createScan, refetch])

  const value: ScanContextValue = {
    theoryId,
    datasetId,
    axes,
    setTheoryId,
    setDatasetId,
    setAxes,
    handleSubmit,
    createScan,
    scans,
    refetch,
  }

  return (
    <ScanContext.Provider value={value}>
      {children}
    </ScanContext.Provider>
  )
}

export function useScan() {
  const ctx = useContext(ScanContext)
  if (!ctx) throw new Error('useScan must be used within ScanProvider')
  return ctx
}
