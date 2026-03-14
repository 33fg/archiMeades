import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Bot, FileText, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useLayout } from '@/contexts/LayoutContext'
import { useSelection } from '@/contexts/SelectionContext'
import { useApiQuery } from '@/hooks/useApi'
import { SettingsModal } from '@/components/SettingsModal'
import { ExploreParameterControls } from '@/components/explore/ExploreParameterControls'
import { MCMCConfigControls } from '@/components/mcmc/MCMCConfigControls'
import { NBodyConfigControls } from '@/components/nbody/NBodyConfigControls'
import { ScanGridControls } from '@/components/scan/ScanGridControls'

function DetailsPanelContent() {
  const { theoryId, observationIds } = useSelection()
  const { data: theory } = useApiQuery<{ id: string; name: string; identifier?: string }>(
    ['theories', 'detail', theoryId ?? ''],
    `/api/theories/${theoryId}`,
    { enabled: !!theoryId }
  )
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">Details</p>
      <div className="space-y-2 rounded-md border border-border bg-background p-3 text-sm">
        {theory ? (
          <>
            <p className="font-medium">{theory.name || theory.identifier || 'Theory'}</p>
            <p className="text-xs text-muted-foreground">ID: {theory.id.slice(0, 8)}…</p>
          </>
        ) : observationIds.length > 0 ? (
          <p>{observationIds.length} dataset(s) selected</p>
        ) : (
          <p className="text-muted-foreground">Select a theory or dataset to view details.</p>
        )}
      </div>
    </div>
  )
}

export function RightSidebar() {
  const location = useLocation()
  const { rightPanelMode, setRightPanelMode } = useLayout()
  const [settingsOpen, setSettingsOpen] = useState(false)
  const isExplore = location.pathname === '/explore'
  const isNbody = location.pathname === '/nbody'
  const isScan = location.pathname === '/scan'
  const isInference = location.pathname === '/inference'

  return (
    <aside className="right-sidebar min-w-0 flex-1 border-l border-border bg-sidebar py-4">
      <div className="space-y-4 px-3">
        {isExplore && (
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Parameters
            </p>
            <ExploreParameterControls />
          </div>
        )}
        {isNbody && (
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              N-body Config
            </p>
            <NBodyConfigControls />
          </div>
        )}
        {isScan && (
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Grid Config
            </p>
            <ScanGridControls />
          </div>
        )}
        {isInference && (
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              MCMC Config
            </p>
            <MCMCConfigControls />
          </div>
        )}
        <div className="flex items-center justify-between gap-1">
          <div className="flex rounded-md border border-border p-0.5" role="tablist">
            <Button
              variant={rightPanelMode === 'ai' ? 'secondary' : 'ghost'}
              size="sm"
              className="flex-1 gap-1.5 px-2 text-xs"
              onClick={() => setRightPanelMode('ai')}
            >
              <Bot className="h-3.5 w-3.5" />
              AI
            </Button>
            <Button
              variant={rightPanelMode === 'details' ? 'secondary' : 'ghost'}
              size="sm"
              className="flex-1 gap-1.5 px-2 text-xs"
              onClick={() => setRightPanelMode('details')}
            >
              <FileText className="h-3.5 w-3.5" />
              Details
            </Button>
          </div>
        </div>
        {rightPanelMode === 'ai' && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">AI Assistant</p>
            <div className="rounded-md border border-border bg-background p-3 text-sm">
              <p className="text-muted-foreground">
                Contextual help and suggestions. WebSocket chat interface (placeholder).
              </p>
            </div>
          </div>
        )}
        {rightPanelMode === 'details' && (
          <DetailsPanelContent />
        )}
        <Button
          variant="outline"
          size="sm"
          className="w-full justify-start gap-2"
          onClick={() => setSettingsOpen(true)}
        >
          <Settings className="h-4 w-4" />
          Settings
        </Button>
      </div>
      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </aside>
  )
}
