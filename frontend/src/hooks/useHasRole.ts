/**
 * useHasRole - role-based access control for conditional UI rendering.
 * WO-16: Authentication Integration with Amplify
 */

import { useAuth } from '@/contexts/AuthContext'

export function useHasRole(allowedRoles: string | string[]): boolean {
  const { user } = useAuth()
  if (!user) return false
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles]
  return roles.includes(user.role)
}
