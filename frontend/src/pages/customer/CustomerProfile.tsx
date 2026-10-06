import { Link, useNavigate } from 'react-router-dom'
import { CarFront, Calendar, LogOut, ChevronRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { useAuth } from '@/services/auth-context'
import { ROLE_LABEL } from '@/services/api'

export function CustomerProfile() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const initial = (user?.name || user?.username || '?').trim().charAt(0).toUpperCase()

  return (
    <div className="max-w-xl mx-auto w-full space-y-4">
      <Card className="p-5 rounded-2xl flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-primary text-white flex items-center justify-center text-xl font-black">{initial}</div>
        <div className="min-w-0">
          <p className="text-lg font-black text-on-surface truncate">{user?.name || 'Chưa đặt tên'}</p>
          <p className="text-xs text-on-surface-variant">@{user?.username}</p>
          <p className="text-[11px] text-on-surface-variant">{ROLE_LABEL[user?.role ?? ''] ?? user?.role}</p>
        </div>
      </Card>
      <Card className="p-0 rounded-2xl divide-y divide-outline-variant overflow-hidden">
        {[{ to: '/app/vehicles', icon: CarFront, label: 'Xe của tôi' }, { to: '/app/bookings', icon: Calendar, label: 'Lượt đặt của tôi' }].map((i) => (
          <Link key={i.to} to={i.to} className="flex items-center gap-3 p-4 hover:bg-surface-container-low">
            <i.icon className="w-5 h-5 text-primary" /><span className="flex-1 text-sm font-semibold">{i.label}</span><ChevronRight className="w-4 h-4 text-outline" />
          </Link>
        ))}
      </Card>
      <button onClick={async () => { await logout(); navigate('/login') }}
        className="w-full h-11 rounded-full border border-error text-error text-sm font-bold flex items-center justify-center gap-2">
        <LogOut className="w-4 h-4" /> Đăng xuất
      </button>
    </div>
  )
}
