/**
 * Home / Dashboard page.
 */

import { useEffect } from 'react'
import { BookOpen, Cpu, Database, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/AuthContext'
import { useApiQuery } from '@/hooks/useApi'

interface CountItem {
  id: string
}

export function HomePage() {
  useEffect(() => {
    document.title = 'Dashboard · Gravitational Physics'
  }, [])
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8002'
  const { user, logout } = useAuth()

  const { data: theories } = useApiQuery<CountItem[]>(['theories-count'], '/api/theories?limit=1000')
  const { data: simulations } = useApiQuery<CountItem[]>(['simulations-count'], '/api/simulations?limit=1000')
  const { data: observations } = useApiQuery<CountItem[]>(['observations-count'], '/api/observations?limit=1000')

  const theoryCount = theories?.length ?? '–'
  const simCount = simulations?.length ?? '–'
  const obsCount = observations?.length ?? '–'

  return (
    <div className="flex min-h-full w-full flex-col items-center justify-center p-8 text-center">
      <h1 className="text-3xl font-bold text-foreground">
        ArchiMeades — Gravitational Physics Simulations Platform
      </h1>
      <p className="text-muted-foreground text-center max-w-lg">
        Research platform for defining theories, running GPU simulations, MCMC inference, and publishing results.
      </p>
      {user && (
        <p className="text-sm text-muted-foreground">
          Signed in as {user.email}{' '}
          <button
            type="button"
            onClick={logout}
            className="underline hover:text-foreground"
          >
            Sign out
          </button>
        </p>
      )}
      <div className="mt-8 flex flex-wrap justify-center gap-4">
        <Link to="/explore">
          <Button className="gap-2">
            <BookOpen className="h-4 w-4" />
            Explore
          </Button>
        </Link>
        <Link to="/theories">
          <Button variant="outline" className="gap-2">
            <BookOpen className="h-4 w-4" />
            Theories {theoryCount !== '–' && `(${theoryCount})`}
          </Button>
        </Link>
        <Link to="/simulations">
          <Button variant="outline" className="gap-2">
            <Cpu className="h-4 w-4" />
            Simulations {simCount !== '–' && `(${simCount})`}
          </Button>
        </Link>
        <Link to="/observations">
          <Button variant="outline" className="gap-2">
            <Database className="h-4 w-4" />
            Observations {obsCount !== '–' && `(${obsCount})`}
          </Button>
        </Link>
        <a href={`${backendUrl}/docs`} target="_blank" rel="noreferrer">
          <Button variant="outline" className="gap-2">
            <ExternalLink className="h-4 w-4" />
            API Docs
          </Button>
        </a>
      </div>
    </div>
  )
}
