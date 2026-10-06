import { useEffect, useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, CalendarDays, LineChart, Settings2, Gauge, Building2, LogOut, ShieldCheck } from 'lucide-react'
import { useAuth } from '@/services/auth-context'
import { ROLE_LABEL, garageApi, activeGarage } from '@/services/api'
import { LotSwitcher, type LotOption } from '@/components/LotSwitcher'
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
  const isAdmin = user?.role === 'super_admin'
  const [lots, setLots] = useState<LotOption[]>([])
  const [ready, setReady] = useState(false)
  const [loadError, setLoadError] = useState('')

  // Xác định bãi đang thao tác trước khi render trang con (chủ nhiều bãi, hoặc admin xem như chủ bãi)
  useEffect(() => {
    garageApi.accessibleGarages()
      .then((list) => {
        setLots(list)
        const stored = activeGarage.get()
        // admin giữ bãi đã chọn dù không nằm trong 50 bãi đầu; chủ bãi chỉ giữ nếu thuộc tài khoản mình
        const valid = stored && (isAdmin || list.some((l) => l.id === stored))
        if (!valid) {
          if (list[0]) activeGarage.set(list[0].id, list[0].name)
          else activeGarage.clear()
        }
        if (!activeGarage.get()) setLoadError('Tài khoản này chưa có bãi đỗ nào.')
        setReady(true)
      })
      .catch((e) => { setLoadError(e.message || 'Không tải được danh sách bãi'); setReady(true) })
  }, [isAdmin])

  const handleLogout = async () => {
    try { await logout() } finally { activeGarage.clear(); navigate('/login') }
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
            {isAdmin && (
              <Link to="/admin" className="w-full px-4 py-2 mb-1 text-xs font-medium text-primary hover:bg-surface-container-low rounded-full flex items-center gap-3">
                <ShieldCheck className="w-4 h-4" /> Về trang quản trị
              </Link>
            )}
            <button onClick={handleLogout}
              className="w-full px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-error rounded-full flex items-center gap-3">
              <LogOut className="w-4 h-4" /> Đăng xuất
            </button>
          </div>
        </div>
      </aside>

      <header className="fixed top-0 left-0 md:left-64 right-0 h-16 flex justify-between items-center px-4 md:px-8 bg-surface/90 backdrop-blur-md border-b border-outline-variant z-40">
        <div className="flex md:hidden items-center gap-2"><Brand className="text-base" /></div>
        <div className="flex items-center gap-3 ml-auto min-w-0">
          <LotSwitcher lots={lots} searchable={isAdmin} />
          {isAdmin && <Link to="/admin" className="md:hidden p-2 text-primary rounded-full" aria-label="Về trang quản trị"><ShieldCheck className="w-5 h-5" /></Link>}
          <div className="text-right hidden sm:block">
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
        {!ready ? (
          <div className="flex items-center justify-center py-24 text-sm text-on-surface-variant">Đang tải bãi đỗ…</div>
        ) : loadError ? (
          <div className="max-w-md mx-auto py-24 px-6 text-center text-sm text-on-surface-variant">{loadError}</div>
        ) : (
          <Outlet key={activeGarage.get()} />
        )}
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
