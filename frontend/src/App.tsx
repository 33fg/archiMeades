import { useAuth } from '@/contexts/AuthContext'
import { ExploreProvider } from '@/contexts/ExploreContext'
import { MCMCProvider } from '@/contexts/MCMCContext'
import { NBodyProvider } from '@/contexts/NBodyContext'
import { ScanProvider } from '@/contexts/ScanContext'
import { AppShell } from '@/components/layout'
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { HomePage } from '@/pages/HomePage'
import { LoginPage } from '@/pages/LoginPage'
import { DatasetDetailPage } from '@/pages/DatasetDetailPage'
import { ObservationDetailPage } from '@/pages/ObservationDetailPage'
import { ObservationsPage } from '@/pages/ObservationsPage'
import { SimulationDetailPage } from '@/pages/SimulationDetailPage'
import { SimulationsPage } from '@/pages/SimulationsPage'
import { TheoryDetailPage } from '@/pages/TheoryDetailPage'
import { TheoriesPage } from '@/pages/TheoriesPage'
import { ExplorePage } from '@/pages/ExplorePage'
import { ScanPage } from '@/pages/ScanPage'
import { InferencePage } from '@/pages/InferencePage'
import { NBodyPage } from '@/pages/NBodyPage'
import { PublicationsPage } from '@/pages/PublicationsPage'
import { PhysicsNumericsPage } from '@/pages/PhysicsNumericsPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

function AppLayout() {
  return (
    <ProtectedRoute>
      <ExploreProvider>
        <MCMCProvider>
          <NBodyProvider>
            <ScanProvider>
            <AppShell>
              <Outlet />
            </AppShell>
            </ScanProvider>
          </NBodyProvider>
        </MCMCProvider>
      </ExploreProvider>
    </ProtectedRoute>
  )
}

function AppRoutes() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/theories" element={<TheoriesPage />} />
        <Route path="/theories/:id" element={<TheoryDetailPage />} />
        <Route path="/simulations" element={<SimulationsPage />} />
        <Route path="/simulations/:id" element={<SimulationDetailPage />} />
        <Route path="/observations" element={<ObservationsPage />} />
        <Route path="/observations/datasets/:id" element={<DatasetDetailPage />} />
        <Route path="/observations/:id" element={<ObservationDetailPage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/nbody" element={<NBodyPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/inference" element={<InferencePage />} />
        <Route path="/publications" element={<PublicationsPage />} />
        <Route path="/library" element={<PhysicsNumericsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}
