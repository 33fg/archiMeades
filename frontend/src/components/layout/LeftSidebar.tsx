import {
  BarChart3,
  BookOpen,
  Calculator,
  Database,
  FileOutput,
  LineChart,
  Orbit,
  Scan,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useLayout } from '@/contexts/LayoutContext'
import { useWorkflow } from '@/contexts/WorkflowContext'
import { SimulationsSection } from './SimulationsSection'

const navItems = [
  { icon: BookOpen, label: 'Theories', href: '/theories' },
  { icon: Database, label: 'Observations', href: '/observations' },
  { icon: Calculator, label: 'Library', href: '/library' },
]

const workflowItems = [
  { mode: 'explore' as const, icon: LineChart, label: 'Explore', href: '/explore' },
  { mode: 'nbody' as const, icon: Orbit, label: 'N-body', href: '/nbody' },
  { mode: 'scan' as const, icon: Scan, label: 'Parameter Scan', href: '/scan' },
  { mode: 'mcmc' as const, icon: BarChart3, label: 'MCMC Inference', href: '/inference' },
  { mode: 'publish' as const, icon: FileOutput, label: 'Publish', href: '/publications' },
]

export function LeftSidebar() {
  const location = useLocation()
  const { leftCollapsed } = useLayout()
  const { mode } = useWorkflow()

  return (
    <aside className="left-sidebar flex flex-col gap-4 py-4">
      <nav className="flex flex-col items-stretch gap-1 px-2">
        <Link
          to="/"
          className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent ${
            location.pathname === '/' ? 'bg-sidebar-accent' : ''
          } ${leftCollapsed ? 'justify-center px-2' : ''}`}
          title="Dashboard"
        >
          <BookOpen className="h-4 w-4 shrink-0" />
          {!leftCollapsed && <span>Dashboard</span>}
        </Link>
        {navItems.map(({ icon: Icon, label, href }) => (
          <Link
            key={href}
            to={href}
            className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent ${
              location.pathname.startsWith(href) ? 'bg-sidebar-accent' : ''
            } ${leftCollapsed ? 'justify-center px-2' : ''}`}
            title={label}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {!leftCollapsed && <span>{label}</span>}
          </Link>
        ))}
      </nav>
      {!leftCollapsed && (
        <>
          <div className="border-t border-sidebar-border px-2 pt-2">
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Workflow
            </p>
            <nav className="flex flex-col gap-1">
              {workflowItems.map(({ mode: m, icon: Icon, label, href }) => (
                <Link
                  key={href}
                  to={href}
                  className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent ${
                    location.pathname.startsWith(href) || mode === m ? 'bg-sidebar-accent' : ''
                  }`}
                  title={label}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </Link>
              ))}
            </nav>
          </div>
          <SimulationsSection />
          <div className="border-t border-sidebar-border px-2 pt-2">
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Config
            </p>
            <div className="space-y-2 px-3 py-2 text-xs text-muted-foreground">
              {mode === 'nbody' && <p>N-body config in right panel</p>}
            {mode === 'scan' && <p>Grid config in right panel</p>}
              {mode === 'mcmc' && <p>MCMC config in right panel</p>}
              {mode === 'publish' && <p>Export options, figure style</p>}
            </div>
          </div>
        </>
      )}
    </aside>
  )
}
