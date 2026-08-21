import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, CalendarDays, LineChart, Settings2, Gauge, Plus, Settings, HelpCircle, Search, Bell } from 'lucide-react'
import { useAuth } from '@/services/auth-context'
import { Brand } from '@/components/Brand'

export function GarageLayout() {
  const { user } = useAuth()
  const location = useLocation()

  const navItems = [
    { name: 'Dashboard', path: '/garage', icon: LayoutDashboard },
    { name: 'Booking Queue', path: '/garage/queue', icon: CalendarDays },
    { name: 'Analytics', path: '/garage/analytics', icon: LineChart },
    { name: 'Services', path: '/garage/services', icon: Settings2 },
    { name: 'Score', path: '/garage/score', icon: Gauge },
  ]

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-inter">
      {/* Sidebar Navigation */}
      <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-50 border-r border-slate-200 z-50 overflow-y-auto">
        <div className="flex flex-col gap-y-2 p-6 h-full text-sm font-medium tracking-wide">
          <div className="mb-8 px-4">
            <Brand />
            <p className="text-[0.6875rem] uppercase tracking-widest text-slate-500 mt-1">Cổng chủ bãi</p>
          </div>
          
          <nav className="flex flex-col gap-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2.5 rounded-full transition-all flex items-center gap-3 active:scale-95 ${
                    isActive 
                      ? 'bg-blue-100 text-blue-700 border border-blue-200 font-bold' 
                      : 'text-slate-600 hover:bg-white hover:shadow-sm'
                  }`}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          <div className="mt-8 mb-4">
            <button className="w-full bg-blue-100 text-blue-800 hover:bg-blue-200 py-3 rounded-full font-bold flex items-center justify-center gap-2 active:scale-95 transition-all">
              <Plus className="w-4 h-4" />
              New Booking
            </button>
          </div>

          <div className="mt-auto border-t border-slate-200 pt-6 flex flex-col gap-y-1">
            <Link to="/garage/settings" className="px-4 py-2.5 text-slate-600 hover:bg-white hover:shadow-sm rounded-full flex items-center gap-3 active:scale-95">
              <Settings className="w-5 h-5" /> Settings
            </Link>
            <Link to="/support" className="px-4 py-2.5 text-slate-600 hover:bg-white hover:shadow-sm rounded-full flex items-center gap-3 active:scale-95">
              <HelpCircle className="w-5 h-5" /> Support
            </Link>
          </div>
        </div>
      </aside>

      {/* Top Navigation Bar */}
      <header className="fixed top-0 left-64 right-0 h-16 flex justify-between items-center px-8 bg-white/80 backdrop-blur-md border-b border-slate-200 z-40">
        <div className="flex items-center gap-4 bg-slate-50 px-4 py-2 rounded-full border border-slate-200 w-96 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
          <Search className="w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search cars, bookings, or owners..." 
            className="bg-transparent border-none focus:ring-0 text-sm outline-none w-full"
          />
        </div>

        <div className="flex items-center gap-6">
          <button className="relative text-slate-500 hover:text-blue-600 transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-rose-500 border border-white rounded-full"></span>
          </button>
          <button className="text-slate-500 hover:text-blue-600 transition-colors">
            <HelpCircle className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-3 ml-4">
            <div className="text-right">
              <p className="text-xs font-bold text-slate-900">{user?.name || 'Chủ bãi'}</p>
              <p className="text-[10px] uppercase tracking-tighter text-slate-500">{user?.role ?? ''}</p>
            </div>
            <div className="w-10 h-10 rounded-full border border-slate-200 bg-slate-100 flex items-center justify-center font-bold text-slate-600 uppercase">
              {user?.name?.charAt(0) || 'P'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="ml-64 pt-16 min-h-screen">
        <Outlet />
      </main>
    </div>
  )
}
