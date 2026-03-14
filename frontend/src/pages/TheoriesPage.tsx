/**
 * Theories page - list and manage gravitational theory definitions.
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { BookOpen, Plus, Trash2, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { QueryStateGuard } from '@/components/ui/QueryStateGuard'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'
import { queryKeys } from '@/lib/queryKeys'

interface Theory {
  id: string
  name: string
  description: string | null
  equation_spec: string | null
}

type FormMode = 'create' | 'register' | null

export function TheoriesPage() {
  const navigate = useNavigate()
  const [showForm, setShowForm] = useState(false)
  const [formMode, setFormMode] = useState<FormMode>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [equationSpec, setEquationSpec] = useState('')
  const [identifier, setIdentifier] = useState('')
  const [version, setVersion] = useState('')
  const [code, setCode] = useState('')

  const { data: theories, isLoading, error, refetch } = useApiQuery<Theory[]>(
    queryKeys.theories.list(),
    '/api/theories'
  )
  const createMutation = useApiMutation<Theory, { name: string; description?: string; equation_spec?: string }>(
    'post',
    () => '/api/theories'
  )
  const registerMutation = useApiMutation<
    { message: string; theory_id: string; status_url: string },
    { identifier: string; version: string; code: string }
  >('post', () => '/api/theories/register')
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/theories/${v.id}`
  )

  useEffect(() => {
    document.title = 'Theories · Gravitational Physics'
  }, [])

  return (
    <QueryStateGuard
      isLoading={isLoading}
      error={error}
      refetch={refetch}
      loadingMessage="Loading theories..."
    >
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center gap-2">
        <BookOpen className="h-6 w-6 text-muted-foreground" />
        <h1 className="text-2xl font-bold text-foreground">Theories</h1>
      </div>
      <p className="text-muted-foreground">
        Gravitational theory definitions for simulations and analysis.
      </p>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            if (showForm && formMode === 'create') {
              setShowForm(false)
              setFormMode(null)
            } else {
              setShowForm(true)
              setFormMode('create')
            }
          }}
          className="w-fit gap-2"
        >
          <Plus className="h-4 w-4" />
          {showForm && formMode === 'create' ? 'Cancel' : 'Create theory'}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            if (showForm && formMode === 'register') {
              setShowForm(false)
              setFormMode(null)
            } else {
              setShowForm(true)
              setFormMode('register')
            }
          }}
          className="w-fit gap-2"
        >
          <Upload className="h-4 w-4" />
          {showForm && formMode === 'register' ? 'Cancel' : 'Register theory'}
        </Button>
      </div>
      {showForm && formMode === 'create' && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            createMutation.mutate(
              {
                name,
                description: description || undefined,
                equation_spec: equationSpec || undefined,
              },
              {
                onSuccess: () => {
                  setName('')
                  setDescription('')
                  setEquationSpec('')
                  setShowForm(false)
                  setFormMode(null)
                },
              }
            )
          }}
          className="rounded-lg border border-border bg-card p-4 space-y-4"
        >
          <div>
            <label htmlFor="theory-name" className="block text-sm font-medium text-foreground mb-1">
              Name
            </label>
            <input
              id="theory-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="theory-desc" className="block text-sm font-medium text-foreground mb-1">
              Description
            </label>
            <input
              id="theory-desc"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="theory-eq" className="block text-sm font-medium text-foreground mb-1">
              Equation spec
            </label>
            <input
              id="theory-eq"
              type="text"
              value={equationSpec}
              onChange={(e) => setEquationSpec(e.target.value)}
              placeholder="e.g. G_μν = 8πT_μν"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
            />
          </div>
          {createMutation.error && (
            <p className="text-sm text-destructive">{createMutation.error.detail}</p>
          )}
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creating...' : 'Create'}
          </Button>
        </form>
      )}
      {showForm && formMode === 'register' && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            registerMutation.mutate(
              { identifier, version, code },
              {
                onSuccess: (data) => {
                  setIdentifier('')
                  setVersion('')
                  setCode('')
                  setShowForm(false)
                  setFormMode(null)
                  navigate(`/theories/${data.theory_id}`)
                },
              }
            )
          }}
          className="rounded-lg border border-border bg-card p-4 space-y-4"
        >
          <p className="text-sm text-muted-foreground">
            Register a theory with code. Validation runs async; you can check status on the theory page.
          </p>
          <div>
            <label htmlFor="reg-identifier" className="block text-sm font-medium text-foreground mb-1">
              Identifier
            </label>
            <input
              id="reg-identifier"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="e.g. lambda_cdm"
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
            />
          </div>
          <div>
            <label htmlFor="reg-version" className="block text-sm font-medium text-foreground mb-1">
              Version
            </label>
            <input
              id="reg-version"
              type="text"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="e.g. 1.0.0"
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
            />
          </div>
          <div>
            <label htmlFor="reg-code" className="block text-sm font-medium text-foreground mb-1">
              Code (Python)
            </label>
            <textarea
              id="reg-code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={'def luminosity_distance(z, params):\n    return 0.0\ndef age_of_universe(params):\n    return 13.8'}
              required
              rows={8}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
            />
          </div>
          {registerMutation.error && (
            <p className="text-sm text-destructive">{registerMutation.error.detail}</p>
          )}
          <Button type="submit" disabled={registerMutation.isPending}>
            {registerMutation.isPending ? 'Registering...' : 'Register'}
          </Button>
        </form>
      )}
      {!theories || theories.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border bg-muted/30 p-8 text-center">
          <p className="text-muted-foreground">No theories yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Click Create theory above to add one.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {theories.map((theory) => (
            <li key={theory.id} className="flex gap-2">
              <Link
                to={`/theories/${theory.id}`}
                className="flex-1 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/50"
              >
                <h2 className="font-semibold text-foreground">{theory.name}</h2>
                {theory.description && (
                  <p className="mt-1 text-sm text-muted-foreground">{theory.description}</p>
                )}
                {theory.equation_spec && (
                  <p className="mt-2 font-mono text-xs text-muted-foreground">
                    {theory.equation_spec}
                  </p>
                )}
              </Link>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-muted-foreground hover:text-destructive"
                disabled={deleteMutation.isPending}
                onClick={(e) => {
                  e.preventDefault()
                  if (window.confirm(`Delete "${theory.name}"?`)) {
                    deleteMutation.mutate({ id: theory.id })
                  }
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
    </QueryStateGuard>
  )
}
