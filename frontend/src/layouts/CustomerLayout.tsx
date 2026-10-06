import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { MapPin, Calendar, Home, CarFront, User as UserIcon, Plus, ChevronDown, LogOut, ShieldCheck } from 'lucide-react'
import { ROLE_LABEL } from '@/services/api'
import { cn } from '@/services/utils'
import { Brand } from '@/components/Brand'
import { APP_TAGLINE } from '@/config/app'
import { useAuth } from '@/services/auth-context'
import { useState } from 'react'

const navItems = [
  { to: '/app', icon: Home, label: 'Trang chủ' },
  { to: '/app/map', icon: MapPin, label: 'Bản đồ' },
  { to: '/app/bookings', icon: Calendar, label: 'Lượt đặt' },
  { to: '/app/vehicles', icon: CarFront, label: 'Xe' },
  { to: '/app/profile', icon: UserIcon, label: 'Hồ sơ' },
]

export function CustomerLayout() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const userInitial = user?.name ? user.name.trim().charAt(0).toUpperCase() : (user?.username?.charAt(0).toUpperCase() ?? '?')

  return (
    <div className="flex min-h-screen bg-background relative selection:bg-blue-100">
      {/* ── Left Sidebar (Desktop Web: md và lớn hơn) ── */}
      <aside className="hidden md:flex fixed left-0 top-0 h-screen w-[280px] flex-col pt-8 pb-6 z-40 bg-surface border-r border-outline-variant">
        {/* Branding */}
        <div className="px-8 mb-8 flex flex-col items-start gap-1">
          <Brand className="text-2xl" />
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">{APP_TAGLINE}</p>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-1.5 px-4">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to || (item.to !== '/app' && location.pathname.startsWith(item.to))

            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  'px-4 py-3 flex items-center gap-3.5 rounded-full transition-all font-medium',
                  isActive
                    ? 'bg-primary text-white font-semibold'
                    : 'text-on-surface-variant hover:bg-surface-container-low hover:text-primary'
                )}
              >
                <item.icon className={cn('w-5 h-5 shrink-0', isActive ? 'text-white' : 'text-outline')} />
                <span className="text-sm">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Bottom Actions */}
        <div className="px-6 mt-auto space-y-4">
          <Link to="/app/map" className="block">
            <button className="w-full bg-primary-container text-on-primary-container hover:opacity-90 py-3 px-4 rounded-full text-xs font-bold tracking-wide transition-all flex items-center justify-center gap-2 border border-primary/20">
              <Plus className="w-4 h-4" />
              Đặt chỗ mới
            </button>
          </Link>
        </div>
      </aside>

      {/* ── Main Content Area ── */}
      <main className="ml-0 md:ml-[280px] flex-1 relative min-h-screen flex flex-col pb-20 md:pb-0">
        {/* ── Global Top Header ── */}
        <header className="h-16 md:h-[76px] bg-surface/90 backdrop-blur-md border-b border-outline-variant sticky top-0 z-30 px-4 md:px-8 flex items-center justify-between">
          {/* Logo on Mobile */}
          <div className="flex md:hidden items-center gap-2">
            <Brand className="text-lg" />
          </div>

          {/* Header Right Actions */}
          <div className="flex items-center gap-3 md:gap-4 ml-auto">


            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="flex items-center gap-2 hover:bg-surface-container-low p-1 pr-2.5 rounded-full transition-colors border border-outline-variant"
              >
                <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-xs">
                  {userInitial}
                </div>
                <div className="text-left hidden sm:block">
                  <p className="text-xs font-bold text-on-surface leading-tight">{user?.name ?? 'Khách'}</p>
                  <p className="text-[10px] font-medium text-on-surface-variant uppercase">{ROLE_LABEL[user?.role ?? ''] ?? user?.role ?? ''}</p>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-outline hidden sm:block" />
              </button>

              {showMenu && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-surface border border-outline-variant rounded-2xl z-50 overflow-hidden shadow-lg animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="px-4 py-3 border-b border-outline-variant sm:hidden">
                    <p className="text-xs font-bold text-on-surface">{user?.name ?? 'Khách'}</p>
                    <p className="text-[10px] text-on-surface-variant uppercase">{ROLE_LABEL[user?.role ?? ''] ?? user?.role ?? ''}</p>
                  </div>
                  {user?.role === 'super_admin' && (
                    <Link to="/admin" onClick={() => setShowMenu(false)}
                      className="w-full flex items-center gap-2.5 px-4 py-3 text-xs font-semibold text-primary hover:bg-surface-container-low transition-colors">
                      <ShieldCheck className="w-4 h-4" /> Về trang quản trị
                    </Link>
                  )}
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-4 py-3 text-xs font-semibold text-error hover:bg-error-container/30 transition-colors"
                  >
                    <LogOut className="w-4 h-4" /> Đăng xuất
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Dynamic Page Outlet */}
        <div className={cn("flex-1 flex flex-col", location.pathname === '/app/map' ? 'p-0' : 'p-4 sm:p-6 md:p-8')}>
          <Outlet />
        </div>
      </main>

      {/* ── Mobile Bottom Navigation Bar (Dưới 768px) ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-outline-variant flex justify-around items-center px-1 py-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to || (item.to !== '/app' && location.pathname.startsWith(item.to))

          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                'flex flex-col items-center justify-center py-1 px-1.5 rounded-2xl transition-all',
                isActive
                  ? 'text-primary font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              )}
            >
              <div className={cn(
                'p-1 rounded-full transition-colors',
                isActive ? 'bg-primary-container text-on-primary-container' : ''
              )}>
                <item.icon className="w-5 h-5" />
              </div>
              <span className="text-[11px] mt-0.5">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

