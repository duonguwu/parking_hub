import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Component, type ErrorInfo, type ReactNode } from 'react'
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
import { GarageProfile } from '@/pages/garage/GarageProfile'

// Pages — Admin (Platform)
import { AdminDashboard } from '@/pages/admin/AdminDashboard'
import { AdminMap } from '@/pages/admin/AdminMap'
import { AdminGarages } from '@/pages/admin/AdminGarages'
import { AdminGarageDetail } from '@/pages/admin/AdminGarageDetail'
import { AdminUsers } from '@/pages/admin/AdminUsers'
import { AdminServices } from '@/pages/admin/AdminServices'

// Auth
import { LoginPage } from '@/pages/auth/LoginPage'

// PWA Components
import { PWABadge } from '@/components/pwa/PWABadge'
import { PWAInstallPrompt } from '@/components/pwa/PWAInstallPrompt'
import { OfflineBanner } from '@/components/pwa/OfflineBanner'

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
  // Đã đăng nhập nhưng sai vai trò → về trang chủ đúng vai trò, không đẩy về /login
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to={homeForRole(user.role)} replace />
  return <>{children}</>
}

const GARAGE_ROLES = ['garage_owner', 'garage_manager', 'garage_staff']
const CUSTOMER_ROLES = ['customer', 'fleet_manager']

function homeForRole(role: string): string {
  if (CUSTOMER_ROLES.includes(role)) return '/app'
  if (GARAGE_ROLES.includes(role)) return '/garage'
  return '/admin'
}

/** Bắt lỗi render để không bị trắng trang: hiện thông báo kèm nút tải lại. */
class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) { return { error } }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('UI error:', error, info.componentStack) }
  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="max-w-md text-center space-y-3">
          <h1 className="text-lg font-bold text-slate-800">Trang gặp lỗi hiển thị</h1>
          <p className="text-sm text-slate-500">{this.state.error.message}</p>
          <button onClick={() => window.location.assign('/')} className="px-4 py-2 rounded-full bg-blue-600 text-white text-sm font-semibold">Về trang chủ</button>
        </div>
      </div>
    )
  }
}

function RoleRedirect() {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={homeForRole(user.role)} replace />
}

function App() {
  return (
    <BrowserRouter>
      <OfflineBanner />
      <ErrorBoundary>
      <Routes>
        {/* ── Auth ── */}
        <Route path="/login" element={<LoginPage />} />

        {/* ── Customer Routes ── */}
        <Route path="/app" element={
          <ProtectedRoute allowedRoles={[...CUSTOMER_ROLES, 'super_admin']}>
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
          <ProtectedRoute allowedRoles={[...GARAGE_ROLES, 'super_admin']}>
            <GarageLayout />
          </ProtectedRoute>
        }>
          <Route index element={<GarageDashboard />} />
          <Route path="queue" element={<GarageQueue />} />
          <Route path="analytics" element={<GarageAnalytics />} />
          <Route path="services" element={<GarageServices />} />
          <Route path="score" element={<GarageScore />} />
          <Route path="profile" element={<GarageProfile />} />
        </Route>

        {/* ── Admin (Platform) Routes ── */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['super_admin', 'platform_ops']}>
            <AdminLayout />
          </ProtectedRoute>
        }>
          <Route index element={<AdminDashboard />} />
          <Route path="map" element={<AdminMap />} />
          <Route path="garages" element={<AdminGarages />} />
          <Route path="garages/:id" element={<AdminGarageDetail />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="services" element={<AdminServices />} />
        </Route>

        {/* ── Root ── */}
        <Route path="/" element={<RoleRedirect />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </ErrorBoundary>

      {/* ── PWA UI Elements ── */}
      <PWABadge />
      <PWAInstallPrompt />
    </BrowserRouter>
  )
}

export default App

