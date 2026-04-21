import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/services/auth-context'

// Layouts
import { CustomerLayout } from '@/layouts/CustomerLayout'
import { GarageLayout } from '@/layouts/GarageLayout'
import { AdminLayout } from '@/layouts/AdminLayout'

// Pages — Customer
import { CustomerHome } from '@/pages/customer/CustomerHome'
import { CustomerGarageDetail } from '@/pages/customer/GarageDetail'
import { CustomerBookingTracker } from '@/pages/customer/BookingTracker'
import { CustomerVehicles } from '@/pages/customer/CustomerVehicles'
import { CustomerMap } from '@/pages/customer/CustomerMap'
import { CustomerBookings } from '@/pages/customer/CustomerBookings'
import { CustomerProfile } from '@/pages/customer/CustomerProfile'

// Pages — Garage Owner
import { GarageDashboard } from '@/pages/garage/GarageDashboard'
import { GarageQueue } from '@/pages/garage/GarageQueue'
import { GarageAnalytics } from '@/pages/garage/GarageAnalytics'
import { GarageServices } from '@/pages/garage/GarageServices'
import { GarageScore } from '@/pages/garage/GarageScore'

// Pages — Admin (Platform)
import { AdminDashboard } from '@/pages/admin/AdminDashboard'

// Auth
import { LoginPage } from '@/pages/auth/LoginPage'

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-sm font-bold text-slate-400 uppercase tracking-widest">Authenticating...</span>
      </div>
    </div>
  )
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RoleRedirect() {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'customer') return <Navigate to="/app" replace />
  if (user.role === 'garage_owner' || user.role === 'garage_manager' || user.role === 'garage_staff')
    return <Navigate to="/garage" replace />
  return <Navigate to="/admin" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── Auth ── */}
        <Route path="/login" element={<LoginPage />} />

        {/* ── Customer Routes ── */}
        <Route path="/app" element={
          <ProtectedRoute allowedRoles={['customer']}>
            <CustomerLayout />
          </ProtectedRoute>
        }>
          <Route index element={<CustomerHome />} />
          <Route path="map" element={<CustomerMap />} />
          <Route path="garages/:id" element={<CustomerGarageDetail />} />
          <Route path="bookings" element={<CustomerBookings />} />
          <Route path="bookings/:id" element={<CustomerBookingTracker />} />
          <Route path="vehicles" element={<CustomerVehicles />} />
          <Route path="profile" element={<CustomerProfile />} />
        </Route>

        {/* ── Garage Owner Routes ── */}
        <Route path="/garage" element={
          <ProtectedRoute allowedRoles={['garage_owner', 'garage_manager', 'garage_staff']}>
            <GarageLayout />
          </ProtectedRoute>
        }>
          <Route index element={<GarageDashboard />} />
          <Route path="queue" element={<GarageQueue />} />
          <Route path="analytics" element={<GarageAnalytics />} />
          <Route path="services" element={<GarageServices />} />
          <Route path="score" element={<GarageScore />} />
        </Route>

        {/* ── Admin (Platform) Routes ── */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['super_admin', 'platform_ops']}>
            <AdminLayout />
          </ProtectedRoute>
        }>
          <Route index element={<AdminDashboard />} />
        </Route>

        {/* ── Root ── */}
        <Route path="/" element={<RoleRedirect />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
