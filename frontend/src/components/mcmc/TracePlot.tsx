/**
 * WO-37: Trace plot - sample index vs value per parameter.
 * AC-IRE-006.4: Export SVG for publication.
 */

import { useRef, useCallback } from 'react'
import { Download } from 'lucide-react'

function flatten<T>(arr: T[] | T[][]): T[] {
  if (!arr.length) return []
  return Array.isArray(arr[0]) ? (arr as T[][]).flat() : (arr as T[])
}

function formatTick(v: number): string {
  if (Math.abs(v) >= 1000 || (Math.abs(v) < 0.01 && v !== 0)) return v.toExponential(1)
  return v.toFixed(2)
}

export function TracePlot({
  samples,
  paramNames,
}: {
  samples: Record<string, number[] | number[][]>
  paramNames: string[]
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const exportSvg = useCallback(() => {
    const el = containerRef.current?.querySelector('svg')
    if (!el) return
    const s = new XMLSerializer().serializeToString(el)
    const blob = new Blob([s], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'trace_plot.svg'
    a.click()
    URL.revokeObjectURL(url)
  }, [])

  const names = paramNames.length ? paramNames : Object.keys(samples)
  if (!names.length) return null

  const padLeft = 55
  const padRight = 20
  const padTop = 20
  const padBottom = 28
  const w = 450
  const hPerTrace = 120
  const h = names.length * hPerTrace + padTop + padBottom

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
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full min-w-[300px]" preserveAspectRatio="xMidYMid meet">
        {names.map((name, idx) => {
          const raw = samples[name]
          if (!raw) return null
          const vals = flatten(raw) as number[]
          const vMin = Math.min(...vals.filter(Number.isFinite))
          const vMax = Math.max(...vals.filter(Number.isFinite))
          const vRange = vMax - vMin || 1
          const y0 = padTop + idx * hPerTrace + 20
          const traceH = hPerTrace - 35
          const plotW = w - padLeft - padRight
          const pts = vals
            .map((v, i) => {
              const x = padLeft + (i / Math.max(1, vals.length - 1)) * plotW
              const y = y0 + traceH - ((v - vMin) / vRange) * traceH
              return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
            })
            .join(' ')
          const n = vals.length
          return (
            <g key={name}>
              <text x={12} y={y0 + traceH / 2} className="fill-muted-foreground" style={{ fontSize: 10 }} textAnchor="end">
                {name}
              </text>
              <path d={pts} fill="none" stroke="var(--chart-1)" strokeWidth="1" opacity={0.8} />
              <line x1={padLeft} y1={y0} x2={padLeft} y2={y0 + traceH} stroke="currentColor" strokeWidth="0.5" opacity={0.4} />
              <line x1={padLeft} y1={y0 + traceH} x2={w - padRight} y2={y0 + traceH} stroke="currentColor" strokeWidth="0.5" opacity={0.4} />
              {/* Y-axis ticks */}
              <text x={padLeft - 4} y={y0 + traceH + 3} className="fill-muted-foreground" style={{ fontSize: 9 }} textAnchor="end">{formatTick(vMin)}</text>
              <text x={padLeft - 4} y={y0 - 2} className="fill-muted-foreground" style={{ fontSize: 9 }} textAnchor="end">{formatTick(vMax)}</text>
              {/* X-axis ticks (bottom trace only) */}
              {idx === names.length - 1 && (
                <>
                  <text x={padLeft} y={h - 6} className="fill-muted-foreground" style={{ fontSize: 9 }} textAnchor="start">0</text>
                  <text x={padLeft + plotW / 2} y={h - 6} className="fill-muted-foreground" style={{ fontSize: 9 }} textAnchor="middle">{Math.floor(n / 2)}</text>
                  <text x={w - padRight} y={h - 6} className="fill-muted-foreground" style={{ fontSize: 9 }} textAnchor="end">{n}</text>
                </>
              )}
            </g>
          )
        })}
        {/* X-axis label (only for first subplot area) */}
        <text x={w / 2} y={h - 2} className="fill-muted-foreground" style={{ fontSize: 10 }} textAnchor="middle">Iteration</text>
      </svg>
      </div>
    </div>
  )
}
