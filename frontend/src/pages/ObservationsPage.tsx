/**
 * Observations page - observational data for comparison.
 * WO-29: Dataset browser for built-in and custom datasets.
 */

import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Database, Plus, Trash2, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { QueryStateGuard } from '@/components/ui/QueryStateGuard'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/contexts/AuthContext'
import { api, type ApiError } from '@/lib/api'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'

interface Observation {
  id: string
  name: string
  description: string | null
  source: string | null
  metadata_json: string | null
}

interface DatasetSummary {
  id: string
  name: string
  type: string
  num_points?: number
  observable_type?: string
  citation?: string
  unavailable_hint?: string
}

export function ObservationsPage() {
  const navigate = useNavigate()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [source, setSource] = useState('')

  const { data: datasets } = useApiQuery<DatasetSummary[]>(
    ['observations', 'datasets'],
    '/api/observations/datasets'
  )
  const { data: observations, isLoading, error, refetch } = useApiQuery<Observation[]>(
    ['observations'],
    '/api/observations'
  )
  const queryClient = useQueryClient()
  const { getToken } = useAuth()
  const createMutation = useApiMutation<
    Observation,
    { name: string; description?: string; source?: string }
  >('post', () => '/api/observations')
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/observations/${v.id}`
  )
  const uploadMutation = useMutation<Observation, ApiError, { file: File; name?: string }>({
    mutationFn: async ({ file, name }) => {
      const form = new FormData()
      form.append('file', file)
      if (name) form.append('name', name)
      return api.post<Observation>('/api/observations/upload', form, getToken())
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['observations'] })
      queryClient.invalidateQueries({ queryKey: ['observations', 'datasets'] })
      navigate(`/observations/datasets/${data.id}`)
    },
  })
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    document.title = 'Observations · Gravitational Physics'
  }, [])

  return (
    <QueryStateGuard
      isLoading={isLoading}
      error={error}
      refetch={refetch}
      loadingMessage="Loading observations..."
    >
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center gap-2">
        <Database className="h-6 w-6 text-muted-foreground" />
        <h1 className="text-2xl font-bold text-foreground">Observations</h1>
      </div>
      <p className="text-muted-foreground">
        Observational datasets for comparing simulations with real-world data.
      </p>

      {/* WO-29: Dataset browser */}
      {datasets && datasets.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-foreground mb-3">Datasets</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {datasets.map((ds) => (
              <Link
                key={ds.id}
                to={`/observations/datasets/${ds.id}`}
                className="rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/50 block"
              >
                <h3 className="font-medium text-foreground">{ds.name}</h3>
                <p className="mt-1 text-xs text-muted-foreground">
                  {ds.type} · {ds.num_points != null ? `${ds.num_points} points` : ds.unavailable_hint ?? '—'}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}

      <h2 className="text-lg font-semibold text-foreground">Custom observations</h2>
      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowForm((s) => !s)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          {showForm ? 'Cancel' : 'Create observation'}
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) {
              uploadMutation.mutate({ file })
              e.target.value = ''
            }
          }}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadMutation.isPending}
          className="gap-2"
        >
          <Upload className="h-4 w-4" />
          {uploadMutation.isPending ? 'Uploading...' : 'Upload CSV'}
        </Button>
      </div>
      {uploadMutation.error && (
        <p className="text-sm text-destructive">{uploadMutation.error.detail}</p>
      )}
      {showForm && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            createMutation.mutate(
              {
                name,
                description: description || undefined,
                source: source || undefined,
              },
              {
                onSuccess: () => {
                  setName('')
                  setDescription('')
                  setSource('')
                  setShowForm(false)
                },
              }
            )
          }}
          className="rounded-lg border border-border bg-card p-4 space-y-4"
        >
          <div>
            <label htmlFor="obs-name" className="block text-sm font-medium text-foreground mb-1">
              Name
            </label>
            <input
              id="obs-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="obs-desc" className="block text-sm font-medium text-foreground mb-1">
              Description
            </label>
            <input
              id="obs-desc"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="obs-source" className="block text-sm font-medium text-foreground mb-1">
              Source
            </label>
            <input
              id="obs-source"
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="e.g. HST, JWST, Gaia"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
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
      {!observations || observations.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border bg-muted/30 p-8 text-center">
          <p className="text-muted-foreground">No observations yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Click Create observation above to add one.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {observations.map((obs) => (
            <li key={obs.id} className="flex gap-2">
              <Link
                to={`/observations/${obs.id}`}
                className="flex-1 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/50 block"
              >
                <h2 className="font-semibold text-foreground">{obs.name}</h2>
                {obs.description && (
                  <p className="mt-1 text-sm text-muted-foreground">{obs.description}</p>
                )}
                {obs.source && (
                  <p className="mt-1 text-xs text-muted-foreground">Source: {obs.source}</p>
                )}
              </Link>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-muted-foreground hover:text-destructive"
                disabled={deleteMutation.isPending}
                onClick={() => {
                  if (window.confirm(`Delete "${obs.name}"?`)) {
                    deleteMutation.mutate({ id: obs.id })
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
