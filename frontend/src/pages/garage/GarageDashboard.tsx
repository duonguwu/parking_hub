import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Minus, Plus, Car, Clock, Wallet, AlertCircle, RefreshCw } from 'lucide-react'
import {
  garageApi, formatVnd, formatTime, formatDateTime,
  type PortalOverview, type CapacityChart,
} from '@/services/api'
import { AvailabilityPill, BookingStatusBadge, EmptyState, Spinner, BarChart } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const SOURCE_LABEL: Record<string, string> = {
  manual: 'Chủ bãi cập nhật', checkin: 'Theo lượt vào/ra', simulated: 'Mô phỏng', camera: 'Camera',
}

const box = 'bg-surface rounded-2xl border border-outline-variant p-5'

export function GarageDashboard() {
  const [ov, setOv] = useState<PortalOverview | null>(null)
  const [chart, setChart] = useState<CapacityChart | null>(null)
  const [range, setRange] = useState<'24H' | '7D'>('24H')
  const [error, setError] = useState('')
  const [occInput, setOccInput] = useState('')
  const [occSaving, setOccSaving] = useState(false)
  const [occError, setOccError] = useState('')

  const load = useCallback(() => {
    garageApi.dashboardOverview()
      .then((d) => { setOv(d); setOccInput(d.availability.occupied != null ? String(d.availability.occupied) : ''); setError('') })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(load, [load])
  useEffect(() => {
    setChart(null)
    garageApi.dashboardCapacity(range).then(setChart).catch(() => setChart({ range, labels: [], data: [] }))
  }, [range])

  const saveOccupied = async (value: number) => {
    if (!ov) return
    const v = Math.max(0, Math.min(ov.availability.total_spots || value, Math.round(value)))
    setOccSaving(true); setOccError('')
    try {
      const a = await garageApi.setOccupied(v)
      setOv({ ...ov, availability: a })
      setOccInput(String(a.occupied ?? v))
    } catch (e: any) {
      setOccError(e.message)
    } finally {
      setOccSaving(false)
    }
  }

  if (!ov) {
    return error
      ? <div className="p-6"><EmptyState title="Không tải được tổng quan" desc={error} /></div>
      : <Spinner />
  }

  const a = ov.availability
  const current = Number(occInput) || 0
  const revDiff = ov.revenue.yesterday ? Math.round(((ov.revenue.today - ov.revenue.yesterday) / ov.revenue.yesterday) * 100) : null
  const chartHasData = !!chart && chart.data.some((v) => v !== null)

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">{ov.garage.name}</h1>
          <p className="text-sm text-on-surface-variant">
            Cấp tích hợp {ov.garage.integration_level} · {ov.garage.integration_label}
            {!ov.garage.is_accepting_bookings && ' · Đang tạm ngưng nhận đặt chỗ'}
          </p>
        </div>
        <button onClick={load} className="p-2 rounded-full hover:bg-surface-container-low text-on-surface-variant" aria-label="Tải lại">
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {ov.garage.status === 'pending_review' && (
        <div className="flex gap-2 items-start rounded-xl bg-warning/10 text-warning px-4 py-3 text-sm font-semibold">
          <AlertCircle className="w-5 h-5 shrink-0" /> Bãi đang chờ admin duyệt. Tài xế chưa thấy bãi trên bản đồ.
        </div>
      )}
      {ov.garage.status === 'suspended' && (
        <div className="flex gap-2 items-start rounded-xl bg-error/10 text-error px-4 py-3 text-sm font-semibold">
          <AlertCircle className="w-5 h-5 shrink-0" /> Bãi đang bị tạm ngưng. Vui lòng liên hệ quản trị viên.
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <div className={box}>
          <p className="text-xs font-semibold text-on-surface-variant uppercase">Chỗ trống hiện tại</p>
          <div className="flex items-end gap-2 mt-2">
            <span className="text-5xl font-black">{a.has_data ? a.available : '—'}</span>
            <span className="text-on-surface-variant mb-1.5">/ {a.total_spots} chỗ</span>
          </div>
          <AvailabilityPill a={a} level={ov.garage.integration_level} className="mt-3" />
          {a.has_data && a.held ? <p className="text-xs text-on-surface-variant mt-2">Đang giữ cho lượt đặt: {a.held} chỗ</p> : null}
        </div>

        <div className={box}>
          <p className="text-xs font-semibold text-on-surface-variant uppercase">Cập nhật số xe đang đỗ</p>
          <div className="flex items-center gap-2 mt-3">
            <button disabled={occSaving || current <= 0} onClick={() => saveOccupied(current - 1)}
              className="w-11 h-11 rounded-full border border-outline-variant flex items-center justify-center disabled:opacity-40" aria-label="Bớt một xe">
              <Minus className="w-5 h-5" />
            </button>
            <input type="number" min={0} max={a.total_spots} value={occInput}
              onChange={(e) => setOccInput(e.target.value)}
              className="w-24 h-11 text-center text-xl font-bold rounded-xl border border-outline-variant bg-surface-container-low" />
            <button disabled={occSaving || (a.total_spots > 0 && current >= a.total_spots)} onClick={() => saveOccupied(current + 1)}
              className="w-11 h-11 rounded-full border border-outline-variant flex items-center justify-center disabled:opacity-40" aria-label="Thêm một xe">
              <Plus className="w-5 h-5" />
            </button>
            <button disabled={occSaving || occInput === ''} onClick={() => saveOccupied(current)}
              className="ml-auto px-4 h-11 rounded-full bg-primary text-white text-sm font-semibold disabled:opacity-50">
              {occSaving ? 'Đang lưu…' : 'Lưu'}
            </button>
          </div>
          <p className="text-xs text-on-surface-variant mt-3">
            {a.updated_at
              ? <>Nguồn: {SOURCE_LABEL[a.source] ?? a.source} · lúc {formatDateTime(a.updated_at)}</>
              : 'Chưa có lần cập nhật nào'}
          </p>
          {occError && <p className="text-xs text-error mt-1">{occError}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat icon={Car} label="Xe đang trong bãi" value={String(ov.inside_count)} />
        <Link to="/garage/queue" className="block">
          <Stat icon={Clock} label="Chờ xác nhận" value={String(ov.pending_count)} highlight={ov.pending_count > 0} hint="Xem lượt đặt →" />
        </Link>
        <Stat icon={Wallet} label="Doanh thu hôm nay" value={formatVnd(ov.revenue.today)}
          hint={`Hôm qua ${formatVnd(ov.revenue.yesterday)}${revDiff !== null ? ` (${revDiff >= 0 ? '+' : ''}${revDiff}%)` : ''}`} />
        <Stat icon={AlertCircle} label="Lượt chưa thanh toán" value={String(ov.revenue.unpaid_count)} highlight={ov.revenue.unpaid_count > 0}
          hint={`${ov.revenue.sessions_today} lượt ra hôm nay`} />
      </div>

      <div className="grid lg:grid-cols-5 gap-4">
        <div className={cn(box, 'lg:col-span-3')}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold">Tỷ lệ lấp đầy</h2>
            <div className="flex bg-surface-container-low rounded-full p-0.5 text-xs font-semibold">
              {(['24H', '7D'] as const).map((r) => (
                <button key={r} onClick={() => setRange(r)}
                  className={cn('px-3 py-1 rounded-full', range === r ? 'bg-primary text-white' : 'text-on-surface-variant')}>
                  {r === '24H' ? '24 giờ' : '7 ngày'}
                </button>
              ))}
            </div>
          </div>
          {!chart ? <Spinner /> : chartHasData
            ? <BarChart labels={chart.labels} values={chart.data} height={140} format={(v) => `${Math.round(v)}%`} />
            : <EmptyState title="Chưa có dữ liệu lấp đầy" desc="Cập nhật số xe đang đỗ để bắt đầu ghi nhận." />}
        </div>

        <div className={cn(box, 'lg:col-span-2')}>
          <h2 className="font-bold mb-3">Sắp đến trong 2 giờ</h2>
          {ov.upcoming.length === 0
            ? <EmptyState title="Không có lượt đặt sắp đến" />
            : (
              <ul className="divide-y divide-outline-variant">
                {ov.upcoming.map((b) => (
                  <li key={b.id} className="py-2.5 flex items-center justify-between gap-2">
                    <div className="min-w-0">
                      <p className="font-semibold text-sm">{b.license_plate || '—'} <span className="text-on-surface-variant font-normal">· {b.booking_code}</span></p>
                      <p className="text-xs text-on-surface-variant truncate">{formatTime(b.start_time)} · {b.service_name || b.service_type_code}{b.customer_name ? ` · ${b.customer_name}` : ''}</p>
                    </div>
                    <BookingStatusBadge status={b.status} />
                  </li>
                ))}
              </ul>
            )}
        </div>
      </div>
    </div>
  )
}

function Stat({ icon: Icon, label, value, hint, highlight }: {
  icon: typeof Car; label: string; value: string; hint?: string; highlight?: boolean
}) {
  return (
    <div className={cn(box, 'p-4 h-full', highlight && 'border-warning')}>
      <div className="flex items-center gap-2 text-on-surface-variant text-xs font-semibold">
        <Icon className={cn('w-4 h-4', highlight && 'text-warning')} /> {label}
      </div>
      <p className="text-xl md:text-2xl font-bold mt-2 break-words">{value}</p>
      {hint && <p className="text-[11px] text-on-surface-variant mt-1">{hint}</p>}
    </div>
  )
}
