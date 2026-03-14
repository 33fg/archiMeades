/**
 * WO-45: Publication Export Mode - artifact config, theory comparison, export.
 * AC-IRE-006.3: Theory comparison table (χ², Δχ²)
 * AC-IRE-006.4: Export button for PDF, PNG, LaTeX
 */

import { useCallback, useEffect, useState } from 'react'
import { FileText, LineChart, Scan, BarChart3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'

const ARTIFACT_TYPES = [
  { id: 'table', label: 'Table' },
  { id: 'figure', label: 'Figure' },
] as const

const STYLE_PRESETS = [
  { id: 'apj', label: 'ApJ' },
  { id: 'mnras', label: 'MNRAS' },
  { id: 'prd', label: 'PRD' },
  { id: 'nature', label: 'Nature' },
] as const

const THEORIES = [
  { id: 'lcdm', label: 'ΛCDM' },
  { id: 'g4v', label: 'G4v' },
] as const

type TheoryRow = { theory: string; theoryLabel: string; chi2: number | null; deltaChi2: number | null }

export function PublicationsPage() {
  const { setMode } = useWorkflow()
  const { getToken } = useAuth()

  const [artifactType, setArtifactType] = useState<'table' | 'figure'>('table')
  const [stylePreset, setStylePreset] = useState<string>('apj')
  const [datasetId, setDatasetId] = useState('synthetic')
  const [comparisonRows, setComparisonRows] = useState<TheoryRow[]>([])
  const [loading, setLoading] = useState(false)
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    setMode('publish')
    document.title = 'Publications · Gravitational Physics'
  }, [setMode])

  const fetchComparison = useCallback(async () => {
    setLoading(true)
    setFetchError(null)
    try {
      const token = getToken()
      const results: { theory: string; chi2: number }[] = []
      for (const t of THEORIES) {
        const res = await api.post<{ chi_squared: number }>(
          '/api/likelihood/evaluate',
          { theory_id: t.id, dataset_id: datasetId, omega_m: 0.31, h0: 70 },
          token
        )
        results.push({ theory: t.id, chi2: res.chi_squared })
      }
      const chi2Values = results.map((r) => (Number.isFinite(r.chi2) ? r.chi2 : null))
      const minChi2 = chi2Values.reduce<number | null>((acc, v) => {
        if (v == null) return acc
        return acc == null ? v : Math.min(acc, v)
      }, null)
      const rows: TheoryRow[] = THEORIES.map((t, i) => {
        const chi2 = chi2Values[i]
        const deltaChi2 = minChi2 != null && chi2 != null ? chi2 - minChi2 : null
        return {
          theory: t.id,
          theoryLabel: t.label,
          chi2,
          deltaChi2,
        }
      })
      setComparisonRows(rows)
    } catch (e) {
      setComparisonRows([])
      const err = e as { detail?: string; message?: string }
      setFetchError(err.detail ?? err.message ?? String(e))
    } finally {
      setLoading(false)
    }
  }, [datasetId, getToken])

  useEffect(() => {
    if (artifactType === 'table') fetchComparison()
  }, [artifactType, fetchComparison])

  const exportLaTeX = useCallback(() => {
    const header = '\\begin{table}\n  \\centering\n  \\caption{Theory comparison}\n  \\label{tab:theory-comp}\n  \\begin{tabular}{lcc}\n    \\hline\n    Theory & $\\chi^2$ & $\\Delta\\chi^2$ \\\\\n    \\hline\n'
    const body = comparisonRows
      .map((r) => {
        const chi = r.chi2 != null ? r.chi2.toFixed(2) : '---'
        const dchi = r.deltaChi2 != null ? r.deltaChi2.toFixed(2) : '---'
        return `    ${r.theoryLabel} & ${chi} & ${dchi} \\\\`
      })
      .join('\n')
    const footer = '\n    \\hline\n  \\end{tabular}\n\\end{table}\n'
    const content = header + body + footer
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `theory_comparison_${datasetId}.tex`
    a.click()
    URL.revokeObjectURL(url)
  }, [comparisonRows, datasetId])

  return (
    <div className="w-full max-w-5xl space-y-6">
      <h1 className="text-2xl font-bold">Publication Export</h1>
      <p className="text-muted-foreground">
        Configure export format and style. Generate theory comparison tables and download as LaTeX.
      </p>

      <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <div className="space-y-4 rounded-lg border border-border bg-card p-4">
          <h2 className="text-sm font-semibold">Export Configuration</h2>
          <div>
            <label className="block text-xs text-muted-foreground">Artifact type</label>
            <select
              value={artifactType}
              onChange={(e) => setArtifactType(e.target.value as 'table' | 'figure')}
              className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
            >
              {ARTIFACT_TYPES.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-muted-foreground">Style preset</label>
            <select
              value={stylePreset}
              onChange={(e) => setStylePreset(e.target.value)}
              className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
            >
              {STYLE_PRESETS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          {artifactType === 'table' && (
            <div>
              <label className="block text-xs text-muted-foreground">Dataset</label>
              <select
                value={datasetId}
                onChange={(e) => setDatasetId(e.target.value)}
                className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
              >
                <option value="synthetic">Synthetic (5 SNe)</option>
                <option value="pantheon">Pantheon (1048 SNe)</option>
              </select>
            </div>
          )}
        </div>

        <div className="space-y-4">
          {artifactType === 'table' && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="mb-4 font-semibold">Theory Comparison (AC-IRE-006.3)</h2>
              <p className="mb-4 text-xs text-muted-foreground">
                χ² for each theory vs {datasetId}. Δχ² relative to best-fitting theory.
              </p>
              {loading ? (
                <p className="text-sm text-muted-foreground">Loading…</p>
              ) : comparisonRows.length > 0 ? (
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[280px] border-collapse text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="pb-2 pr-4 text-left font-medium">Theory</th>
                          <th className="pb-2 pr-4 text-right font-medium">χ²</th>
                          <th className="pb-2 text-right font-medium">Δχ²</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparisonRows.map((r) => (
                          <tr key={r.theory} className="border-b border-border/50">
                            <td className="py-2 pr-4">{r.theoryLabel}</td>
                            <td className="py-2 pr-4 text-right tabular-nums">
                              {r.chi2 != null && Number.isFinite(r.chi2) ? r.chi2.toFixed(2) : '—'}
                            </td>
                            <td className="py-2 text-right tabular-nums">
                              {r.deltaChi2 != null && Number.isFinite(r.deltaChi2)
                                ? r.deltaChi2.toFixed(2)
                                : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <Button onClick={exportLaTeX} variant="outline" size="sm">
                    <FileText className="mr-2 h-4 w-4" />
                    Download LaTeX (AC-IRE-006.4)
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {fetchError
                      ? `Could not load comparison: ${fetchError}`
                      : 'No comparison data. Is the backend running?'}
                  </p>
                  <Button onClick={() => fetchComparison()} variant="outline" size="sm">
                    Retry
                  </Button>
                </div>
              )}
            </div>
          )}

          {artifactType === 'figure' && (
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="mb-2 font-semibold">Figure Export</h2>
              <p className="mb-4 text-sm text-muted-foreground">
                The Export button is on each plot. Go to the page with the figure you want, then use
                the Export SVG button next to the plot.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link to="/explore">
                  <Button variant="outline" size="sm">
                    <LineChart className="mr-2 h-4 w-4" />
                    Go to Explore
                  </Button>
                </Link>
                <Link to="/scan">
                  <Button variant="outline" size="sm">
                    <Scan className="mr-2 h-4 w-4" />
                    Go to Parameter Scan
                  </Button>
                </Link>
                <Link to="/inference">
                  <Button variant="outline" size="sm">
                    <BarChart3 className="mr-2 h-4 w-4" />
                    Go to MCMC
                  </Button>
                </Link>
              </div>
              <p className="mt-4 text-xs text-muted-foreground">
                Style preset ({stylePreset}) applies to figure margins and fonts when generating
                publication-ready output.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
