/**
 * WO-42: Theory Exploration Mode - interactive Hubble diagram, residuals, chi-squared.
 * AC-IRE-002: Parameter sliders in left sidebar (ExploreContext)
 * AC-IRE-003: Distance modulus plot with data + theory curve
 * AC-IRE-004: Residual plot synchronized with main plot
 */

import { useCallback, useEffect, useMemo, useRef } from 'react'
import { Download } from 'lucide-react'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { useExplore } from '@/contexts/ExploreContext'

/** SVG scatter + line chart for Hubble diagram and residuals. */
function SimpleChart({
  dataPoints,
  theoryLine,
  residuals,
  height = 280,
  yTitle,
}: {
  dataPoints: { x: number; y: number; err?: number }[]
  theoryLine?: { x: number[]; y: number[] }
  residuals?: boolean
  height?: number
  yTitle: string
}) {
  const pad = { left: 50, right: 20, top: 20, bottom: 40 }
  const w = 500
  const h = height

  const allX = useMemo(() => {
    const xs = dataPoints.map((p) => p.x)
    if (theoryLine?.x?.length) xs.push(...theoryLine.x)
    return xs
  }, [dataPoints, theoryLine])
  const allY = useMemo(() => {
    const ys = dataPoints.map((p) => p.y)
    if (theoryLine?.y?.length) ys.push(...theoryLine.y)
    return ys
  }, [dataPoints, theoryLine])

  const xMin = allX.length ? Math.min(...allX) : 0
  const xMax = allX.length ? Math.max(...allX) : 1
  const yMin = allY.length ? Math.min(...allY) : 0
  const yMax = allY.length ? Math.max(...allY) : 1
  const xRange = xMax - xMin || 1
  const yRange = yMax - yMin || 1
  const xPad = xRange * 0.05
  const yPad = yRange * 0.08

  const sx = (v: number) => pad.left + ((v - xMin + xPad) / (xRange + 2 * xPad)) * (w - pad.left - pad.right)
  const sy = (v: number) => h - pad.bottom - ((v - yMin + yPad) / (yRange + 2 * yPad)) * (h - pad.top - pad.bottom)

  const theoryPath =
    theoryLine && theoryLine.x.length > 0
      ? theoryLine.x
          .map((xi, i) => (theoryLine.y[i] != null && Number.isFinite(theoryLine.y[i]) ? { x: xi, y: theoryLine.y[i]! } : null))
          .filter((p): p is { x: number; y: number } => p != null)
          .sort((a, b) => a.x - b.x)
          .map((p, i) => `${i === 0 ? 'M' : 'L'} ${sx(p.x)} ${sy(p.y)}`)
          .join(' ')
      : ''

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full max-w-2xl" preserveAspectRatio="xMidYMid meet">
      <line x1={pad.left} y1={h - pad.bottom} x2={w - pad.right} y2={h - pad.bottom} stroke="currentColor" strokeWidth="1" opacity={0.3} />
      <line x1={pad.left} y1={pad.top} x2={pad.left} y2={h - pad.bottom} stroke="currentColor" strokeWidth="1" opacity={0.3} />
      <text x={w / 2} y={h - 8} textAnchor="middle" className="fill-muted-foreground text-[10px]">
        Redshift z
      </text>
      <text x={14} y={h / 2} textAnchor="middle" transform={`rotate(-90, 14, ${h / 2})`} className="fill-muted-foreground text-[10px]">
        {yTitle}
      </text>
      {dataPoints.map((p, i) =>
        Number.isFinite(p.x) && Number.isFinite(p.y) ? (
          <g key={i}>
            {p.err != null && p.err > 0 && (
              <line
                x1={sx(p.x)}
                y1={sy(p.y)}
                x2={sx(p.x)}
                y2={sy(p.y + p.err)}
                stroke="#6366f1"
                strokeWidth="1"
                opacity={0.6}
              />
            )}
            <circle cx={sx(p.x)} cy={sy(p.y)} r="4" fill="#6366f1" />
          </g>
        ) : null
      )}
      {theoryPath && (
        <path d={theoryPath} fill="none" stroke="#22c55e" strokeWidth="2" strokeLinejoin="round" />
      )}
      {residuals && (
        <line
          x1={pad.left}
          y1={sy(0)}
          x2={w - pad.right}
          y2={sy(0)}
          stroke="#94a3b8"
          strokeWidth="1"
          strokeDasharray="4 2"
          opacity={0.6}
        />
      )}
    </svg>
  )
}

