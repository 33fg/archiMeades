/**
 * MCMC context - shared state for MCMC Inference mode.
 * WO-37/44: Config in right panel per IRE blueprint.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { useLocation } from 'react-router-dom'
import { useApiMutation } from '@/hooks/useApi'
import { api } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

export type PriorSpec = { type: string; low?: number; high?: number; mean?: number; std?: number }

type JobStatusResponse = {
  id: string
  status: string
  progress_percent: number
  error_message: string | null
  result_ref: string | null
  target_backend?: string | null
}

interface MCMCContextValue {
  theoryId: string
  datasetId: string
  priorSpec: Record<string, PriorSpec>
  setTheoryId: (v: string) => void
  setDatasetId: (v: string) => void
  setPriorSpec: (v: Record<string, PriorSpec> | ((p: Record<string, PriorSpec>) => Record<string, PriorSpec>)) => void
  sampler: 'numpyro' | 'emcee'
  setSampler: (v: 'numpyro' | 'emcee') => void
  numSamples: number
  numWarmup: number
  numChains: number
  runInBackground: boolean
  setNumSamples: (v: number) => void
  setNumWarmup: (v: number) => void
  setNumChains: (v: number) => void
  setRunInBackground: (v: boolean) => void
  handleRun: () => void
  runMCMC: ReturnType<typeof useApiMutation<unknown, { body: object }>>
  submitJob: ReturnType<typeof useApiMutation<unknown, { body: object }>>
  lastResult: Record<string, unknown> | null
  setLastResult: (v: Record<string, unknown> | null) => void
  asyncJobId: string | null
  asyncProgress: number
  asyncStatus: string
  asyncTargetBackend: string | null
  asyncError: string | null
  estimatedFlops: number
  effectivePriorSpec: Record<string, PriorSpec>
}

const MCMCContext = createContext<MCMCContextValue | null>(null)

export function MCMCProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { getToken } = useAuth()
  const isInference = location.pathname === '/inference'

  const [theoryId, setTheoryId] = useState('lcdm')
  const [datasetId, setDatasetId] = useState('synthetic')
  const [priorSpec, setPriorSpec] = useState<Record<string, PriorSpec>>({
    omega_m: { type: 'uniform', low: 0.2, high: 0.5 },
    h0: { type: 'uniform', low: 65, high: 75 },
  })
  const [sampler, setSampler] = useState<'numpyro' | 'emcee'>('numpyro')
  const [numSamples, setNumSamples] = useState(500)
  const [numWarmup, setNumWarmup] = useState(250)
  const [numChains, setNumChains] = useState(2)
  const [runInBackground, setRunInBackground] = useState(false)
  const [lastResult, setLastResult] = useState<Record<string, unknown> | null>(null)
  const [asyncJobId, setAsyncJobId] = useState<string | null>(null)
  const [asyncProgress, setAsyncProgress] = useState(0)
  const [asyncStatus, setAsyncStatus] = useState('')
  const [asyncTargetBackend, setAsyncTargetBackend] = useState<string | null>(null)
  const [asyncError, setAsyncError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const effectivePriorSpec =
    theoryId === 'g4v'
      ? { ...priorSpec, i_rel: priorSpec.i_rel ?? { type: 'uniform', low: 1.4, high: 1.5 } }
      : priorSpec

  const numParams = Object.keys(effectivePriorSpec).length
  const stepsPerChain = numWarmup + numSamples
  const totalSteps = stepsPerChain * numChains
  const estimatedFlops = totalSteps * 1e6 * numParams

  const runMCMC = useApiMutation<unknown, { body: object }>('post', () => '/api/mcmc/runs')
  const submitJob = useApiMutation<unknown, { body: object }>('post', () => '/api/jobs/submit')

  const pollJobStatus = useCallback(async (jobId: string) => {
    const res = await api.get<JobStatusResponse>(`/api/jobs/${jobId}/status`, getToken())
    setAsyncStatus(res.status)
    setAsyncProgress(res.progress_percent)
    if (res.target_backend) setAsyncTargetBackend(res.target_backend)
    if (res.status === 'completed') {
      if (res.result_ref) {
        try {
          const parsed = JSON.parse(res.result_ref) as Record<string, unknown>
          setLastResult(parsed)
        } catch {
          setAsyncError('Failed to parse job result')
        }
      } else {
        setAsyncError('Job completed but no result')
      }
      setAsyncJobId(null)
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    } else if (res.status === 'failed') {
      setAsyncError(res.error_message ?? 'Job failed')
      setAsyncJobId(null)
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [getToken])

  useEffect(() => {
    if (!asyncJobId || !isInference) return
    const id = setInterval(() => pollJobStatus(asyncJobId), 2000)
    pollRef.current = id
    void pollJobStatus(asyncJobId)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [asyncJobId, pollJobStatus, isInference])

  const handleRun = useCallback(() => {
    setAsyncError(null)
    if (runInBackground) {
      submitJob.mutate(
        {
          body: {
            job_type: 'mcmc',
            priority: 'batch',
            payload: {
              theory_id: theoryId,
              dataset_id: datasetId,
              prior_spec: effectivePriorSpec,
              num_samples: numSamples,
              num_warmup: numWarmup,
              num_chains: numChains,
              sampler,
            },
          },
        },
        {
          onSuccess: (data: unknown) => {
            const d = data as { id: string; target_backend?: string }
            setAsyncJobId(d.id)
            setAsyncStatus('submitted')
            setAsyncProgress(0)
            setAsyncTargetBackend(d.target_backend ?? null)
          },
          onError: (err: { detail?: string }) => setAsyncError(err?.detail ?? 'Job submission failed'),
        }
      )
    } else {
      runMCMC.mutate(
        {
          body: {
            theory_id: theoryId,
            dataset_id: datasetId,
            prior_spec: effectivePriorSpec,
            num_samples: numSamples,
            num_warmup: numWarmup,
            num_chains: numChains,
            sampler,
          },
        },
        {
          onSuccess: (data: unknown) => setLastResult(data as Record<string, unknown>),
          onError: (err: { detail?: string }) => alert(err?.detail ?? 'MCMC failed'),
        }
      )
    }
  }, [
    runInBackground,
    theoryId,
    datasetId,
    effectivePriorSpec,
    numSamples,
    numWarmup,
    numChains,
    sampler,
    submitJob,
    runMCMC,
  ])

  const value: MCMCContextValue = {
    theoryId,
    datasetId,
    priorSpec,
    setTheoryId,
    setDatasetId,
    setPriorSpec,
    sampler,
    setSampler,
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
    lastResult,
    setLastResult,
    asyncJobId,
    asyncProgress,
    asyncStatus,
    asyncTargetBackend,
    asyncError,
    estimatedFlops,
    effectivePriorSpec,
  }

  return (
    <MCMCContext.Provider value={value}>
      {children}
    </MCMCContext.Provider>
  )
}

export function useMCMC() {
  const ctx = useContext(MCMCContext)
  if (!ctx) throw new Error('useMCMC must be used within MCMCProvider')
  return ctx
}
