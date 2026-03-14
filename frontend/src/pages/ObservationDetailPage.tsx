/**
 * Observation detail page - view and edit a single observation.
 */

import { useEffect, useState } from 'react'
import { ArrowLeft, Database, Pencil, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'

interface Observation {
  id: string
  name: string
  description: string | null
  source: string | null
  metadata_json: string | null
}

export function ObservationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editSource, setEditSource] = useState('')

  const { data: observation, isLoading, error } = useApiQuery<Observation>(
    ['observation', id!],
    `/api/observations/${id}`,
    { enabled: !!id }
  )
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/observations/${v.id}`
  )
  const updateMutation = useApiMutation<
    Observation,
    { id: string; name?: string; description?: string; source?: string }
  >('patch', (v) => `/api/observations/${v.id}`)

  useEffect(() => {
    document.title = observation
      ? `${observation.name} · Gravitational Physics`
      : 'Observation · Gravitational Physics'
  }, [observation])

  useEffect(() => {
    if (observation) {
      setEditName(observation.name)
      setEditDescription(observation.description ?? '')
      setEditSource(observation.source ?? '')
    }
  }, [observation])

  if (!id) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/observations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Observations
          </Button>
        </Link>
        <p className="text-destructive">Invalid observation ID</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center p-8">
        <p className="text-muted-foreground">Loading observation...</p>
      </div>
    )
  }

  if (error || !observation) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/observations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Observations
          </Button>
        </Link>
        <p className="text-destructive">
          {error?.detail ?? 'Observation not found'}
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <Link to="/observations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Observations
          </Button>
        </Link>
        <div className="flex gap-2">
          {!editing ? (
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              onClick={() => setEditing(true)}
            >
              <Pencil className="h-4 w-4" />
              Edit
            </Button>
          ) : null}
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (
                window.confirm(
                  `Delete "${observation.name}"? This cannot be undone.`
                )
              ) {
                deleteMutation.mutate(
                  { id: observation.id },
                  { onSuccess: () => navigate('/observations') }
                )
              }
            }}
          >
            <Trash2 className="h-4 w-4" />
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        {editing ? (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              updateMutation.mutate(
                {
                  id: observation.id,
                  name: editName,
                  description: editDescription || undefined,
                  source: editSource || undefined,
                },
                { onSuccess: () => setEditing(false) }
              )
            }}
            className="space-y-4"
          >
            <div>
              <label
                htmlFor="edit-name"
                className="block text-sm font-medium text-foreground mb-1"
              >
                Name
              </label>
              <input
                id="edit-name"
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="edit-desc"
                className="block text-sm font-medium text-foreground mb-1"
              >
                Description
              </label>
              <input
                id="edit-desc"
                type="text"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="edit-source"
                className="block text-sm font-medium text-foreground mb-1"
              >
                Source
              </label>
              <input
                id="edit-source"
                type="text"
                value={editSource}
                onChange={(e) => setEditSource(e.target.value)}
                placeholder="e.g. HST, JWST, Gaia"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            {updateMutation.error && (
              <p className="text-sm text-destructive">
                {updateMutation.error.detail}
              </p>
            )}
            <div className="flex gap-2">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Saving...' : 'Save'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setEditing(false)
                  setEditName(observation.name)
                  setEditDescription(observation.description ?? '')
                  setEditSource(observation.source ?? '')
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <Database className="h-6 w-6 text-muted-foreground" />
              <h1 className="text-2xl font-bold text-foreground">
                {observation.name}
              </h1>
            </div>
            {observation.description && (
              <p className="mt-4 text-muted-foreground">
                {observation.description}
              </p>
            )}
            {observation.source && (
              <p className="mt-2 text-sm text-muted-foreground">
                Source: {observation.source}
              </p>
            )}
            <p className="mt-4 font-mono text-xs text-muted-foreground">
              ID: {observation.id}
            </p>
            {deleteMutation.error && (
              <p className="mt-4 text-sm text-destructive">
                {deleteMutation.error.detail}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
