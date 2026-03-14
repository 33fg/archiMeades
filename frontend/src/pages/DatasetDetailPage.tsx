/**
 * WO-29: Dataset detail page - metadata, statistics, covariance info.
 */

import { ArrowLeft, BookOpen } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useApiQuery } from '@/hooks/useApi'
import { QueryStateGuard } from '@/components/ui/QueryStateGuard'

interface DatasetDetail {
  id: string
  name: string
  type: string
  num_points: number
  observable_type: string
  citation: string
  redshift_min?: number
  redshift_max?: number
  covariance_shape?: number[]
}

export function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: dataset, isLoading, error, refetch } = useApiQuery<DatasetDetail>(
    ['dataset', id!],
    `/api/observations/datasets/${id}`,
    { enabled: !!id }
  )

  return (
    <QueryStateGuard
      isLoading={isLoading}
      error={error}
      refetch={refetch}
      loadingMessage="Loading dataset..."
    >
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
        <Link to="/observations">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Observations
          </Button>
        </Link>
        {dataset && (
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-muted-foreground" />
              <h1 className="text-2xl font-bold text-foreground">{dataset.name}</h1>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  dataset.type === 'builtin'
                    ? 'bg-blue-500/20 text-blue-700 dark:text-blue-400'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {dataset.type}
              </span>
            </div>
            <div className="mt-6 space-y-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Data points
                </p>
                <p className="mt-1">{dataset.num_points.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Observable type
                </p>
                <p className="mt-1 font-mono text-sm">{dataset.observable_type}</p>
              </div>
              {dataset.redshift_min != null && dataset.redshift_max != null && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Redshift range
                  </p>
                  <p className="mt-1">
                    {dataset.redshift_min.toFixed(4)} — {dataset.redshift_max.toFixed(4)}
                  </p>
                </div>
              )}
              {dataset.covariance_shape && dataset.covariance_shape.length >= 2 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Covariance matrix
                  </p>
                  <p className="mt-1 font-mono text-sm">
                    {dataset.covariance_shape[0]} × {dataset.covariance_shape[1]}
                  </p>
                </div>
              )}
              {dataset.citation && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Citation
                  </p>
                  <p className="mt-1 text-sm text-muted-foreground">{dataset.citation}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </QueryStateGuard>
  )
}
