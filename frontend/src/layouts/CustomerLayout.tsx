import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { MapPin, Calendar, Search, CarFront, Settings, HelpCircle, Plus, Bell, ChevronDown, LogOut } from 'lucide-react'
import { cn } from '@/services/utils'
import { useAuth } from '@/services/auth-context'
import { useState } from 'react'

const navItems = [
  { to: '/app', icon: Search, label: 'Discover' },
  { to: '/app/map', icon: MapPin, label: 'Map View' },
  { to: '/app/garages/1', icon: Settings, label: 'Garage Details' },
  { to: '/app/bookings', icon: Calendar, label: 'My Bookings' },
  { to: '/app/vehicles', icon: CarFront, label: 'My Vehicles' },
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

  return (
    <div className="flex min-h-screen bg-[#F8FAFC] relative selection:bg-blue-100">
      {/* ── Left Sidebar (Desktop Web) ── */}
      <aside className="fixed left-0 top-0 h-screen w-[280px] flex flex-col pt-10 pb-8 z-40 bg-white border-r border-slate-200 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        {/* Branding */}
        <div className="px-8 mb-12 flex flex-col items-start">
          <img
            src="/washmind_logo_ngang.png"
            alt="WashMind"
            className="h-14 w-auto mb-3"
          />
          <Badge text="Technical Coordinator" />
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-2 px-4">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to || (item.to !== '/app' && location.pathname.startsWith(item.to))

            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  'px-4 py-3.5 flex items-center gap-4 rounded-2xl transition-all duration-300 font-medium group relative overflow-hidden',
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-blue-600'
                )}
              >
                <item.icon className={cn('w-[22px] h-[22px]', isActive ? 'text-white' : 'text-slate-400 group-hover:text-blue-500')} />
                <span className="text-[14px]">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Bottom Actions */}
        <div className="px-6 mt-auto space-y-6">
          <Link to="/app/bookings" className="block">
            <button className="w-full bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white py-4 px-6 rounded-2xl text-[13px] font-bold tracking-wide transition-all duration-300 flex items-center justify-center gap-2 shadow-sm border border-blue-100">
              <Plus className="w-5 h-5" />
              NEW BOOKING
            </button>
          </Link>
          <div className="space-y-1 pt-6 px-2 border-t border-slate-100">
            <Link to="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-900 transition-colors py-2 px-2 rounded-lg">
              <Settings className="w-5 h-5 text-slate-400" />
              <span className="text-[14px] font-medium">Settings</span>
            </Link>
            <Link to="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-900 transition-colors py-2 px-2 rounded-lg">
              <HelpCircle className="w-5 h-5 text-slate-400" />
              <span className="text-[14px] font-medium">Support</span>
            </Link>
          </div>
        </div>
      </aside>

      {/* ── Main Content Area ── */}
      <main className="ml-[280px] flex-1 relative min-h-screen flex flex-col">
        {/* ── Global Top Header ── */}
        <header className="h-[88px] bg-white/80 backdrop-blur-xl border-b border-slate-200 sticky top-0 z-30 px-10 flex items-center justify-between shadow-[0_4px_24px_rgba(0,0,0,0.02)]">

          <div className="flex-1 max-w-xl relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search locations, bookings, or vehicles..."
              className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-full pl-12 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-shadow"
            />
          </div>

          <div className="flex items-center gap-6 ml-8">
            <button className="relative p-2.5 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
              <Bell className="w-6 h-6" />
              <div className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
            </button>
            <div className="h-8 w-[1px] bg-slate-200" />
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="flex items-center gap-3 hover:bg-slate-50 p-1.5 pr-3 rounded-full transition-colors border border-transparent hover:border-slate-200"
              >
                <img
                  src={`https://api.dicebear.com/7.x/notionists/svg?seed=${user?.username ?? 'user'}`}
                  alt={user?.name ?? 'User'}
                  className="w-10 h-10 rounded-full border border-slate-200 bg-white object-cover"
                />
                <div className="text-left hidden sm:block">
                  <p className="text-[13px] font-bold text-slate-900 leading-tight">{user?.name ?? '—'}</p>
                  <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Elite Member</p>
                </div>
                <ChevronDown className="w-4 h-4 text-slate-400 ml-1 hidden sm:block" />
              </button>
              {showMenu && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 overflow-hidden">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-5 py-3.5 text-sm font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" /> Đăng xuất
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className={cn("flex-1 flex flex-col", location.pathname === '/app/map' ? 'p-0' : 'p-6 md:p-10')}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function Badge({ text }: { text: string }) {
  return (
    <div className="bg-slate-100 border border-slate-200 text-slate-500 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md">
      {text}
    </div>
  )
}
