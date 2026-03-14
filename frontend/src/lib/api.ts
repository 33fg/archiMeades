/**
 * API client - base URL, auth header injection, error handling.
 * WO-17: State Management and API Integration
 * WO-16: 401 handler for expired sessions
 */

// In dev, use relative URLs so Vite proxy forwards to backend (avoids CORS)
const API_BASE = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : 'http://localhost:8002')

let on401Handler: (() => void) | null = null
export function setOn401Handler(handler: (() => void) | null) {
  on401Handler = handler
}

export interface ApiError {
  detail: string
  status?: number
  type?: string
  title?: string
}

const REQUEST_TIMEOUT_MS = 15_000

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const { token, ...init } = options
  const headers: HeadersInit = {
    ...(init.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    ...(init.headers as Record<string, string>),
  }
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, { ...init, headers, signal: controller.signal })
  } catch (err) {
    clearTimeout(timeoutId)
    if (err && typeof err === 'object' && 'detail' in err) {
      throw err
    }
    if (err instanceof Error && err.name === 'AbortError') {
      throw { detail: 'Request timed out. Is the backend running?', status: 408 } as ApiError
    }
    const msg = err instanceof Error ? err.message : 'Network error'
    throw { detail: msg, status: 500 } as ApiError
  }
  clearTimeout(timeoutId)

  if (!res.ok) {
    let detail: string
    let type: string | undefined
    let title: string | undefined
    try {
      const body = (await res.json()) as Record<string, unknown>
      // RFC 7807 Problem Details: type, title, status, detail
      type = typeof body.type === 'string' ? body.type : undefined
      title = typeof body.title === 'string' ? body.title : undefined
      const raw = body.detail ?? body.message ?? res.statusText
      if (typeof raw === 'string') detail = raw
      else if (Array.isArray(raw)) detail = raw.map((e) => (e as { msg?: string })?.msg ?? (e as { message?: string })?.message ?? String(e)).join(', ')
      else detail = typeof raw === 'object' ? JSON.stringify(raw) : String(raw)
    } catch {
      detail = res.statusText
    }
    if (res.status === 401) {
      on401Handler?.()
    }
    throw { detail, status: res.status, type, title } as ApiError
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string, token?: string | null) =>
    apiRequest<T>(path, { method: 'GET', token }),
  post: <T>(path: string, body: unknown, token?: string | null) =>
    apiRequest<T>(path, {
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body),
      token,
    }),
  put: <T>(path: string, body: unknown, token?: string | null) =>
    apiRequest<T>(path, { method: 'PUT', body: JSON.stringify(body), token }),
  patch: <T>(path: string, body: unknown, token?: string | null) =>
    apiRequest<T>(path, { method: 'PATCH', body: JSON.stringify(body), token }),
  delete: <T>(path: string, token?: string | null) =>
    apiRequest<T>(path, { method: 'DELETE', token }),
}
