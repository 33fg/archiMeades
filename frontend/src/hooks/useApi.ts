/**
 * useApi - React Query integration with auth token injection.
 * WO-17: State Management and API Integration
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationOptions,
  type UseQueryOptions,
} from '@tanstack/react-query'
import { useAuth } from '@/contexts/AuthContext'
import { api, type ApiError } from '@/lib/api'

export function useApiQuery<T>(
  queryKey: readonly unknown[],
  path: string,
  options?: Omit<UseQueryOptions<T, ApiError>, 'queryKey' | 'queryFn'>
) {
  const { getToken } = useAuth()
  return useQuery<T, ApiError>({
    queryKey,
    queryFn: () => api.get<T>(path, getToken()),
    ...options,
  })
}

export function useApiMutation<TData, TVars>(
  method: 'post' | 'put' | 'patch' | 'delete',
  pathFn: (vars: TVars) => string,
  options?: UseMutationOptions<TData, ApiError, TVars>
) {
  const { getToken } = useAuth()
  const queryClient = useQueryClient()

  return useMutation<TData, ApiError, TVars>({
    mutationFn: async (vars) => {
      const path = pathFn(vars)
      const token = getToken()
      if (method === 'post' || method === 'put' || method === 'patch') {
        const body = (vars as { body?: unknown })?.body ?? vars
        return api[method]<TData>(path, body, token)
      }
      return api.delete<TData>(path, token)
    },
    onSettled: () => queryClient.invalidateQueries(),
    ...options,
  })
}
