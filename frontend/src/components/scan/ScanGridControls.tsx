/**
 * WO-43: Grid configuration controls for Parameter Scan mode.
 * Rendered in left sidebar per IRE blueprint.
 */

import { Plus, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useScan, type AxisConfig } from '@/contexts/ScanContext'

export function ScanGridControls() {
  const {
    theoryId,
    datasetId,
    axes,
    setTheoryId,
    setDatasetId,
    setAxes,
    handleSubmit,
    createScan,
  } = useScan()

  return (
    <div className="space-y-3 px-2">
      <div>
        <label className="block text-xs text-muted-foreground">Theory</label>
        <select
          value={theoryId}
          onChange={(e) => setTheoryId(e.target.value)}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          <option value="lcdm">Lambda-CDM</option>
          <option value="g4v">G4v</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground">Dataset</label>
        <select
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
          className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
        >
          <option value="synthetic">Synthetic</option>
          <option value="pantheon">Pantheon</option>
        </select>
      </div>
      <div>
        <label className="block text-xs text-muted-foreground mb-1">Axes</label>
        <div className="space-y-1.5">
          {axes.map((a, i) => (
            <AxisRow
              key={i}
              axis={a}
              onChange={(next) =>
                setAxes((prev) => [...prev.slice(0, i), next, ...prev.slice(i + 1)])
              }
            />
          ))}
        </div>
      </div>
      <Button
        size="sm"
        className="w-full gap-2"
        onClick={handleSubmit}
        disabled={createScan.isPending}
      >
        {createScan.isPending ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <Plus className="h-3.5 w-3.5" />
        )}
        Run Scan
      </Button>
    </div>
  )
}

function AxisRow({
  axis,
  onChange,
}: {
  axis: AxisConfig
  onChange: (a: AxisConfig) => void
}) {
  return (
    <div className="flex flex-wrap gap-1 text-xs">
      <input
        value={axis.name}
        onChange={(e) => onChange({ ...axis, name: e.target.value })}
        placeholder="param"
        className="w-16 rounded border border-input bg-background px-1.5 py-1"
      />
      <input
        type="number"
        step="any"
        value={axis.min}
        onChange={(e) => onChange({ ...axis, min: +e.target.value })}
        className="w-12 rounded border border-input bg-background px-1.5 py-1"
      />
      <input
        type="number"
        step="any"
        value={axis.max}
        onChange={(e) => onChange({ ...axis, max: +e.target.value })}
        className="w-12 rounded border border-input bg-background px-1.5 py-1"
      />
      <input
        type="number"
        value={axis.n}
        onChange={(e) => onChange({ ...axis, n: +e.target.value || 1 })}
        className="w-10 rounded border border-input bg-background px-1.5 py-1"
      />
      <select
        value={axis.scale}
        onChange={(e) => onChange({ ...axis, scale: e.target.value })}
        className="rounded border border-input bg-background px-1.5 py-1"
      >
        <option value="linear">lin</option>
        <option value="log">log</option>
      </select>
    </div>
  )
}
