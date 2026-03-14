/**
 * WO-33: Likelihood surface visualization - contour/heatmap for 2D scans.
 * AC-IRE-006.4: Export SVG for publication.
 */

import { useRef, useCallback } from 'react'
import { Download } from 'lucide-react'

type SliceData = {
  ndim: number
  x: number[]
  y?: number[]
  chi2: number[] | number[][]
}

function chi2ToColor(chi2: number, min: number, max: number): string {
  if (!Number.isFinite(chi2) || chi2 > 1e10) return '#1a1a2e'
  const t = max > min ? (chi2 - min) / (max - min) : 0
  const r = Math.round(30 + t * 200)
  const g = Math.round(50 + (1 - t) * 150)
  const b = Math.round(100 + (1 - t) * 120)
  return `rgb(${r},${g},${b})`
}

export function LikelihoodContour({ data }: { data: SliceData }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const exportSvg = useCallback(() => {
    const el = containerRef.current?.querySelector('svg')
    if (!el) return
    const s = new XMLSerializer().serializeToString(el)
    const blob = new Blob([s], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'likelihood_contour.svg'
    a.click()
    URL.revokeObjectURL(url)
  }, [])

  if (data.ndim === 1) {
    const x = data.x
    const arr = data.chi2 as number[]
    const valid = arr.filter((v) => Number.isFinite(v) && v < 1e10)
    void (valid.length ? Math.min(...valid) : 0) // cMin
    void (valid.length ? Math.max(...valid) : 1) // cMax
    const pts = x.map((xi, i) => ({ x: xi, y: arr[i] })).filter((p) => Number.isFinite(p.y))
    if (pts.length < 2) return <p className="text-sm text-muted-foreground">Insufficient data</p>
    const xMin = Math.min(...pts.map((p) => p.x))
    const xMax = Math.max(...pts.map((p) => p.x))
    const yMin = Math.min(...pts.map((p) => p.y!))
    const yMax = Math.max(...pts.map((p) => p.y!))
    const pad = 40
    const w = 400
    const h = 200
    const sx = (v: number) => pad + ((v - xMin) / (xMax - xMin || 1)) * (w - 2 * pad)
    const sy = (v: number) => h - pad - ((v - yMin) / (yMax - yMin || 1)) * (h - 2 * pad)
    const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${sx(p.x)} ${sy(p.y!)}`).join(' ')
    return (
      <div className="rounded border border-border bg-muted/30 p-2">
        <div className="mb-2 flex justify-end">
          <button
            type="button"
            onClick={exportSvg}
            className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-primary hover:bg-muted"
          >
            <Download className="h-3 w-3" />
            Export SVG
          </button>
        </div>
        <div ref={containerRef}>
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full max-w-md" preserveAspectRatio="xMidYMid meet">
          <path d={pathD} fill="none" stroke="var(--chart-1)" strokeWidth="2" />
          <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke="currentColor" strokeWidth="1" opacity={0.3} />
          <line x1={pad} y1={pad} x2={pad} y2={h - pad} stroke="currentColor" strokeWidth="1" opacity={0.3} />
        </svg>
        </div>
      </div>
    )
  }

  const grid = data.chi2 as number[][]
  const nx = grid[0]?.length ?? 0
  const ny = grid.length
  const flat = grid.flat()
  const valid = flat.filter((v) => Number.isFinite(v) && v < 1e10)
  const cMin = valid.length ? Math.min(...valid) : 0
  const cMax = valid.length ? Math.max(...valid) : 1

  const cellW = 8
  const cellH = 8
  const w = nx * cellW
  const h = ny * cellH

  return (
    <div className="rounded border border-border bg-muted/30 p-2 overflow-auto">
      <div className="mb-2 flex justify-end">
        <button
          type="button"
          onClick={exportSvg}
          className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-primary hover:bg-muted"
        >
          <Download className="h-3 w-3" />
          Export SVG
        </button>
      </div>
      <div ref={containerRef}>
        <svg viewBox={`0 0 ${w} ${h}`} className="min-w-[200px]" preserveAspectRatio="none">
          {grid.map((row, j) =>
            row.map((val, i) => (
              <rect
                key={`${i}-${j}`}
                x={i * cellW}
                y={j * cellH}
                width={cellW}
                height={cellH}
                fill={chi2ToColor(val, cMin, cMax)}
                stroke="transparent"
              />
            ))
          )}
        </svg>
        <p className="text-xs text-muted-foreground mt-1">
          χ² range: {cMin.toFixed(1)} – {cMax.toFixed(1)}
        </p>
      </div>
    </div>
  )
}
