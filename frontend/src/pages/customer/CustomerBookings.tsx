import { useState, useEffect } from 'react'
import { Calendar, Search, Filter, History, Clock, BadgeCheck, XCircle, ChevronRight, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { customerApi, type Booking, BOOKING_STATUS_MAP } from '@/services/api'
import { Link } from 'react-router-dom'

function statusBadge(status: string) {
  const { label, color } = BOOKING_STATUS_MAP[status] ?? { label: status, color: 'gray' }
  const base = 'text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full'
  if (color === 'blue') return <Badge className={`${base} bg-primary-container text-on-primary-container`}><Clock className="w-3 h-3 mr-1" />{label}</Badge>
  if (color === 'green') return <Badge className={`${base} bg-success-soft text-success`}><BadgeCheck className="w-3 h-3 mr-1" />{label}</Badge>
  if (color === 'red') return <Badge className={`${base} bg-error-container text-error`}><XCircle className="w-3 h-3 mr-1" />{label}</Badge>
  return <Badge className={`${base} bg-surface-container text-on-surface-variant`}>{label}</Badge>
}

const ACTIVE_STATUSES = ['pending', 'confirmed', 'customer_arriving', 'customer_arrived', 'in_service']

export function CustomerBookings() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterActive, setFilterActive] = useState(false)

  useEffect(() => {
    customerApi.bookings().then(setBookings).catch(console.error).finally(() => setLoading(false))
  }, [])

  const filtered = bookings.filter(b => {
    if (filterActive && !ACTIVE_STATUSES.includes(b.status)) return false
    if (search && !b.booking_code.toLowerCase().includes(search.toLowerCase()) &&
        !b.service_type_code.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">

      {/* Header */}
      <div className="bg-surface rounded-3xl p-5 sm:p-6 border border-outline-variant">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-surface-container-low text-on-surface-variant rounded-full text-[10px] font-bold uppercase tracking-wider mb-2 border border-outline-variant">
              <History className="w-3 h-3" /> Quản lý lượt đặt
            </span>
            <h1 className="text-xl sm:text-2xl font-black text-on-surface tracking-tight">Lịch hẹn gửi xe</h1>
          </div>

          <div className="flex flex-col sm:flex-row gap-2.5 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-outline" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full bg-surface-container-low border border-outline-variant text-on-surface text-xs rounded-full pl-9 pr-4 py-2.5 outline-none focus:border-primary transition-colors placeholder:text-outline"
                placeholder="Tìm theo mã hoặc dịch vụ..."
              />
            </div>
            <button
              onClick={() => setFilterActive(!filterActive)}
              className={`rounded-full px-4 py-2.5 flex items-center justify-center gap-1.5 transition-colors font-bold text-xs shrink-0 ${
                filterActive
                  ? 'bg-primary text-white'
                  : 'bg-surface border border-outline-variant hover:border-primary text-on-surface-variant'
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>Đang hoạt động</span>
            </button>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant text-xs font-medium bg-surface rounded-3xl border border-outline-variant">
            Chưa có lịch hẹn nào.
          </div>
        ) : filtered.map(booking => (
          <Link key={booking.id} to={`/app/bookings/${booking.id}`} className="block group">
            <Card className="p-4 sm:p-5 rounded-3xl border border-outline-variant bg-surface hover:border-primary/50 transition-all">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                {/* Status & Code */}
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {statusBadge(booking.status)}
                    <span className="text-[11px] font-bold text-on-surface-variant">
                      #{booking.booking_code}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-on-surface group-hover:text-primary transition-colors capitalize">
                    {booking.service_type_code.replace(/_/g, ' ')}
                  </h3>
                  <div className="flex items-center gap-1.5 text-xs text-on-surface-variant">
                    <Calendar className="w-3.5 h-3.5 text-outline" />
                    <span>
                      {new Date(booking.requested_time).toLocaleDateString('vi-VN', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })}
                    </span>
                  </div>
                </div>

                {/* Price & Action */}
                <div className="flex justify-between sm:justify-end items-center gap-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-outline-variant/50">
                  <div className="text-left sm:text-right">
                    <span className="text-[10px] font-bold text-on-surface-variant uppercase block">Tổng phí</span>
                    <span className="text-base font-black text-primary">
                      {booking.price.toLocaleString('vi-VN')} đ
                    </span>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-surface-container-low group-hover:bg-primary group-hover:text-white text-on-surface-variant flex items-center justify-center transition-colors">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

