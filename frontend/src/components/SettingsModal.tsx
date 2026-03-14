import { useEffect, useState } from 'react'
import { Moon, Sun, X } from 'lucide-react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/button'
import { useApiQuery } from '@/hooks/useApi'
import { useTheme } from '@/contexts/ThemeContext'
import { useProvenanceSettings } from '@/contexts/ProvenanceSettingsContext'

type SettingsTab = 'theme' | 'provenance' | 'system' | 'dgx'

type HealthResponse = {
  status: string
  service: string
  database: string
  redis: string
  s3: string
  neo4j: string
  dgx: string
  dgx_cluster_size?: number
  dgx_error?: string
}

type WorkersHealthResponse = {
  status: string
  workers: string[]
}

function StatusRow({ label, status }: { label: string; status: string }) {
  const ok = status === 'ok'
  const labels: Record<string, string> = {
    ok: 'Connected',
    unavailable: 'Unavailable',
    disabled: 'Disabled',
    at_capacity: 'At capacity',
  }
  const display = labels[status] ?? (ok ? 'Connected' : 'Unavailable')
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className={ok ? 'text-green-600 font-medium' : 'text-amber-600'}>
        {display}
      </span>
    </div>
  )
}

const TABS: { id: SettingsTab; label: string }[] = [
  { id: 'theme', label: 'Theme' },
  { id: 'provenance', label: 'Provenance' },
  { id: 'system', label: 'System Status' },
  { id: 'dgx', label: 'DGX Cluster' },
]

export function SettingsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('theme')
  const { theme, setTheme } = useTheme()
  const { settings: provSettings, update: updateProvSettings } = useProvenanceSettings()
  const { data: health, isLoading } = useApiQuery<HealthResponse>(
    ['health', 'settings'],
    '/health',
    { retry: false, enabled: open }
  )
  const { data: workersHealth } = useApiQuery<WorkersHealthResponse>(
    ['workers-health', 'settings'],
    '/api/jobs/workers/health',
    { retry: false, enabled: open }
  )

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
    >
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div className="relative z-10 w-full max-w-md rounded-lg border border-border bg-card shadow-xl overflow-hidden">
        <div className="flex items-center justify-between gap-4 border-b border-border px-4 py-3">
          <h2 id="settings-title" className="text-lg font-semibold">
            Settings
          </h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div
          className="flex border-b border-border px-2"
          role="tablist"
          aria-label="Settings categories"
        >
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              role="tab"
              aria-selected={activeTab === id}
              aria-controls={`settings-panel-${id}`}
              id={`settings-tab-${id}`}
              onClick={() => setActiveTab(id)}
              className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
                activeTab === id
                  ? 'border-primary text-foreground'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="p-4 max-h-[60vh] overflow-y-auto">
          {activeTab === 'theme' && (
            <section
              id="settings-panel-theme"
              role="tabpanel"
              aria-labelledby="settings-tab-theme"
              className="space-y-4"
            >
              <h3 className="text-sm font-medium text-foreground">Theme</h3>
              <div className="flex gap-2">
                <Button
                  variant={theme === 'light' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setTheme('light')}
                >
                  <Sun className="h-4 w-4 mr-1" />
                  Light
                </Button>
                <Button
                  variant={theme === 'dark' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setTheme('dark')}
                >
                  <Moon className="h-4 w-4 mr-1" />
                  Dark
                </Button>
                <Button
                  variant={theme === 'system' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setTheme('system')}
                >
                  System
                </Button>
              </div>
            </section>
          )}

          {activeTab === 'provenance' && (
            <section
              id="settings-panel-provenance"
              role="tabpanel"
              aria-labelledby="settings-tab-provenance"
              className="space-y-4"
            >
              <h3 className="text-sm font-medium text-foreground">Provenance (WO-47)</h3>
              <div className="space-y-2 rounded-md border border-border bg-muted/30 p-4">
                <label className="flex items-center justify-between gap-4 cursor-pointer">
                  <span className="text-sm text-muted-foreground">Show export button</span>
                  <input
                    type="checkbox"
                    checked={provSettings.showExportButton}
                    onChange={(e) => updateProvSettings({ showExportButton: e.target.checked })}
                    className="rounded border-input"
                  />
                </label>
                <label className="flex items-center justify-between gap-4 cursor-pointer">
                  <span className="text-sm text-muted-foreground">Verification (Neo4j status)</span>
                  <input
                    type="checkbox"
                    checked={provSettings.verificationEnabled}
                    onChange={(e) => updateProvSettings({ verificationEnabled: e.target.checked })}
                    className="rounded border-input"
                  />
                </label>
              </div>
            </section>
          )}

          {activeTab === 'system' && (
            <section
              id="settings-panel-system"
              role="tabpanel"
              aria-labelledby="settings-tab-system"
              className="space-y-4"
            >
              <h3 className="text-sm font-medium text-foreground">System Status</h3>
              {isLoading ? (
                <p className="text-sm text-muted-foreground">Checking…</p>
              ) : health ? (
                <div className="space-y-0 rounded-md border border-border bg-muted/30 p-4">
                  <StatusRow label="API" status={health.status === 'unhealthy' ? 'unavailable' : 'ok'} />
                  <StatusRow label="Database" status={health.database} />
                  <StatusRow label="Redis" status={health.redis} />
                  <StatusRow label="Neo4j" status={health.neo4j} />
                  <StatusRow label="S3" status={health.s3} />
                  <StatusRow
                    label={`DGX Cluster (${Math.max(1, health.dgx_cluster_size ?? 1)})`}
                    status={health.dgx ?? 'unavailable'}
                  />
                  <StatusRow
                    label="Celery Workers"
                    status={workersHealth?.status === 'ok' ? 'ok' : 'unavailable'}
                  />
                  {workersHealth?.workers && workersHealth.workers.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border text-xs text-muted-foreground">
                      Workers: {workersHealth.workers.join(', ')}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Unable to fetch status</p>
              )}
            </section>
          )}

          {activeTab === 'dgx' && (
            <section
              id="settings-panel-dgx"
              role="tabpanel"
              aria-labelledby="settings-tab-dgx"
              className="space-y-4"
            >
              <h3 className="text-sm font-medium text-foreground">DGX Cluster</h3>
              {health ? (
                <div className="space-y-2 rounded-md border border-border bg-muted/30 p-4">
                  <StatusRow label="Status" status={health.dgx ?? 'unavailable'} />
                  <div className="flex items-center justify-between gap-4 py-1.5 text-sm">
                    <span className="text-muted-foreground">Cluster size</span>
                    <span className="font-medium">
                      {health.dgx === 'disabled'
                        ? 'Not connected'
                        : `${Math.max(1, health.dgx_cluster_size ?? 1)} ${(health.dgx_cluster_size ?? 1) === 1 ? 'node' : 'nodes'}`}
                    </span>
                  </div>
                  {health.dgx === 'unavailable' && health.dgx_error && (
                    <p className="mt-2 text-xs text-amber-600 dark:text-amber-500">
                      {health.dgx_error}
                    </p>
                  )}
                  <p className="mt-3 pt-3 border-t border-border text-xs text-muted-foreground">
                    Run <code className="rounded bg-muted px-1 text-[10px]">./scripts/deploy-dgx-heartbeat.sh --no-pip</code> (no pip on DGX) or <code className="rounded bg-muted px-1 text-[10px]">./scripts/deploy-dgx-heartbeat.sh</code>. See docs/DGX-SETUP.md.
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Unable to fetch DGX status</p>
              )}
            </section>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}
