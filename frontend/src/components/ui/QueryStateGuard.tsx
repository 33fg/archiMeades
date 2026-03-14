/**
 * QueryStateGuard - loading timeout and error handling with retry.
 * Prevents endless loading by showing "Taking too long" after a timeout.
 */

import { useEffect, useState, type ReactNode } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { type ApiError } from '@/lib/api'

const LOADING_TIMEOUT_MS = 8_000
const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8002'

function formatErrorDetail(err: ApiError): string {
  const d = err.detail as unknown
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((e: unknown) => (e && typeof e === 'object' && ('msg' in e || 'message' in e) ? String((e as { msg?: string; message?: string }).msg ?? (e as { msg?: string; message?: string }).message) : String(e))).join(', ')
  if (d && typeof d === 'object') return (d as { message?: string }).message ?? JSON.stringify(d)
  return 'An error occurred'
}

interface QueryStateGuardProps {
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
  loadingMessage?: string
  children: ReactNode
}

export function QueryStateGuard({
  isLoading,
  error,
  refetch,
  loadingMessage = 'Loading...',
  children,
}: QueryStateGuardProps) {
  const [loadingTimedOut, setLoadingTimedOut] = useState(false)

  useEffect(() => {
    if (!isLoading) {
      queueMicrotask(() => setLoadingTimedOut(false))
      return
    }
    const t = setTimeout(() => setLoadingTimedOut(true), LOADING_TIMEOUT_MS)
    return () => clearTimeout(t)
  }, [isLoading])

  if (error) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4 p-8 text-center">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div>
          <p className="font-medium text-destructive">Failed to load</p>
          <p className="mt-1 text-sm text-muted-foreground">{formatErrorDetail(error)}</p>
          <p className="mt-2 text-xs text-muted-foreground">
            Backend: {backendUrl}
          </p>
        </div>
        <Button variant="outline" onClick={() => refetch()} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  if (isLoading && loadingTimedOut) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4 p-8 text-center">
        <p className="text-muted-foreground">Taking longer than expected.</p>
        <p className="text-sm text-muted-foreground">
          Backend may be starting or unreachable. Check {backendUrl}
        </p>
        <Button variant="outline" onClick={() => refetch()} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center p-8">
        <p className="text-muted-foreground">{loadingMessage}</p>
      </div>
    )
  }

  return <>{children}</>
}
