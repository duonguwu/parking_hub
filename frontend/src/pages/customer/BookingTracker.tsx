import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Loader2, Star, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, formatVnd, formatDateTime, formatTime, type BookingTracking } from '@/services/api'
import { BookingStatusBadge, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="flex justify-between gap-3 text-sm py-1.5"><span className="text-on-surface-variant">{label}</span><span className="font-semibold text-on-surface text-right">{value}</span></div>
}

export function CustomerBookingTracker() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<BookingTracking | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [confirmCancel, setConfirmCancel] = useState(false)
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [actionErr, setActionErr] = useState('')
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')

  const load = () => id && customerApi.bookingTracking(id).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false))
  useEffect(() => { load() }, [id])

  if (loading) return <Spinner />
  if (error || !data) return <EmptyState title="Không tải được lượt đặt" desc={error} />
  const b = data.booking

  const run = async (fn: () => Promise<unknown>) => {
    setBusy(true); setActionErr('')
    try { await fn(); await load(); setConfirmCancel(false) } catch (e: any) { setActionErr(e.message) } finally { setBusy(false) }
  }

  return (
    <div className="max-w-2xl mx-auto w-full space-y-4 pb-8">
      <div className="flex items-center gap-3">
        <Link to="/app/bookings" className="p-2 rounded-full border border-outline-variant bg-surface"><ChevronLeft className="w-5 h-5" /></Link>
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-black text-on-surface truncate">{b.garage_name || 'Lượt đặt'}</h1>
          <p className="text-[11px] text-on-surface-variant">Mã {b.booking_code}</p>
        </div>
        <BookingStatusBadge status={b.status} />
      </div>

      {b.status === 'reserved' && b.grace_until && (
        <p className="text-sm bg-primary/10 text-primary rounded-2xl p-3 flex gap-2"><Clock className="w-4 h-4 shrink-0 mt-0.5" /> Bãi giữ chỗ đến {formatTime(b.grace_until)}</p>
      )}
      {b.status === 'pending' && <p className="text-sm bg-warning/10 text-warning rounded-2xl p-3">Đang chờ bãi xác nhận yêu cầu của bạn.</p>}

      <Card className="p-4 rounded-2xl divide-y divide-outline-variant">
        {b.garage_address && <Row label="Địa chỉ" value={b.garage_address} />}
        <Row label="Biển số" value={b.license_plate || '—'} />
        {b.service_name && <Row label="Dịch vụ" value={b.service_name} />}
        <Row label="Thời gian" value={`${formatDateTime(b.start_time)} – ${formatDateTime(b.end_time)}`} />
        <Row label="Tạm tính" value={formatVnd(b.quoted_price)} />
        {b.status === 'checked_out' && <>
          <Row label="Thực trả" value={<span className="text-primary">{formatVnd(b.final_price)}</span>} />
          <Row label="Thanh toán" value={b.payment_status === 'paid' ? 'Đã thanh toán' : 'Chưa thanh toán'} />
        </>}
        {b.cancellation_reason && <Row label="Lý do huỷ" value={b.cancellation_reason} />}
        {b.garage_id && <div className="pt-2"><Link to={`/app/garages/${b.garage_id}`} className="text-xs font-bold text-primary">Xem thông tin bãi →</Link></div>}
      </Card>

      <Card className="p-4 rounded-2xl">
        <h2 className="font-bold text-on-surface mb-3">Tiến trình</h2>
        {data.timeline.length === 0 ? <p className="text-xs text-on-surface-variant">Chưa có cập nhật.</p> : (
          <ol className="space-y-3">
            {data.timeline.map((t, i) => (
              <li key={i} className="flex gap-3">
                <span className={cn('mt-1 w-2.5 h-2.5 rounded-full shrink-0', i === data.timeline.length - 1 ? 'bg-primary' : 'bg-outline-variant')} />
                <div><p className="text-sm font-semibold text-on-surface">{t.description}</p><p className="text-[11px] text-on-surface-variant">{formatDateTime(t.timestamp)}</p></div>
              </li>
            ))}
          </ol>
        )}
      </Card>

      {actionErr && <p className="text-xs text-error font-semibold">{actionErr}</p>}

      {(b.status === 'pending' || b.status === 'reserved') && (
        confirmCancel ? (
          <Card className="p-4 rounded-2xl space-y-2">
            <p className="text-sm font-semibold">Bạn chắc chắn muốn huỷ lượt đặt này?</p>
            <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Lý do (không bắt buộc)"
              className="w-full h-10 rounded-xl border border-outline-variant bg-surface px-3 text-sm outline-none focus:border-primary" />
            <div className="flex gap-2">
              <button onClick={() => setConfirmCancel(false)} className="flex-1 h-10 rounded-full border border-outline-variant text-sm font-semibold">Không</button>
              <button disabled={busy} onClick={() => run(() => customerApi.cancelBooking(b.id, reason.trim()))}
                className="flex-1 h-10 rounded-full bg-error text-white text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-50">
                {busy && <Loader2 className="w-4 h-4 animate-spin" />} Huỷ lượt đặt
              </button>
            </div>
          </Card>
        ) : <button onClick={() => setConfirmCancel(true)} className="w-full h-11 rounded-full border border-error text-error text-sm font-bold">Huỷ lượt đặt</button>
      )}

      {b.status === 'checked_out' && (
        b.feedback?.rating ? (
          <Card className="p-4 rounded-2xl">
            <p className="text-sm font-semibold mb-1">Đánh giá của bạn</p>
            <div className="flex gap-0.5">{[1, 2, 3, 4, 5].map((n) => <Star key={n} className={cn('w-4 h-4', n <= (b.feedback.rating ?? 0) ? 'fill-warning text-warning' : 'text-outline-variant')} />)}</div>
            {b.feedback.comment && <p className="text-xs text-on-surface-variant mt-1">{b.feedback.comment}</p>}
          </Card>
        ) : (
          <Card className="p-4 rounded-2xl space-y-3">
            <p className="text-sm font-semibold">Đánh giá lượt gửi xe</p>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((n) => (
                <button key={n} onClick={() => setRating(n)} aria-label={`${n} sao`}>
                  <Star className={cn('w-7 h-7', n <= rating ? 'fill-warning text-warning' : 'text-outline-variant')} />
                </button>
              ))}
            </div>
            <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3} placeholder="Nhận xét (không bắt buộc)"
              className="w-full rounded-xl border border-outline-variant bg-surface p-3 text-sm outline-none focus:border-primary" />
            <button disabled={!rating || busy} onClick={() => run(() => customerApi.feedback(b.id, { rating, comment: comment.trim() || undefined }))}
              className="w-full h-10 rounded-full bg-primary text-white text-sm font-bold disabled:opacity-50 flex items-center justify-center gap-2">
              {busy && <Loader2 className="w-4 h-4 animate-spin" />} Gửi đánh giá
            </button>
          </Card>
        )
      )}
    </div>
  )
}
