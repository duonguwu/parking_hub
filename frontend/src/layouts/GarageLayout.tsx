import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, CalendarDays, LineChart, Settings2, Gauge, Settings, HelpCircle, Search, Bell } from 'lucide-react'
import { useAuth } from '@/services/auth-context'
import { Brand } from '@/components/Brand'
import { cn } from '@/services/utils'

export function GarageLayout() {
  const { user } = useAuth()
  const location = useLocation()

  const navItems = [
    { name: 'Tổng quan', path: '/garage', icon: LayoutDashboard },
    { name: 'Hàng đợi', path: '/garage/queue', icon: CalendarDays },
    { name: 'Phân tích', path: '/garage/analytics', icon: LineChart },
    { name: 'Dịch vụ', path: '/garage/services', icon: Settings2 },
    { name: 'Điểm số', path: '/garage/score', icon: Gauge },
  ]

  const userInitial = user?.name ? user.name.trim().charAt(0).toUpperCase() : 'P'

  return (
    <div className="min-h-screen bg-background text-on-surface">
      {/* ── Sidebar Navigation (Desktop: md và lớn hơn) ── */}
      <aside className="hidden md:block fixed left-0 top-0 h-screen w-64 bg-surface border-r border-outline-variant z-50 overflow-y-auto">
        <div className="flex flex-col gap-y-2 p-6 h-full text-sm font-medium tracking-wide">
          <div className="mb-6 px-3">
            <Brand />
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-1">Cổng chủ bãi</p>
          </div>
          
          <nav className="flex flex-col gap-y-1.5">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'px-4 py-2.5 rounded-full transition-all flex items-center gap-3',
                    isActive 
                      ? 'bg-primary text-white font-semibold' 
                      : 'text-on-surface-variant hover:bg-surface-container-low hover:text-primary'
                  )}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>

          <div className="mt-auto border-t border-outline-variant pt-4 flex flex-col gap-y-1">
            <Link to="#" className="px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface rounded-full flex items-center gap-3">
              <Settings className="w-4 h-4 text-outline" /> Cài đặt
            </Link>
            <Link to="#" className="px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface rounded-full flex items-center gap-3">
              <HelpCircle className="w-4 h-4 text-outline" /> Hỗ trợ
            </Link>
          </div>
        </div>
      </aside>

      {/* ── Top Navigation Bar ── */}
      <header className="fixed top-0 left-0 md:left-64 right-0 h-16 flex justify-between items-center px-4 md:px-8 bg-surface/90 backdrop-blur-md border-b border-outline-variant z-40">
        {/* Mobile Logo */}
        <div className="flex md:hidden items-center gap-2">
          <Brand className="text-base" />
        </div>

        {/* Search Bar (Desktop) */}
        <div className="hidden sm:flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-full border border-outline-variant w-72 md:w-96">
          <Search className="w-4 h-4 text-outline" />
          <input 
            type="text" 
            placeholder="Tìm biển số xe, lượt đặt..." 
            className="bg-transparent border-none focus:ring-0 text-xs outline-none w-full text-on-surface placeholder:text-outline"
          />
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-3 md:gap-4 ml-auto">
          <button className="relative p-2 text-on-surface-variant hover:bg-surface-container-low rounded-full transition-colors" title="Thông báo">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full" />
          </button>
          
          <div className="h-6 w-px bg-outline-variant" />

          <div className="flex items-center gap-2.5">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-on-surface">{user?.name || 'Chủ bãi'}</p>
              <p className="text-[10px] uppercase tracking-wider text-on-surface-variant">{user?.role ?? ''}</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-xs">
              {userInitial}
            </div>
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="ml-0 md:ml-64 pt-16 min-h-screen pb-20 md:pb-0">
        <Outlet />
      </main>

      {/* ── Mobile Bottom Navigation Bar (Dưới 768px) ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-outline-variant flex justify-around items-center px-1 py-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex flex-col items-center justify-center py-1 px-2.5 rounded-2xl transition-all',
                isActive
                  ? 'text-primary font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              )}
            >
              <div className={cn(
                'p-1 rounded-full transition-colors',
                isActive ? 'bg-primary-container text-on-primary-container' : ''
              )}>
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-[10px] mt-0.5 whitespace-nowrap">{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

