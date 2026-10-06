import { useCallback, useEffect, useState, type ReactNode, type FormEvent } from 'react'
import { Search, Plus, ChevronLeft, ChevronRight, X } from 'lucide-react'
import {
  garageApi, formatVnd, formatDateTime, formatTime,
  type Booking, type BookingAction, type PortalBookings, type PortalBookingTab, type PortalService,
} from '@/services/api'
import { BookingStatusBadge, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const TABS: { key: PortalBookingTab; label: string }[] = [
  { key: 'upcoming', label: 'Sắp đến' },
  { key: 'pending', label: 'Chờ xác nhận' },
  { key: 'inside', label: 'Đang trong bãi' },
  { key: 'history', label: 'Lịch sử' },
]

const PAY_LABEL: Record<string, string> = { cash: 'Tiền mặt', transfer: 'Chuyển khoản' }

type Pay = 'cash' | 'transfer' | ''
type Dialog =
  | { kind: 'reject' | 'cancel'; b: Booking; reason: string }
  | { kind: 'checkin'; b: Booking; plate: string }
  | { kind: 'checkout' | 'paid'; b: Booking; pay: Pay }
  | null

const btn = 'px-3 py-1.5 rounded-full text-xs font-semibold border border-outline-variant hover:bg-surface-container-low disabled:opacity-50'
const btnPrimary = 'px-3 py-1.5 rounded-full text-xs font-semibold bg-primary text-white disabled:opacity-50'
const input = 'w-full px-3 py-2 rounded-xl border border-outline-variant bg-surface-container-low text-sm outline-none focus:border-primary'

export function GarageQueue() {
  const [tab, setTab] = useState<PortalBookingTab>('upcoming')
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<PortalBookings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialog, setDialog] = useState<Dialog>(null)
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState('')
  const [showWalkIn, setShowWalkIn] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    garageApi.bookings(tab, query, page)
      .then((d) => { setData(d); setError('') })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [tab, query, page])
  useEffect(load, [load])

  const run = async (b: Booking, action: BookingAction, extra: Parameters<typeof garageApi.bookingAction>[2] = {}) => {
    setBusy(true); setActionError('')
    try {
      await garageApi.bookingAction(b.id, action, extra)
      setDialog(null); load()
    } catch (e: any) {
      setActionError(e.message)
    } finally {
      setBusy(false)
    }
  }

  const open = (d: Dialog) => { setDialog(d); setActionError('') }
  const counts = data?.counts

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Lượt đặt &amp; vào/ra</h1>
        <button onClick={() => setShowWalkIn((v) => !v)} className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary text-white text-sm font-semibold">
          <Plus className="w-4 h-4" /> Xe vãng lai vào
        </button>
      </div>

      {showWalkIn && <WalkInForm onClose={() => setShowWalkIn(false)} onDone={() => { setShowWalkIn(false); setTab('inside'); setPage(1); load() }} />}

      <div className="flex gap-1 overflow-x-auto pb-1">
        {TABS.map((t) => {
          const c = t.key !== 'history' ? counts?.[t.key] : undefined
          return (
            <button key={t.key} onClick={() => { setTab(t.key); setPage(1) }}
              className={cn('px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap',
                tab === t.key ? 'bg-primary text-white' : 'bg-surface border border-outline-variant text-on-surface-variant')}>
              {t.label}{c !== undefined && <span className="ml-1.5 opacity-80">({c})</span>}
            </button>
          )
        })}
      </div>

      <form onSubmit={(e) => { e.preventDefault(); setPage(1); setQuery(q.trim()) }} className="flex gap-2">
        <div className="flex-1 flex items-center gap-2 bg-surface border border-outline-variant rounded-full px-4">
          <Search className="w-4 h-4 text-on-surface-variant" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm theo biển số hoặc mã lượt đặt"
            className="flex-1 py-2 bg-transparent outline-none text-sm" />
        </div>
        <button className="px-4 rounded-full bg-surface border border-outline-variant text-sm font-semibold">Tìm</button>
      </form>

      {error && <p className="text-sm text-error">{error}</p>}

      {loading && !data ? <Spinner /> : !data?.items.length ? (
        <div className="bg-surface rounded-2xl border border-outline-variant">
          <EmptyState title="Không có lượt nào" desc={query ? 'Thử từ khoá khác.' : undefined} />
        </div>
      ) : (
        <ul className={cn('space-y-3', loading && 'opacity-60')}>
          {data.items.map((b) => (
            <li key={b.id} className="bg-surface rounded-2xl border border-outline-variant p-4">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="font-bold">{b.license_plate || 'Chưa có biển số'} <span className="text-xs font-normal text-on-surface-variant">· {b.booking_code}</span></p>
                  <p className="text-xs text-on-surface-variant">
                    {b.customer_name || (b.source === 'walk_in' ? 'Khách vãng lai' : 'Khách')}{b.customer_phone ? ` · ${b.customer_phone}` : ''}
                    {' · '}{b.service_name || b.service_type_code}
                  </p>
                  <p className="text-xs text-on-surface-variant">{formatDateTime(b.start_time)} – {formatTime(b.end_time)}</p>
                </div>
                <div className="text-right space-y-1">
                  <BookingStatusBadge status={b.status} />
                  <p className="text-sm font-semibold">
                    {b.status === 'checked_in' && b.current_charge != null
                      ? <>Tạm tính {formatVnd(b.current_charge)}</>
                      : formatVnd(b.final_price ?? b.quoted_price)}
                  </p>
                  {(b.status === 'checked_out' || b.payment_status === 'paid') && (
                    <p className={cn('text-[11px] font-semibold', b.payment_status === 'paid' ? 'text-success' : 'text-warning')}>
                      {b.payment_status === 'paid' ? `Đã thu · ${PAY_LABEL[b.payment_method] ?? b.payment_method}` : 'Chưa thu tiền'}
                    </p>
                  )}
                </div>
              </div>

              <Actions b={b} busy={busy} onRun={run} onOpen={open} />

              {dialog?.b.id === b.id && (
                <div className="mt-3 p-3 rounded-xl bg-surface-container-low space-y-2">
                  {(dialog.kind === 'reject' || dialog.kind === 'cancel') && (
                    <>
                      <p className="text-sm font-semibold">{dialog.kind === 'reject' ? 'Lý do từ chối' : 'Lý do huỷ'}</p>
                      <input className={input} value={dialog.reason} autoFocus placeholder="Ví dụ: bãi đã kín chỗ"
                        onChange={(e) => setDialog({ ...dialog, reason: e.target.value })} />
                    </>
                  )}
                  {dialog.kind === 'checkin' && (
                    <>
                      <p className="text-sm font-semibold">Xác nhận biển số khi xe vào</p>
                      <input className={input} value={dialog.plate} autoFocus
                        onChange={(e) => setDialog({ ...dialog, plate: e.target.value.toUpperCase() })} />
                    </>
                  )}
                  {(dialog.kind === 'checkout' || dialog.kind === 'paid') && (
                    <>
                      <p className="text-sm font-semibold">Hình thức thanh toán</p>
                      <div className="flex flex-wrap gap-2">
                        {([['cash', 'Tiền mặt'], ['transfer', 'Chuyển khoản'], ...(dialog.kind === 'checkout' ? [['', 'Chưa thu']] : [])] as [Pay, string][]).map(([v, l]) => (
                          <button key={l} onClick={() => setDialog({ ...dialog, pay: v })}
                            className={cn(btn, dialog.pay === v && 'bg-primary text-white border-primary')}>{l}</button>
                        ))}
                      </div>
                    </>
                  )}
                  {actionError && <p className="text-xs text-error">{actionError}</p>}
                  <div className="flex gap-2 justify-end">
                    <button className={btn} onClick={() => setDialog(null)}>Đóng</button>
                    <button className={btnPrimary} disabled={busy} onClick={() => {
                      if (dialog.kind === 'reject' || dialog.kind === 'cancel') run(b, dialog.kind, { reason: dialog.reason })
                      else if (dialog.kind === 'checkin') run(b, 'checkin', { license_plate: dialog.plate.trim() })
                      else if (dialog.kind === 'checkout' || dialog.kind === 'paid') run(b, dialog.kind, dialog.pay ? { payment_method: dialog.pay } : {})
                    }}>{busy ? 'Đang xử lý…' : 'Xác nhận'}</button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {actionError && !dialog && <p className="text-sm text-error">{actionError}</p>}

      {data && data.pagination.total_pages > 1 && (
        <div className="flex items-center justify-center gap-3 text-sm">
          <button className={btn} disabled={page <= 1} onClick={() => setPage(page - 1)} aria-label="Trang trước"><ChevronLeft className="w-4 h-4" /></button>
          <span>Trang {data.pagination.current_page} / {data.pagination.total_pages}</span>
          <button className={btn} disabled={page >= data.pagination.total_pages} onClick={() => setPage(page + 1)} aria-label="Trang sau"><ChevronRight className="w-4 h-4" /></button>
        </div>
      )}
    </div>
  )
}

function Actions({ b, busy, onRun, onOpen }: {
  b: Booking; busy: boolean
  onRun: (b: Booking, a: BookingAction) => void
  onOpen: (d: Dialog) => void
}) {
  const pastGrace = b.grace_until ? Date.now() > new Date(b.grace_until).getTime() : false
  let content: ReactNode = null
  if (b.status === 'pending') {
    content = <>
      <button className={btnPrimary} disabled={busy} onClick={() => onRun(b, 'confirm')}>Xác nhận</button>
      <button className={btn} onClick={() => onOpen({ kind: 'reject', b, reason: '' })}>Từ chối</button>
    </>
  } else if (b.status === 'reserved') {
    content = <>
      <button className={btnPrimary} onClick={() => onOpen({ kind: 'checkin', b, plate: b.license_plate || '' })}>Check-in</button>
      {pastGrace && <button className={btn} disabled={busy} onClick={() => onRun(b, 'no_show')}>Không đến</button>}
      <button className={btn} onClick={() => onOpen({ kind: 'cancel', b, reason: '' })}>Huỷ</button>
    </>
  } else if (b.status === 'checked_in') {
    content = <button className={btnPrimary} onClick={() => onOpen({ kind: 'checkout', b, pay: 'cash' })}>Check-out</button>
  } else if (b.status === 'checked_out' && b.payment_status !== 'paid') {
    content = <button className={btnPrimary} onClick={() => onOpen({ kind: 'paid', b, pay: 'cash' })}>Đã thu tiền</button>
  }
  return content ? <div className="flex flex-wrap gap-2 mt-3">{content}</div> : null
}

function WalkInForm({ onClose, onDone }: { onClose: () => void; onDone: () => void }) {
  const [services, setServices] = useState<PortalService[]>([])
  const [plate, setPlate] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    garageApi.services().then((d) => {
      const list = d.services.filter((s) => s.category === 'parking')
      const all = list.length ? list : d.services
      setServices(all)
      setCode(all.find((s) => s.service_type_code === 'park_hourly')?.service_type_code ?? all[0]?.service_type_code ?? '')
    }).catch((e) => setError(e.message))
  }, [])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    if (!plate.trim()) { setError('Nhập biển số xe'); return }
    setBusy(true); setError('')
    try { await garageApi.walkIn(plate.trim(), code || undefined); onDone() }
    catch (err: any) { setError(err.message) }
    finally { setBusy(false) }
  }

  return (
    <form onSubmit={submit} className="bg-surface rounded-2xl border border-outline-variant p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-bold">Ghi nhận xe vãng lai vào bãi</h2>
        <button type="button" onClick={onClose} aria-label="Đóng"><X className="w-5 h-5 text-on-surface-variant" /></button>
      </div>
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="text-xs font-semibold text-on-surface-variant space-y-1">
          <span>Biển số</span>
          <input className={input} value={plate} onChange={(e) => setPlate(e.target.value.toUpperCase())} placeholder="51A-123.45" autoFocus />
        </label>
        <label className="text-xs font-semibold text-on-surface-variant space-y-1">
          <span>Dịch vụ</span>
          <select className={input} value={code} onChange={(e) => setCode(e.target.value)}>
            {services.length === 0 && <option value="">Chưa có dịch vụ</option>}
            {services.map((s) => <option key={s.id} value={s.service_type_code}>{s.name}</option>)}
          </select>
        </label>
      </div>
      {error && <p className="text-xs text-error">{error}</p>}
      <div className="flex justify-end">
        <button disabled={busy} className="px-5 py-2 rounded-full bg-primary text-white text-sm font-semibold disabled:opacity-50">
          {busy ? 'Đang ghi nhận…' : 'Cho xe vào'}
        </button>
      </div>
    </form>
  )
}
