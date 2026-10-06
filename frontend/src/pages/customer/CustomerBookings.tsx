import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { customerApi, formatVnd, formatDateTime, ACTIVE_BOOKING_STATUSES, type Booking } from '@/services/api'
import { BookingStatusBadge, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

export function CustomerBookings() {
  const [items, setItems] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<'active' | 'history'>('active')

  useEffect(() => {
    customerApi.bookings().then(setItems).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [])

  const active = items.filter((b) => ACTIVE_BOOKING_STATUSES.includes(b.status))
  const history = items.filter((b) => !ACTIVE_BOOKING_STATUSES.includes(b.status))
  const list = tab === 'active' ? active : history

  return (
    <div className="max-w-3xl mx-auto w-full space-y-4">
      <h1 className="text-xl font-black text-on-surface">Lượt đặt của tôi</h1>
      <div className="flex gap-1 bg-surface-container-low rounded-full p-1">
        {([['active', `Đang hoạt động (${active.length})`], ['history', `Lịch sử (${history.length})`]] as const).map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)} className={cn('flex-1 py-2 rounded-full text-xs font-bold',
            tab === k ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant')}>{l}</button>
        ))}
      </div>
      {loading ? <Spinner /> : error ? <EmptyState title="Không tải được lượt đặt" desc={error} />
        : list.length === 0 ? <EmptyState title={tab === 'active' ? 'Không có lượt đặt đang hoạt động' : 'Chưa có lịch sử gửi xe'} />
        : (
          <div className="space-y-2">
            {list.map((b) => (
              <Link key={b.id} to={`/app/bookings/${b.id}`} className="flex items-center gap-3 p-3 rounded-2xl bg-surface border border-outline-variant hover:border-primary/50">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-on-surface truncate">{b.garage_name || 'Bãi đỗ'}</p>
                    <BookingStatusBadge status={b.status} />
                  </div>
                  <p className="text-[11px] text-on-surface-variant">{b.license_plate}{b.service_name ? ` · ${b.service_name}` : ''}</p>
                  <p className="text-[11px] text-on-surface-variant">{formatDateTime(b.start_time)} – {formatDateTime(b.end_time)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-on-surface">{formatVnd(b.final_price ?? b.quoted_price)}</p>
                  <p className="text-[10px] text-on-surface-variant">{b.final_price != null ? 'Thực trả' : 'Tạm tính'}</p>
                </div>
                <ChevronRight className="w-4 h-4 text-outline" />
              </Link>
            ))}
          </div>
        )}
    </div>
  )
}
