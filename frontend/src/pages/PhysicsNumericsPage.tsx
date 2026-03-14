/**
 * Physics & Numerics Library — method catalog.
 * WO-51: Layer 1 numerics. WO-52: Layer 2 physics methods.
 */

import { useEffect } from 'react'
import { Calculator, CheckCircle, Clock, Layers } from 'lucide-react'
import { useApiQuery } from '@/hooks/useApi'

type MethodEntry = {
  id: string
  name: string
  formula: string
  complexity?: string
  hardware_target?: string
  precision?: string
  regime?: string
  status: 'implemented' | 'planned'
  module: string
}

export function PhysicsNumericsPage() {
  useEffect(() => {
    document.title = 'Physics & Numerics Library · Gravitational Physics'
  }, [])

  const { data: catalog, isLoading, error } = useApiQuery<MethodEntry[]>(
    ['physics-numerics-catalog'],
    '/api/physics-numerics/catalog'
  )

  return (
    <div className="w-full max-w-4xl space-y-6">
      <div className="flex items-center gap-3">
        <Calculator className="h-8 w-8 text-muted-foreground" />
        <div>
          <h1 className="text-2xl font-bold">Physics & Numerics Library</h1>
          <p className="text-sm text-muted-foreground">
            Reusable numerical methods for gravitational theory evaluation
          </p>
          <div className="mt-2 flex items-center gap-2 rounded-md border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
            <Layers className="h-4 w-4 shrink-0" />
            <span>
              <strong>Layer 1</strong> — Stateless foundation consumed by Simulation Engines (Layer 2)
              and Workflow Orchestrator (Layer 3). GPU-accelerated, pure functional.
            </span>
          </div>
        </div>
      </div>

      {isLoading && (
        <p className="text-sm text-muted-foreground">Loading catalog…</p>
      )}
      {error && (
        <p className="text-sm text-destructive">
          Failed to load catalog: {error.detail}
        </p>
      )}
      {catalog && catalog.length > 0 && (
        <div className="rounded-lg border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Method</th>
                <th className="px-4 py-3 text-left font-medium">Formula</th>
                <th className="px-4 py-3 text-left font-medium">Complexity</th>
                <th className="px-4 py-3 text-left font-medium">Hardware</th>
                <th className="px-4 py-3 text-left font-medium">Precision</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {catalog.map((m) => (
                <tr
                  key={m.id}
                  className="border-b border-border last:border-0 hover:bg-muted/30"
                >
                  <td className="px-4 py-3">
                    <span className="font-medium">{m.name}</span>
                    <span className="ml-1 text-xs text-muted-foreground">
                      ({m.id})
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{m.formula}</td>
                  <td className="px-4 py-3 text-muted-foreground">{m.complexity}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {m.hardware_target}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{m.precision}</td>
                  <td className="px-4 py-3">
                    {m.status === 'implemented' ? (
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        Implemented
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-600">
                        <Clock className="h-4 w-4" />
                        Planned
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* WO-52: Layer 2 Physics Methods */}
      <PhysicsMethodsSection />
    </div>
  )
}

function PhysicsMethodsSection() {
  const { data: catalog, isLoading, error } = useApiQuery<MethodEntry[]>(
    ['physics-methods-catalog'],
    '/api/physics-methods/catalog'
  )
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 rounded-md border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
        <Layers className="h-4 w-4 shrink-0" />
        <span>
          <strong>Layer 2 (WO-52)</strong> — Physics Methods: classical mechanics, relativistic
          extensions. Consumed by WO-69 simulation engine for N-body and retardation.
        </span>
      </div>
      {isLoading && <p className="text-sm text-muted-foreground">Loading physics methods…</p>}
      {error && (
        <p className="text-sm text-destructive">Failed to load physics methods: {error.detail}</p>
      )}
      {catalog && catalog.length > 0 && (
        <div className="rounded-lg border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Method</th>
                <th className="px-4 py-3 text-left font-medium">Formula</th>
                <th className="px-4 py-3 text-left font-medium">Regime</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {catalog.map((m) => (
                <tr key={m.id} className="border-b border-border last:border-0 hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <span className="font-medium">{m.name}</span>
                    <span className="ml-1 text-xs text-muted-foreground">({m.id})</span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{m.formula}</td>
                  <td className="px-4 py-3 text-muted-foreground">{m.regime ?? '—'}</td>
                  <td className="px-4 py-3">
                    {m.status === 'implemented' ? (
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        Implemented
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-600">
                        <Clock className="h-4 w-4" />
                        Planned
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
