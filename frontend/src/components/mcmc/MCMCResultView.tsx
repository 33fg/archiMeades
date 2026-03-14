/**
 * WO-37: MCMC posterior visualization - summary, diagnostics, trace, triangle plot.
 * WO-37: Parameter selection for triangle plot filtering.
 */

import { useEffect, useState } from 'react'
import { X, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { TracePlot } from './TracePlot'
import { TrianglePlot } from './TrianglePlot'

type Diagnostics = {
  rhat?: Record<string, number>
  ess_bulk?: Record<string, number>
  ess_tail?: Record<string, number>
  n_divergences?: number
  divergence_rate?: number
  warning?: string | null
}

function rhatColor(v: number): string {
  if (v <= 1.01) return 'text-green-600'
  if (v <= 1.1) return 'text-yellow-600'
  return 'text-red-600'
}
function essColor(v: number): string {
  if (v >= 400) return 'text-green-600'
  if (v >= 100) return 'text-yellow-600'
  return 'text-red-600'
}

export function MCMCResultView({
  result,
  onClear,
  targetBackend,
}: {
  result: Record<string, unknown>
  onClear: () => void
  targetBackend?: string | null
}) {
  const backendLabel = targetBackend === 'dgx_spark' ? 'DGX' : targetBackend === 'mac_gpu' ? 'Mac' : null
  const posterior = (result.posterior_samples ?? {}) as Record<string, number[] | number[][]>
  const paramNames = (result.param_names ?? []) as string[]
  const diag = (result.diagnostics ?? {}) as Diagnostics

  const flatten = (arr: number[] | number[][]): number[] =>
    Array.isArray(arr) && Array.isArray(arr[0]) ? (arr as number[][]).flat() : (arr as number[])

  const mean = (xs: number[]) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0
  const std = (xs: number[]) => {
    if (xs.length < 2) return 0
    const m = mean(xs)
    return Math.sqrt(xs.reduce((s, x) => s + (x - m) ** 2, 0) / (xs.length - 1))
  }
  const quantile = (xs: number[], q: number) => {
    const s = [...xs].sort((a, b) => a - b)
    const i = Math.floor(q * (s.length - 1))
    return s[i] ?? 0
  }

  const samples: Record<string, number[]> = {}
  for (const p of paramNames) {
    const raw = posterior[p]
    if (raw) samples[p] = flatten(raw)
  }

  // WO-37: Parameter selection for triangle plot - default all selected
  const [triangleSelection, setTriangleSelection] = useState<Record<string, boolean>>({})
  useEffect(() => {
    setTriangleSelection((prev) => {
      const next: Record<string, boolean> = {}
      for (const p of paramNames) next[p] = prev[p] ?? true
      return next
    })
  }, [paramNames.join(',')])
  const selectedTriangleParams = paramNames.filter((p) => triangleSelection[p] !== false)

  const summaryRows = paramNames.map((p) => {
    const xs = samples[p] ?? []
    return {
      param: p,
      mean: mean(xs),
      std: std(xs),
      q05: quantile(xs, 0.05),
      q50: quantile(xs, 0.5),
      q95: quantile(xs, 0.95),
    }
  })

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold">Posterior Results</h2>
          {backendLabel && (
            <span className="rounded bg-muted px-2 py-0.5 text-xs">{backendLabel}</span>
          )}
        </div>
        <div className="flex gap-2">
          {(result.getdist as { chains_txt?: string; paramnames_txt?: string })?.chains_txt && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const gd = result.getdist as { chains_txt: string; paramnames_txt: string }
                const a1 = document.createElement('a')
                a1.href = URL.createObjectURL(new Blob([gd.chains_txt], { type: 'text/plain' }))
                a1.download = 'chains.txt'
                a1.click()
                URL.revokeObjectURL(a1.href)
                const a2 = document.createElement('a')
                a2.href = URL.createObjectURL(new Blob([gd.paramnames_txt], { type: 'text/plain' }))
                a2.download = 'paramnames'
                a2.click()
                URL.revokeObjectURL(a2.href)
              }}
            >
              <Download className="h-4 w-4" />
              GetDist
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={onClear}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {diag.warning && (
        <div className="rounded-md bg-amber-500/10 border border-amber-500/30 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          {diag.warning}
        </div>
      )}

      <div>
        <h3 className="text-sm font-medium mb-2">Summary Statistics</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2">Param</th>
                <th className="text-right py-2">Mean</th>
                <th className="text-right py-2">Std</th>
                <th className="text-right py-2">5%</th>
                <th className="text-right py-2">50%</th>
                <th className="text-right py-2">95%</th>
                {Object.keys(diag.rhat ?? {}).length > 0 && <th className="text-right py-2">R̂</th>}
                {Object.keys(diag.ess_bulk ?? {}).length > 0 && <th className="text-right py-2">ESS</th>}
              </tr>
            </thead>
            <tbody>
              {summaryRows.map((r) => (
                <tr key={r.param} className="border-b border-border/50">
                  <td className="py-1.5">{r.param}</td>
                  <td className="text-right">{r.mean.toFixed(4)}</td>
                  <td className="text-right">{r.std.toFixed(4)}</td>
                  <td className="text-right">{r.q05.toFixed(4)}</td>
                  <td className="text-right">{r.q50.toFixed(4)}</td>
                  <td className="text-right">{r.q95.toFixed(4)}</td>
                  {Object.keys(diag.rhat ?? {}).length > 0 && (
                    <td className={`text-right font-mono ${rhatColor(diag.rhat![r.param] ?? 1)}`}>
                      {(diag.rhat ?? {})[r.param]?.toFixed(4) ?? '—'}
                    </td>
                  )}
                  {Object.keys(diag.ess_bulk ?? {}).length > 0 && (
                    <td className={`text-right font-mono ${essColor((diag.ess_bulk ?? {})[r.param] ?? 0)}`}>
                      {(diag.ess_bulk ?? {})[r.param] ?? '—'}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {(diag.n_divergences ?? 0) > 0 && (
        <p className="text-sm text-muted-foreground">
          Divergences: {diag.n_divergences} ({((diag.divergence_rate ?? 0) * 100).toFixed(2)}%)
        </p>
      )}

      <TracePlot samples={samples} paramNames={paramNames} />
      {paramNames.length >= 2 && (
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium">Triangle plot parameters</span>
            {paramNames.map((p) => (
              <label
                key={p}
                className="flex items-center gap-1.5 cursor-pointer text-sm text-muted-foreground hover:text-foreground"
              >
                <input
                  type="checkbox"
                  checked={triangleSelection[p] !== false}
                  onChange={(e) =>
                    setTriangleSelection((s) => ({ ...s, [p]: e.target.checked }))
                  }
                  className="rounded border-input"
                />
                {p}
              </label>
            ))}
          </div>
          {selectedTriangleParams.length >= 2 ? (
            <TrianglePlot samples={samples} paramNames={selectedTriangleParams} />
          ) : (
            <p className="text-sm text-muted-foreground">
              Select ≥2 parameters to show triangle plot.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
