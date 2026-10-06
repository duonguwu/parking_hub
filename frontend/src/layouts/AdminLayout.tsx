import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Map, ParkingSquare, Users, Settings2, LogOut } from 'lucide-react'
import { useAuth } from '@/services/auth-context'
import { ROLE_LABEL } from '@/services/api'
import { Brand } from '@/components/Brand'
import { cn } from '@/services/utils'

const navItems = [
  { name: 'Tổng quan', path: '/admin', icon: LayoutDashboard },
  { name: 'Bản đồ', path: '/admin/map', icon: Map },
  { name: 'Bãi đỗ', path: '/admin/garages', icon: ParkingSquare },
  { name: 'Người dùng', path: '/admin/users', icon: Users },
  { name: 'Dịch vụ', path: '/admin/services', icon: Settings2 },
]

export function AdminLayout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const isActive = (p: string) => (p === '/admin' ? location.pathname === p : location.pathname.startsWith(p))
  const initial = user?.name ? user.name.trim().charAt(0).toUpperCase() : 'A'
  const onLogout = async () => { await logout(); navigate('/login') }

  return (
    <div className="min-h-screen bg-background text-on-surface">
      <aside className="hidden md:block fixed left-0 top-0 h-screen w-64 bg-surface border-r border-outline-variant z-50 overflow-y-auto">
        <div className="flex flex-col gap-y-2 p-6 h-full text-sm font-medium">
          <div className="mb-6 px-3">
            <Brand />
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-1">Quản trị mạng lưới</p>
          </div>
          <nav className="flex flex-col gap-y-1.5">
            {navItems.map(({ name, path, icon: Icon }) => (
              <Link key={path} to={path} className={cn('px-4 py-2.5 rounded-full transition-all flex items-center gap-3',
                isActive(path) ? 'bg-primary text-white font-semibold' : 'text-on-surface-variant hover:bg-surface-container-low hover:text-primary')}>
                <Icon className="w-5 h-5 shrink-0" /><span>{name}</span>
              </Link>
            ))}
          </nav>
          <div className="mt-auto border-t border-outline-variant pt-4">
            <button onClick={onLogout} className="w-full px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-error rounded-full flex items-center gap-3">
              <LogOut className="w-4 h-4" /> Đăng xuất
            </button>
          </div>
        </div>
      </aside>

      <header className="fixed top-0 left-0 md:left-64 right-0 h-16 flex items-center px-4 md:px-8 bg-surface/90 backdrop-blur-md border-b border-outline-variant z-40">
        <div className="flex md:hidden"><Brand className="text-base" /></div>
        <div className="flex items-center gap-3 ml-auto">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-bold">{user?.name || 'Quản trị viên'}</p>
            <p className="text-[10px] uppercase tracking-wider text-on-surface-variant">{ROLE_LABEL[user?.role ?? ''] ?? user?.role ?? ''}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-xs">{initial}</div>
          <button onClick={onLogout} title="Đăng xuất" className="md:hidden p-2 text-on-surface-variant hover:text-error rounded-full"><LogOut className="w-5 h-5" /></button>
        </div>
      </header>

      <main className="ml-0 md:ml-64 pt-16 min-h-screen pb-20 md:pb-0"><Outlet /></main>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-outline-variant flex justify-around items-center px-1 py-2">
        {navItems.map(({ name, path, icon: Icon }) => (
          <Link key={path} to={path} className={cn('flex flex-col items-center py-1 px-2 rounded-2xl',
            isActive(path) ? 'text-primary font-bold' : 'text-on-surface-variant')}>
            <div className={cn('p-1 rounded-full', isActive(path) && 'bg-primary-container text-on-primary-container')}><Icon className="w-5 h-5" /></div>
            <span className="text-[10px] mt-0.5 whitespace-nowrap">{name}</span>
          </Link>
        ))}
      </nav>
    </div>
  )
}