export function ExplorePage() {
  const { setMode } = useWorkflow()
  const {
    datasetId,
    datasetData,
    loadingData,
    theoryCurve,
  } = useExplore()
  const hubblePlotRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setMode('explore')
    document.title = 'Explore · Gravitational Physics'
  }, [setMode])

  const exportHubbleSvg = useCallback(() => {
    const el = hubblePlotRef.current?.querySelector('svg')
    if (!el) return
    const s = new XMLSerializer().serializeToString(el)
    const blob = new Blob([s], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `hubble_diagram_${datasetId}.svg`
    a.click()
    URL.revokeObjectURL(url)
  }, [datasetId])

  const residuals = useMemo(() => {
    if (!datasetData || !theoryCurve) return null
    const obs = datasetData.observable
    const pred = theoryCurve.mu
    if (obs.length !== pred.length) return null
    return obs.map((o, i) => o - pred[i])
  }, [datasetData, theoryCurve])

  const dataPoints = useMemo(() => {
    if (!datasetData) return []
    return datasetData.redshift.map((x, i) => ({
      x,
      y: datasetData.observable[i] ?? NaN,
      err: datasetData.stat_unc[i],
    }))
  }, [datasetData])

  const theoryLine = useMemo(() => {
    if (!theoryCurve) return undefined
    const valid = theoryCurve.z
      .map((z, i) => (Number.isFinite(theoryCurve.mu[i]) ? { x: z, y: theoryCurve.mu[i]! } : null))
      .filter((p): p is { x: number; y: number } => p != null)
    return valid.length ? { x: valid.map((p) => p.x), y: valid.map((p) => p.y) } : undefined
  }, [theoryCurve])

  const residualPoints = useMemo(() => {
    if (!datasetData || !residuals) return []
    return datasetData.redshift.map((x, i) => ({ x, y: residuals[i] ?? NaN, err: undefined }))
  }, [datasetData, residuals])

  return (
    <div className="w-full max-w-5xl space-y-6">
      <h1 className="text-2xl font-bold">Exploration View</h1>
      <p className="text-muted-foreground">
        Interactive Hubble diagram with theory predictions overlaying observational data.
        Adjust parameters in the right sidebar to explore the fit.
      </p>

      <div className="space-y-4">
          <div className="rounded-lg border border-border bg-card p-2">
            <div className="mb-2 flex items-center justify-between px-2">
              <p className="text-xs font-medium text-muted-foreground">
                Distance modulus μ vs redshift
              </p>
              {dataPoints.length > 0 && !loadingData && (
                <button
                  type="button"
                  onClick={exportHubbleSvg}
                  className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-primary hover:bg-muted"
                >
                  <Download className="h-3 w-3" />
                  Export SVG
                </button>
              )}
            </div>
            {loadingData ? (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                Loading data…
              </div>
            ) : dataPoints.length > 0 ? (
              <div ref={hubblePlotRef}>
                <SimpleChart
                  dataPoints={dataPoints}
                  theoryLine={theoryLine}
                  height={320}
                  yTitle="μ (mag)"
                />
              </div>
            ) : (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                Select a dataset
              </div>
            )}
          </div>

          <div className="rounded-lg border border-border bg-card p-2">
            <p className="mb-2 px-2 text-xs font-medium text-muted-foreground">
              Residuals (data − theory)
            </p>
            {residualPoints.length > 0 ? (
              <SimpleChart
                dataPoints={residualPoints}
                residuals
                height={200}
                yTitle="Δμ (mag)"
              />
            ) : (
              <div className="flex h-48 items-center justify-center text-muted-foreground">
                —
              </div>
            )}
          </div>
        </div>
    </div>
  )
}
