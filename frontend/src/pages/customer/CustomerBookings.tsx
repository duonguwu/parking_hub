import { useState, useEffect } from 'react'
import { Calendar, Search, Filter, History, Clock, BadgeCheck, XCircle, ChevronRight, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { customerApi, type Booking, BOOKING_STATUS_MAP } from '@/services/api'
import { Link } from 'react-router-dom'

function statusBadge(status: string) {
  const { label, color } = BOOKING_STATUS_MAP[status] ?? { label: status, color: 'gray' }
  const base = 'text-[9px] uppercase tracking-widest font-black border-none px-2 py-0.5'
  if (color === 'blue') return <Badge className={`${base} bg-blue-100 text-blue-700 hover:bg-blue-100 border border-blue-200`}><Clock className="w-3 h-3 mr-1" />{label}</Badge>
  if (color === 'green') return <Badge className={`${base} bg-emerald-100 text-emerald-700 hover:bg-emerald-100 border border-emerald-200`}><BadgeCheck className="w-3 h-3 mr-1" />{label}</Badge>
  if (color === 'red') return <Badge className={`${base} bg-rose-100 text-rose-700 hover:bg-rose-100 border border-rose-200`}><XCircle className="w-3 h-3 mr-1" />{label}</Badge>
  return <Badge className={`${base} bg-slate-100 text-slate-600 hover:bg-slate-100 border border-slate-200`}>{label}</Badge>
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
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pt-6 px-6">

      {/* Header */}
      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-bold uppercase tracking-widest mb-3 border border-slate-200">
              <History className="w-3.5 h-3.5" /> Lịch sử dịch vụ
            </span>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Lịch hẹn</h1>
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative group min-w-[280px]">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full bg-slate-50 border-2 border-slate-100 text-slate-900 text-sm rounded-2xl block pl-12 p-3.5 outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all font-semibold placeholder:font-medium placeholder:text-slate-400"
                placeholder="Tìm theo mã hoặc dịch vụ..."
              />
            </div>
            <button
              onClick={() => setFilterActive(!filterActive)}
              className={`border-2 rounded-2xl px-5 flex items-center justify-center gap-2 transition-colors font-bold h-[52px] ${filterActive ? 'bg-blue-600 text-white border-blue-600' : 'bg-white border-slate-200 hover:border-slate-300 text-slate-600'}`}
            >
              <Filter className="w-5 h-5" />
              <span className="hidden sm:inline">Đang diễn ra</span>
            </button>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-slate-400 font-medium">Không có lịch hẹn nào.</div>
        ) : filtered.map(booking => (
          <Link key={booking.id} to={`/app/bookings/${booking.id}`}>
            <Card className="p-6 rounded-3xl border-slate-200 hover:border-blue-200 shadow-sm hover:shadow-md transition-all duration-300 bg-white group cursor-pointer mb-4">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">

                {/* Status & Date */}
                <div className="md:col-span-3 flex flex-col gap-2">
                  <div className="mb-1">{statusBadge(booking.status)}</div>
                  <div className="flex items-center gap-2 text-slate-600">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm font-bold">
                      {new Date(booking.requested_time).toLocaleDateString('vi-VN', { day:'2-digit', month:'short', year:'numeric' })}
                    </span>
                  </div>
                </div>

                {/* Info */}
                <div className="md:col-span-6 flex flex-col justify-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">
                    {booking.booking_code}
                  </span>
                  <h3 className="text-lg font-black text-slate-900 group-hover:text-blue-600 transition-colors mb-2 capitalize">
                    {booking.service_type_code.replace(/_/g, ' ')}
                  </h3>
                </div>

                {/* Price */}
                <div className="md:col-span-3 flex justify-between md:justify-end items-center gap-6 border-t md:border-t-0 pt-4 md:pt-0 border-slate-100">
                  <span className="text-xl font-black text-slate-900 tracking-tight">
                    {booking.price.toLocaleString('vi-VN')}đ
                  </span>
                  <button className="w-10 h-10 rounded-full bg-slate-50 hover:bg-blue-50 text-slate-400 hover:text-blue-600 flex items-center justify-center transition-colors">
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
