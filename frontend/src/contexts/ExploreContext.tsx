/**
 * Explore context - shared state for Theory Exploration mode.
 * WO-42, IRE blueprint: parameter controls in left sidebar, plots in center.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { useLocation } from 'react-router-dom'
import { useApiQuery } from '@/hooks/useApi'
import { api } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

const DEBOUNCE_MS = 100

export type DatasetData = { redshift: number[]; observable: number[]; stat_unc: number[] }

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(t)
  }, [value, delayMs])
  return debounced
}

interface ExploreState {
  theoryId: string
  datasetId: string
  omegaM: number
  h0: number
  iRel: number
}

interface ExploreContextValue extends ExploreState {
  setTheoryId: (v: string) => void
  setDatasetId: (v: string) => void
  setOmegaM: (v: number) => void
  setH0: (v: number) => void
  setIRel: (v: number) => void
  datasets: { id: string; name: string; type: string }[]
  datasetData: DatasetData | undefined
  loadingData: boolean
  theoryCurve: { z: number[]; mu: number[] } | null
  chi2: number | null
  loadingPrediction: boolean
}

const ExploreContext = createContext<ExploreContextValue | null>(null)

export function ExploreProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { getToken } = useAuth()
  const isExplore = location.pathname === '/explore'

  const [theoryId, setTheoryId] = useState('lcdm')
  const [datasetId, setDatasetId] = useState('synthetic')
  const [omegaM, setOmegaM] = useState(0.31)
  const [h0, setH0] = useState(70)
  const [iRel, setIRel] = useState(1.451782)

  const debouncedOmegaM = useDebouncedValue(omegaM, DEBOUNCE_MS)
  const debouncedH0 = useDebouncedValue(h0, DEBOUNCE_MS)
  const debouncedIRel = useDebouncedValue(iRel, DEBOUNCE_MS)

  const { data: datasets } = useApiQuery<{ id: string; name: string; type: string }[]>(
    ['observations', 'datasets'],
    '/api/observations/datasets',
    { enabled: isExplore, staleTime: 0, refetchOnMount: 'always', refetchOnWindowFocus: true }
  )

  const { data: datasetData, isLoading: loadingData } = useApiQuery<DatasetData>(
    ['dataset-data', datasetId],
    `/api/observations/datasets/${datasetId}/data`,
    { enabled: isExplore && !!datasetId }
  )

  const [theoryCurve, setTheoryCurve] = useState<{ z: number[]; mu: number[] } | null>(null)
  const [chi2, setChi2] = useState<number | null>(null)
  const [loadingPrediction, setLoadingPrediction] = useState(false)

  const fetchPrediction = useCallback(async () => {
    if (!isExplore || !datasetData?.redshift?.length) return
    setLoadingPrediction(true)
    try {
      const token = getToken()
      const [predRes, chi2Res] = await Promise.all([
        api.post<{ redshifts: number[]; distance_modulus: (number | null)[] }>(
          '/api/observables/distance_modulus',
          {
            theory_id: theoryId,
            redshifts: datasetData.redshift,
            omega_m: debouncedOmegaM,
            h0: debouncedH0,
            i_rel: debouncedIRel,
          },
          token
        ),
        api.post<{ chi_squared: number }>(
          '/api/likelihood/evaluate',
          {
            theory_id: theoryId,
            dataset_id: datasetId,
            omega_m: debouncedOmegaM,
            h0: debouncedH0,
            i_rel: debouncedIRel,
          },
          token
        ),
      ])
      const mu = (predRes.distance_modulus ?? []).map((v) => (v != null ? v : NaN))
      setTheoryCurve({ z: predRes.redshifts ?? datasetData.redshift, mu })
      setChi2(chi2Res.chi_squared)
    } catch {
      setTheoryCurve(null)
      setChi2(null)
    } finally {
      setLoadingPrediction(false)
    }
  }, [
    isExplore,
    datasetData,
    theoryId,
    datasetId,
    debouncedOmegaM,
    debouncedH0,
    debouncedIRel,
    getToken,
  ])

  useEffect(() => {
    fetchPrediction()
  }, [fetchPrediction])

  const value: ExploreContextValue = {
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
    datasets: datasets ?? [{ id: 'synthetic', name: 'Synthetic (5 SNe)', type: '' }, { id: 'pantheon', name: 'Pantheon (1048 SNe)', type: '' }],
    datasetData,
    loadingData,
    theoryCurve,
    chi2,
    loadingPrediction,
  }

  return (
    <ExploreContext.Provider value={value}>
      {children}
    </ExploreContext.Provider>
  )
}

export function useExplore() {
  const ctx = useContext(ExploreContext)
  if (!ctx) throw new Error('useExplore must be used within ExploreProvider')
  return ctx
}
