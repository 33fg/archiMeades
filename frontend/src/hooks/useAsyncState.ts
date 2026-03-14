/**
 * useAsyncState - loading and error state helpers.
 * WO-17: State Management and API Integration
 *
 * Wraps useApiQuery to expose a consistent { loading, error, data, refetch } interface.
 * Use for simple list/detail pages where you need loading/error/data in one place.
 */

import type { UseQueryOptions } from '@tanstack/react-query'
import { useApiQuery } from './useApi'
import type { ApiError } from '@/lib/api'

export function useAsyncState<T>(
  queryKey: readonly unknown[],
  path: string,
  options?: Omit<UseQueryOptions<T, ApiError>, 'queryKey' | 'queryFn'>
) {
  const query = useApiQuery<T>(queryKey, path, options)
  return {
    loading: query.isLoading,
    error: query.error,
    data: query.data,
    refetch: query.refetch,
    isFetching: query.isFetching,
  }
}
