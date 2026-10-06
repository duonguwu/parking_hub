import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, CheckCircle2, Circle, Clock, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type BookingTracking, BOOKING_STATUS_MAP } from '@/services/api'

const TIMELINE_STEPS = [
  { key: 'CREATED',             label: 'Đã đặt chỗ',        desc: 'Hệ thống đã ghi nhận yêu cầu giữ chỗ' },
  { key: 'CONFIRMED',           label: 'Bãi đỗ xác nhận',   desc: 'Bãi đỗ đã giữ vị trí đỗ cho bạn' },
  { key: 'CUSTOMER_DEPARTING',  label: 'Đang di chuyển',    desc: 'Đang lái xe đến bãi đỗ' },
  { key: 'CUSTOMER_ARRIVED',    label: 'Đã đến cổng bãi',   desc: 'Hệ thống nhận diện biển số tại cổng vào' },
  { key: 'IN_SERVICE',          label: 'Đang gửi xe',       desc: 'Xe đang đỗ an toàn trong bãi' },
  { key: 'COMPLETED',           label: 'Hoàn tất lượt gửi', desc: 'Đã check-out và thanh toán thành công' },
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
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
    </div>
  )

  if (error || !data) return (
    <div className="text-center py-16 text-on-surface-variant">{error || 'Không tìm thấy lượt đặt chỗ'}</div>
  )

  const { booking, timeline } = data
  const statusMeta = BOOKING_STATUS_MAP[booking.status] ?? { label: booking.status, color: 'gray' }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">

      {/* Back Button */}
      <Link to="/app/bookings" className="inline-flex items-center gap-1.5 text-xs font-bold text-on-surface-variant hover:text-primary transition-colors uppercase tracking-wider group">
        <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        <span>Danh sách lịch hẹn</span>
      </Link>

      {/* Booking Summary Card */}
      <Card className="p-5 sm:p-6 rounded-3xl border border-outline-variant bg-surface">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
          <div>
            <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block mb-1">
              Mã đặt chỗ: #{booking.booking_code}
            </span>
            <h1 className="text-xl sm:text-2xl font-black text-on-surface tracking-tight capitalize mb-2">
              {booking.service_type_code.replace(/_/g, ' ')}
            </h1>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
              statusMeta.color === 'blue' ? 'bg-primary-container text-on-primary-container' :
              statusMeta.color === 'green' ? 'bg-success-soft text-success' :
              statusMeta.color === 'red' ? 'bg-error-container text-error' :
              'bg-surface-container text-on-surface-variant'
            }`}>
              <span className={`w-2 h-2 rounded-full ${statusMeta.color === 'blue' ? 'bg-primary' : statusMeta.color === 'green' ? 'bg-success' : 'bg-outline'}`} />
              {statusMeta.label}
            </span>
          </div>

          <div className="sm:text-right pt-3 sm:pt-0 border-t sm:border-t-0 border-outline-variant/60">
            <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-0.5">Tổng thanh toán</p>
            <p className="text-2xl sm:text-3xl font-black text-primary">{booking.price.toLocaleString('vi-VN')} đ</p>
          </div>
        </div>
      </Card>

      {/* Timeline Tracking */}
      <Card className="p-5 sm:p-6 rounded-3xl border border-outline-variant bg-surface">
        <div className="flex items-center gap-2 mb-6">
          <Clock className="text-primary w-5 h-5" />
          <h2 className="text-sm font-bold text-on-surface uppercase tracking-wider">Tiến trình gửi xe</h2>
        </div>

        <div className="space-y-0">
          {TIMELINE_STEPS.map((step, idx) => {
            const done = doneStatuses.has(step.key)
            const isCurrent = idx === currentIdx && done
            const timelineItem = timeline.find(t => t.status === step.key)
            const isLast = idx === TIMELINE_STEPS.length - 1

            return (
              <div key={step.key} className="flex gap-4 sm:gap-6">
                {/* Line + Icon */}
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center shrink-0 transition-all ${
                    done
                      ? (isCurrent ? 'bg-primary text-white' : 'bg-success text-white')
                      : 'bg-surface-container-low border border-outline-variant'
                  }`}>
                    {done
                      ? <CheckCircle2 className="w-4 h-4 text-white" />
                      : <Circle className="w-4 h-4 text-outline" />
                    }
                  </div>
                  {!isLast && (
                    <div className={`w-0.5 flex-1 my-1 min-h-[28px] ${done ? 'bg-success-soft' : 'bg-outline-variant'}`} />
                  )}
                </div>

                {/* Content */}
                <div className="pb-5">
                  <p className={`font-bold text-sm ${done ? 'text-on-surface' : 'text-outline'}`}>{step.label}</p>
                  <p className="text-xs text-on-surface-variant mt-0.5">{timelineItem?.description ?? step.desc}</p>
                  {timelineItem?.timestamp && (
                    <p className="text-[10px] font-bold text-primary mt-1">
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

