/**
 * Theory detail page - view and edit a single theory.
 * WO-20: Provenance section shows simulations and lineage from Neo4j.
 */

import { useEffect, useState } from 'react'
import { ArrowLeft, BookOpen, Pencil, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useApiQuery, useApiMutation } from '@/hooks/useApi'
import { queryKeys } from '@/lib/queryKeys'
import { ProvenanceViewer } from '@/components/ProvenanceViewer'
import { useProvenanceSettings } from '@/contexts/ProvenanceSettingsContext'

interface Theory {
  id: string
  name: string
  description: string | null
  equation_spec: string | null
}

export function TheoryDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editEquationSpec, setEditEquationSpec] = useState('')

  const { data: theory, isLoading, error } = useApiQuery<Theory>(
    queryKeys.theories.detail(id!),
    `/api/theories/${id}`,
    { enabled: !!id }
  )
  const { data: lineage, error: lineageError } = useApiQuery<{
    theory_id: string
    simulation_ids: string[]
    publication_ids: string[]
  }>(
    ['provenance', 'lineage', id!],
    `/api/provenance/theory/${id}/lineage`,
    { enabled: !!id && !!theory, retry: false }
  )
  const { settings: provSettings } = useProvenanceSettings()
  const deleteMutation = useApiMutation<unknown, { id: string }>(
    'delete',
    (v) => `/api/theories/${v.id}`
  )
  const updateMutation = useApiMutation<
    Theory,
    { id: string; name?: string; description?: string; equation_spec?: string }
  >('patch', (v) => `/api/theories/${v.id}`)

  useEffect(() => {
    document.title = theory ? `${theory.name} · Gravitational Physics` : 'Theory · Gravitational Physics'
  }, [theory])

  useEffect(() => {
    if (theory) {
      setEditName(theory.name)
      setEditDescription(theory.description ?? '')
      setEditEquationSpec(theory.equation_spec ?? '')
    }
  }, [theory])

  if (!id) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/theories">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Theories
          </Button>
        </Link>
        <p className="text-destructive">Invalid theory ID</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center p-8">
        <p className="text-muted-foreground">Loading theory...</p>
      </div>
    )
  }

  if (error || !theory) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/theories">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Theories
          </Button>
        </Link>
        <p className="text-destructive">
          {error?.detail ?? 'Theory not found'}
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <Link to="/theories">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Theories
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
              if (window.confirm(`Delete "${theory.name}"? This cannot be undone.`)) {
                deleteMutation.mutate(
                  { id: theory.id },
                  { onSuccess: () => navigate('/theories') }
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
                  id: theory.id,
                  name: editName,
                  description: editDescription || undefined,
                  equation_spec: editEquationSpec || undefined,
                },
                {
                  onSuccess: () => setEditing(false),
                }
              )
            }}
            className="space-y-4"
          >
            <div>
              <label htmlFor="edit-name" className="block text-sm font-medium text-foreground mb-1">
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
              <label htmlFor="edit-desc" className="block text-sm font-medium text-foreground mb-1">
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
              <label htmlFor="edit-eq" className="block text-sm font-medium text-foreground mb-1">
                Equation spec
              </label>
              <input
                id="edit-eq"
                type="text"
                value={editEquationSpec}
                onChange={(e) => setEditEquationSpec(e.target.value)}
                placeholder="e.g. G_μν = 8πT_μν"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
              />
            </div>
            {updateMutation.error && (
              <p className="text-sm text-destructive">{updateMutation.error.detail}</p>
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
                  setEditName(theory.name)
                  setEditDescription(theory.description ?? '')
                  setEditEquationSpec(theory.equation_spec ?? '')
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-muted-foreground" />
              <h1 className="text-2xl font-bold text-foreground">{theory.name}</h1>
            </div>
            {theory.description && (
              <p className="mt-4 text-muted-foreground">{theory.description}</p>
            )}
            {theory.equation_spec && (
              <div className="mt-4 rounded-md bg-muted/50 p-4">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Equation spec
                </p>
                <p className="mt-2 font-mono text-sm">{theory.equation_spec}</p>
              </div>
            )}
            <p className="mt-4 font-mono text-xs text-muted-foreground">ID: {theory.id}</p>

            {/* WO-20, WO-47: Provenance viewer with verification and export */}
            <ProvenanceViewer
              type="theory"
              data={lineage ?? null}
              verified={!!lineage}
              error={lineageError?.status === 503}
              showExport={provSettings.showExportButton}
              showVerification={provSettings.verificationEnabled}
            />

            {deleteMutation.error && (
              <p className="mt-4 text-sm text-destructive">{deleteMutation.error.detail}</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
