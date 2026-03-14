/**
 * Parameter Scan View - likelihood surface, contour plots.
 * WO-31/33: HDF5 storage, contour visualization.
 * WO-43: Grid config in left sidebar (ScanContext).
 */

import { useEffect, useState } from 'react'
import { Download, ChevronDown, ChevronUp } from 'lucide-react'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { useApiQuery } from '@/hooks/useApi'
import { LikelihoodContour } from '@/components/scan/LikelihoodContour'
import { useAuth } from '@/contexts/AuthContext'
import { useScan } from '@/contexts/ScanContext'

export function ScanPage() {
  const { setMode } = useWorkflow()
  const { getToken } = useAuth()
  const { scans } = useScan()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data: sliceData } = useApiQuery<{ ndim: number; x: number[]; y?: number[]; chi2: number[] | number[][] } | null>(
    ['scan-slice', expandedId],
    expandedId ? `/api/scans/${expandedId}/slice` : '',
    { enabled: !!expandedId }
  )
  const { data: bestfit } = useApiQuery<{ chi2_min: number; bestfit_params: Record<string, number> } | null>(
    ['scan-bestfit', expandedId],
    expandedId ? `/api/scans/${expandedId}/bestfit` : '',
    { enabled: !!expandedId }
  )

  useEffect(() => {
    setMode('scan')
    document.title = 'Parameter Scan · Gravitational Physics'
  }, [setMode])

  return (
    <div className="w-full max-w-4xl space-y-6">
      <h1 className="text-2xl font-bold">Parameter Scan</h1>
      <p className="text-muted-foreground">
        Configure grid in the right panel and run scans. Results appear below.
      </p>

      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-semibold mb-4">Recent Scans</h2>
        {scans.length === 0 ? (
          <p className="text-sm text-muted-foreground">No scans yet. Configure grid in the right panel and run a scan.</p>
        ) : (
          <ul className="space-y-2">
            {scans.map((s) => (
              <li key={s.id} className="border-b border-border last:border-0">
                <button
                  type="button"
                  onClick={() => setExpandedId(expandedId === s.id ? null : s.id)}
                  className="flex justify-between items-center text-sm py-2 w-full text-left hover:bg-muted/50 rounded px-2"
                >
                  <span>{s.theory_id} × {s.dataset_id} — {s.total_points} pts</span>
                  <span className="flex items-center gap-2">
                    <span className={s.status === 'completed' ? 'text-green-600' : s.status === 'failed' ? 'text-destructive' : 'text-muted-foreground'}>{s.status}</span>
                    {expandedId === s.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </span>
                </button>
                {expandedId === s.id && s.status === 'completed' && (
                  <div className="pb-4 px-2 space-y-3">
                    {bestfit && (
                      <div className="text-sm">
                        <span className="font-medium">Best fit:</span> χ² = {bestfit.chi2_min.toFixed(2)}
                        {Object.entries(bestfit.bestfit_params).map(([k, v]) => (
                          <span key={k} className="ml-2">{k}={v.toFixed(4)}</span>
                        ))}
                      </div>
                    )}
                    {sliceData && <LikelihoodContour data={sliceData} />}
                    <button
                      type="button"
                      onClick={async () => {
                        const token = getToken()
                        const base = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : 'http://localhost:8002')
                        const res = await fetch(`${base}/api/scans/${s.id}/download`, {
                          headers: token ? { Authorization: `Bearer ${token}` } : {},
                        })
                        if (!res.ok) return
                        const blob = await res.blob()
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url
                        a.download = `scan_${s.id}.h5`
                        a.click()
                        URL.revokeObjectURL(url)
                      }}
                      className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                    >
                      <Download className="h-4 w-4" />
                      Download HDF5
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
