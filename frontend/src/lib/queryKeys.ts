/**
 * Query key factory - hierarchical keys by resource type.
 * WO-17: State Management and API Integration
 */

export const queryKeys = {
  all: ['gravitational'] as const,
  theories: {
    all: () => [...queryKeys.all, 'theories'] as const,
    lists: () => [...queryKeys.theories.all(), 'list'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.theories.lists(), filters ?? {}] as const,
    details: () => [...queryKeys.theories.all(), 'detail'] as const,
    detail: (id: string) => [...queryKeys.theories.details(), id] as const,
  },
  simulations: {
    all: () => [...queryKeys.all, 'simulations'] as const,
    lists: () => [...queryKeys.simulations.all(), 'list'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.simulations.lists(), filters ?? {}] as const,
    details: () => [...queryKeys.simulations.all(), 'detail'] as const,
    detail: (id: string) => [...queryKeys.simulations.details(), id] as const,
  },
  observations: {
    all: () => [...queryKeys.all, 'observations'] as const,
    lists: () => [...queryKeys.observations.all(), 'list'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.observations.lists(), filters ?? {}] as const,
    details: () => [...queryKeys.observations.all(), 'detail'] as const,
    detail: (id: string) => [...queryKeys.observations.details(), id] as const,
  },
  health: () => [...queryKeys.all, 'health'] as const,
}
