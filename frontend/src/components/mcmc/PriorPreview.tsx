/**
 * WO-37: Prior distribution preview plots - visualize uniform/normal priors before MCMC.
 */

type PriorSpec = { type: string; low?: number; high?: number; mean?: number; std?: number }

function UniformPreview({ low, high }: { low: number; high: number }) {
  const pad = 4
  const w = 120
  const h = 36
  const xMin = Math.min(low, high)
  const xMax = Math.max(low, high)
  const range = xMax - xMin || 1
  const x1 = pad + ((low - xMin) / range) * (w - 2 * pad)
  const x2 = pad + ((high - xMin) / range) * (w - 2 * pad)
  const rectX = Math.min(x1, x2)
  const rectW = Math.abs(x2 - x1) || 1
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-9 w-30 min-w-[120px]" preserveAspectRatio="none">
      <rect x={pad} y={pad} width={w - 2 * pad} height={h - 2 * pad} fill="var(--muted)" rx={2} />
      <rect x={rectX} y={pad} width={rectW} height={h - 2 * pad} fill="var(--chart-1)" opacity={0.7} rx={1} />
    </svg>
  )
}

function NormalPreview({ mean, std }: { mean: number; std: number }) {
  const pad = 4
  const w = 120
  const h = 36
  const s = Math.max(std * 0.5, 0.01)
  const xMin = mean - 3 * s
  const xMax = mean + 3 * s
  const range = xMax - xMin || 1
  const pts: string[] = []
  for (let i = 0; i <= 40; i++) {
    const x = xMin + (i / 40) * range
    const g = Math.exp(-0.5 * ((x - mean) / s) ** 2)
    const px = pad + ((x - xMin) / range) * (w - 2 * pad)
    const py = h - pad - (g / 1) * (h - 2 * pad)
    pts.push(`${i === 0 ? 'M' : 'L'} ${px} ${py}`)
  }
  pts.push(`L ${w - pad} ${h - pad} L ${pad} ${h - pad} Z`)
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-9 w-30 min-w-[120px]" preserveAspectRatio="none">
      <path d={pts.join(' ')} fill="var(--chart-1)" opacity={0.5} />
      <path d={pts.slice(0, -3).join(' ')} fill="none" stroke="var(--chart-1)" strokeWidth="1.5" />
    </svg>
  )
}

export function PriorPreview({ priorSpec }: { priorSpec: Record<string, PriorSpec> }) {
  const entries = Object.entries(priorSpec)
  if (!entries.length) return null
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-muted-foreground">Prior preview</p>
      <div className="flex flex-wrap gap-4">
        {entries.map(([name, spec]) => (
          <div key={name} className="flex flex-col gap-0.5">
            <span className="text-xs text-muted-foreground">{name}</span>
            {spec.type === 'uniform' && typeof spec.low === 'number' && typeof spec.high === 'number' ? (
              <UniformPreview low={spec.low} high={spec.high} />
            ) : spec.type === 'normal' && typeof spec.mean === 'number' && typeof spec.std === 'number' ? (
              <NormalPreview mean={spec.mean} std={spec.std} />
            ) : (
              <div className="h-9 w-[120px] rounded bg-muted/50 flex items-center justify-center text-xs text-muted-foreground">
                —
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
