/**
 * WO-37: Triangle (corner) plot - 2D scatter between parameter pairs.
 * AC-IRE-006.4: Export SVG for publication.
 */

import { useRef, useCallback } from 'react'
import { Download } from 'lucide-react'

function flatten<T>(arr: T[] | T[][]): T[] {
  if (!arr.length) return []
  return Array.isArray(arr[0]) ? (arr as T[][]).flat() : (arr as T[])
}

export function TrianglePlot({
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
    a.download = 'triangle_plot.svg'
    a.click()
    URL.revokeObjectURL(url)
  }, [])

  const names = paramNames.length ? paramNames : Object.keys(samples)
  if (names.length < 2) return <p className="text-sm text-muted-foreground">Need ≥2 parameters for triangle plot.</p>

  const pairs: [string, string][] = []
  for (let i = 0; i < names.length; i++) {
    for (let j = i + 1; j < names.length; j++) pairs.push([names[i], names[j]])
  }
  if (!pairs.length) return null

  const cellSize = 140
  const cols = Math.min(2, pairs.length)
  const rows = Math.ceil(pairs.length / cols)
  const pad = 50
  const w = cols * cellSize + pad * 2
  const h = rows * cellSize + pad * 2

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
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full min-w-[250px]" preserveAspectRatio="xMidYMid meet">
        {pairs.map(([xName, yName], idx) => {
          const col = idx % cols
          const row = Math.floor(idx / cols)
          const x0 = pad + col * cellSize + 10
          const y0 = pad + row * cellSize + 10
          const size = cellSize - 20
          const xRaw = samples[xName]
          const yRaw = samples[yName]
          if (!xRaw || !yRaw) return null
          const xVals = flatten(xRaw) as number[]
          const yVals = flatten(yRaw) as number[]
          const n = Math.min(xVals.length, yVals.length)
          const xMin = Math.min(...xVals.slice(0, n).filter(Number.isFinite))
          const xMax = Math.max(...xVals.slice(0, n).filter(Number.isFinite))
          const yMin = Math.min(...yVals.slice(0, n).filter(Number.isFinite))
          const yMax = Math.max(...yVals.slice(0, n).filter(Number.isFinite))
          const xR = xMax - xMin || 1
          const yR = yMax - yMin || 1
          const pts = []
          for (let i = 0; i < n; i++) {
            const x = x0 + ((xVals[i] - xMin) / xR) * size
            const y = y0 + size - ((yVals[i] - yMin) / yR) * size
            if (Number.isFinite(x) && Number.isFinite(y)) pts.push([x, y])
          }
          return (
            <g key={`${xName}-${yName}`}>
              <text x={x0 + size / 2} y={y0 - 5} textAnchor="middle" className="fill-muted-foreground" style={{ fontSize: 10 }}>
                {yName} vs {xName}
              </text>
              <rect x={x0} y={y0} width={size} height={size} fill="var(--background)" stroke="currentColor" strokeWidth="0.5" opacity={0.5} />
              {pts.map(([px, py], i) => (
                <circle key={i} cx={px} cy={py} r={1.5} fill="var(--chart-1)" opacity={0.5} />
              ))}
            </g>
          )
        })}
      </svg>
      </div>
    </div>
  )
}
