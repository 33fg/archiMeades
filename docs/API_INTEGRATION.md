# API Integration Patterns

**WO-17: State Management and API Integration**

This document describes patterns for integrating with the backend API in feature development.

## Overview

- **React Query (TanStack Query)** for server state: caching, refetching, loading/error states
- **useApiQuery** and **useApiMutation** hooks with automatic Cognito token injection
- **Query key factory** (`queryKeys`) for hierarchical cache keys
- **RFC 7807 Problem Details** error parsing for backend exceptions

## useApiQuery

For GET requests. Automatically injects the Bearer token when the user is authenticated.

```tsx
import { useApiQuery } from '@/hooks/useApi'
import { queryKeys } from '@/lib/queryKeys'

const { data, isLoading, error, refetch } = useApiQuery<Theory[]>(
  queryKeys.theories.list(),
  '/api/theories'
)
```

**Options**: Pass any `UseQueryOptions` (staleTime, retry, enabled, etc.) as the third argument.

## useApiMutation

For POST, PUT, PATCH, DELETE. Provides a path function and handles cache invalidation on success.

```tsx
import { useApiMutation } from '@/hooks/useApi'
import { queryKeys } from '@/lib/queryKeys'

const createMutation = useApiMutation<Theory, { name: string; description?: string }>(
  'post',
  () => '/api/theories'
)

createMutation.mutate({ name: 'My Theory', description: '...' })
```

For mutations that need the resource ID:

```tsx
const updateMutation = useApiMutation<Theory, { id: string; name: string }>(
  'patch',
  (vars) => `/api/theories/${vars.id}`
)
```

**Cache invalidation**: By default, `onSettled` invalidates all queries. Override in options to invalidate specific keys:

```tsx
useApiMutation<Theory, { id: string }>('put', (v) => `/api/theories/${v.id}`, {
  onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.theories.all() }),
})
```

## useAsyncState

Thin wrapper around `useApiQuery` that exposes `loading`, `error`, `data`, `refetch`. Use when you prefer `loading` over `isLoading`.

```tsx
import { useAsyncState } from '@/hooks/useAsyncState'

const { loading, error, data, refetch } = useAsyncState<Theory[]>(
  queryKeys.theories.list(),
  '/api/theories'
)
```

## Query Key Factory

Use `queryKeys` for consistent, hierarchical cache keys. Enables targeted invalidation.

```tsx
import { queryKeys } from '@/lib/queryKeys'

// List all theories
queryKeys.theories.list()

// List with filters
queryKeys.theories.list({ status: 'active' })

// Single theory
queryKeys.theories.detail(id)

// Invalidate all theory-related queries
queryClient.invalidateQueries({ queryKey: queryKeys.theories.all() })
```

When adding a new resource, extend `queryKeys` in `src/lib/queryKeys.ts`.

## Error Handling

- **ApiError**: `{ detail: string, status?: number, type?: string, title?: string }`
- Backend uses RFC 7807 Problem Details; `type` and `title` are parsed when present
- **401/403/404/408**: No retry (user action required)
- **500+**: Retry up to 2 times with exponential backoff
- **Mutations**: Global toast on error via QueryClient defaults
- **Queries**: Use `QueryStateGuard` or per-page error UI

## QueryStateGuard

For list/detail pages with loading and error states:

```tsx
<QueryStateGuard isLoading={isLoading} error={error} onRetry={refetch}>
  {/* Your content when data is ready */}
</QueryStateGuard>
```

## Adding a New Feature

1. Add query keys to `queryKeys` if needed
2. Use `useApiQuery` for data fetching
3. Use `useApiMutation` for create/update/delete
4. Wrap list/detail content in `QueryStateGuard` for loading/error
5. Handle mutation success (toast, navigate, invalidate specific keys)
