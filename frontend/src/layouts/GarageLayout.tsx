import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, CalendarDays, LineChart, Settings2, Gauge, Building2, LogOut } from 'lucide-react'
import { useAuth } from '@/services/auth-context'
import { ROLE_LABEL } from '@/services/api'
import { Brand } from '@/components/Brand'
import { cn } from '@/services/utils'

const NAV_ITEMS = [
  { name: 'Tổng quan', short: 'Tổng quan', path: '/garage', icon: LayoutDashboard },
  { name: 'Lượt đặt & vào/ra', short: 'Lượt đặt', path: '/garage/queue', icon: CalendarDays },
  { name: 'Hồ sơ bãi', short: 'Hồ sơ', path: '/garage/profile', icon: Building2 },
  { name: 'Dịch vụ & giá', short: 'Giá', path: '/garage/services', icon: Settings2 },
  { name: 'Phân tích', short: 'Phân tích', path: '/garage/analytics', icon: LineChart },
  { name: 'Chất lượng', short: 'Chất lượng', path: '/garage/score', icon: Gauge },
]

export function GarageLayout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const userInitial = user?.name ? user.name.trim().charAt(0).toUpperCase() : 'C'

  const handleLogout = async () => {
    try { await logout() } finally { navigate('/login') }
  }

  return (
    <div className="min-h-screen bg-background text-on-surface">
      <aside className="hidden md:block fixed left-0 top-0 h-screen w-64 bg-surface border-r border-outline-variant z-50 overflow-y-auto">
        <div className="flex flex-col gap-y-2 p-6 h-full text-sm font-medium">
          <div className="mb-6 px-3">
            <Brand />
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-1">Cổng chủ bãi</p>
          </div>
          <nav className="flex flex-col gap-y-1.5">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon
              return (
                <Link key={item.path} to={item.path}
                  className={cn('px-4 py-2.5 rounded-full transition-all flex items-center gap-3',
                    isActive ? 'bg-primary text-white font-semibold' : 'text-on-surface-variant hover:bg-surface-container-low hover:text-primary')}>
                  <Icon className="w-5 h-5 shrink-0" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>
          <div className="mt-auto border-t border-outline-variant pt-4">
            <button onClick={handleLogout}
              className="w-full px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-error rounded-full flex items-center gap-3">
              <LogOut className="w-4 h-4" /> Đăng xuất
            </button>
          </div>
        </div>
      </aside>

      <header className="fixed top-0 left-0 md:left-64 right-0 h-16 flex justify-between items-center px-4 md:px-8 bg-surface/90 backdrop-blur-md border-b border-outline-variant z-40">
        <div className="flex md:hidden items-center gap-2"><Brand className="text-base" /></div>
        <div className="flex items-center gap-3 ml-auto">
          <div className="text-right">
            <p className="text-xs font-bold text-on-surface">{user?.name || 'Chủ bãi'}</p>
            <p className="text-[10px] text-on-surface-variant">{user ? ROLE_LABEL[user.role] ?? user.role : ''}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs">{userInitial}</div>
          <button onClick={handleLogout} title="Đăng xuất" aria-label="Đăng xuất"
            className="md:hidden p-2 text-on-surface-variant hover:text-error rounded-full">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <main className="ml-0 md:ml-64 pt-16 min-h-screen pb-20 md:pb-0">
        <Outlet />
      </main>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-outline-variant grid grid-cols-6 px-1 py-1.5">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon
          return (
            <Link key={item.path} to={item.path}
              className={cn('flex flex-col items-center justify-center py-1 min-w-0',
                isActive ? 'text-primary font-bold' : 'text-on-surface-variant')}>
              <div className={cn('p-1 rounded-full', isActive && 'bg-primary/10')}><Icon className="w-5 h-5" /></div>
              <span className="text-[9px] mt-0.5 truncate max-w-full">{item.short}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
