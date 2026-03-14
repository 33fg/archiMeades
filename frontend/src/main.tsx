import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster, toast } from 'sonner'
import '@/lib/amplify'
import { AuthProvider } from '@/contexts/AuthContext'
import { LayoutProvider } from '@/contexts/LayoutContext'
import { ProvenanceSettingsProvider } from '@/contexts/ProvenanceSettingsContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { SelectionProvider } from '@/contexts/SelectionContext'
import { WorkflowProvider } from '@/contexts/WorkflowContext'
import { type ApiError } from '@/lib/api'
import './index.css'
import App from './App.tsx'

function formatApiError(err: unknown): string {
  if (err && typeof err === 'object' && 'detail' in err && typeof (err as ApiError).detail === 'string') {
    return (err as ApiError).detail
  }
  return err instanceof Error ? err.message : 'An error occurred'
}

function isClientError(err: unknown): boolean {
  if (err && typeof err === 'object' && 'status' in err) {
    const s = (err as { status?: number }).status
    return s === 401 || s === 403 || s === 404 || s === 408
  }
  return false
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => (isClientError(error) ? false : failureCount < 2),
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 30_000,
      refetchOnWindowFocus: true,
    },
    mutations: {
      onError: (err) => toast.error(formatApiError(err)),
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Toaster richColors position="bottom-right" />
      <ReactQueryDevtools initialIsOpen={false} />
      <AuthProvider>
        <ThemeProvider>
          <ProvenanceSettingsProvider>
          <SelectionProvider>
            <WorkflowProvider>
              <LayoutProvider>
                <App />
              </LayoutProvider>
            </WorkflowProvider>
          </SelectionProvider>
          </ProvenanceSettingsProvider>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
)
