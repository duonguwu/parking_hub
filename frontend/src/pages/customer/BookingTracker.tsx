import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, CheckCircle2, Circle, Clock, Loader2, MapPin } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type BookingTracking, BOOKING_STATUS_MAP } from '@/services/api'

const TIMELINE_STEPS = [
  { key: 'CREATED',             label: 'Đã đặt lịch',        desc: 'Hệ thống ghi nhận yêu cầu' },
  { key: 'CONFIRMED',           label: 'Cửa hàng xác nhận',  desc: 'Gara đã chấp nhận lịch hẹn' },
  { key: 'CUSTOMER_DEPARTING',  label: 'Đang trên đường',     desc: 'Khách hàng đang di chuyển đến' },
  { key: 'CUSTOMER_ARRIVED',    label: 'Đã đến nơi',          desc: 'Khách hàng đã check-in tại gara' },
  { key: 'IN_SERVICE',          label: 'Đang thực hiện',      desc: 'Kỹ thuật viên đang rửa xe' },
  { key: 'COMPLETED',           label: 'Hoàn tất',            desc: 'Dịch vụ đã hoàn thành' },
]

export function CustomerBookingTracker() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<BookingTracking | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    const load = () =>
      customerApi.bookingTracking(id)
        .then(setData)
        .catch(() => setError('Không thể tải thông tin theo dõi'))
        .finally(() => setLoading(false))
    load()
    // Poll every 10s if in-service
    const interval = setInterval(() => {
      if (data?.booking?.status && ['confirmed','customer_arriving','in_service'].includes(data.booking.status)) {
        load()
      }
    }, 10000)
    return () => clearInterval(interval)
  }, [id])

  const doneStatuses = new Set((data?.timeline ?? []).map(t => t.status))
  const currentIdx = Math.max(...TIMELINE_STEPS.map((s, i) => doneStatuses.has(s.key) ? i : -1))

  if (loading) return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
    </div>
  )

  if (error || !data) return (
    <div className="text-center py-16 text-slate-500">{error || 'Không tìm thấy lịch hẹn'}</div>
  )

  const { booking, timeline } = data
  const statusMeta = BOOKING_STATUS_MAP[booking.status] ?? { label: booking.status, color: 'gray' }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 px-6 pt-6 pb-24">

      {/* Back */}
      <Link to="/app/bookings" className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-blue-600 transition-colors uppercase tracking-widest group">
        <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        Danh sách lịch hẹn
      </Link>

      {/* Booking Summary Card */}
      <Card className="p-8 rounded-3xl border border-slate-200 shadow-sm bg-white">
        <div className="flex flex-col md:flex-row justify-between gap-6">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">{booking.booking_code}</span>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight capitalize mb-3">
              {booking.service_type_code.replace(/_/g, ' ')}
            </h1>
            <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-bold uppercase tracking-widest border ${statusMeta.color === 'blue' ? 'bg-blue-50 text-blue-700 border-blue-200' : statusMeta.color === 'green' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : statusMeta.color === 'red' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
              <span className={`w-2 h-2 rounded-full ${statusMeta.color === 'blue' ? 'bg-blue-500 animate-pulse' : statusMeta.color === 'green' ? 'bg-emerald-500' : 'bg-slate-400'}`} />
              {statusMeta.label}
            </span>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Tổng tiền</p>
            <p className="text-4xl font-black text-slate-900 tracking-tight">{booking.price.toLocaleString('vi-VN')}đ</p>
          </div>
        </div>
      </Card>

      {/* Timeline */}
      <Card className="p-8 rounded-3xl border border-slate-200 shadow-sm bg-white">
        <div className="flex items-center gap-3 mb-8">
          <Clock className="text-blue-500 w-5 h-5" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest">Tiến trình dịch vụ</h3>
        </div>

        <div className="space-y-0">
          {TIMELINE_STEPS.map((step, idx) => {
            const done = doneStatuses.has(step.key)
            const isCurrent = idx === currentIdx && done
            const timelineItem = timeline.find(t => t.status === step.key)
            const isLast = idx === TIMELINE_STEPS.length - 1

            return (
              <div key={step.key} className="flex gap-6">
                {/* Line + icon */}
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-all duration-500 ${done ? (isCurrent ? 'bg-blue-600 shadow-lg shadow-blue-600/30' : 'bg-emerald-500') : 'bg-slate-100 border-2 border-slate-200'}`}>
                    {done
                      ? <CheckCircle2 className={`w-5 h-5 ${isCurrent ? 'text-white' : 'text-white'}`} />
                      : <Circle className="w-5 h-5 text-slate-300" />
                    }
                  </div>
                  {!isLast && <div className={`w-0.5 flex-1 my-1 min-h-[32px] ${done ? 'bg-emerald-200' : 'bg-slate-100'}`} />}
                </div>

                {/* Content */}
                <div className={`pb-6 ${isLast ? '' : ''}`}>
                  <p className={`font-bold text-base ${done ? 'text-slate-900' : 'text-slate-400'}`}>{step.label}</p>
                  <p className="text-xs font-medium text-slate-500 mt-0.5">{timelineItem?.description ?? step.desc}</p>
                  {timelineItem?.timestamp && (
                    <p className="text-[10px] font-bold text-blue-500 mt-1 uppercase tracking-wider">
                      {new Date(timelineItem.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

    </div>
  )
}
