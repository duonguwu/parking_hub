import { useEffect, useMemo, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ChevronLeft, MapPin, Phone, Info, Loader2, CalendarCheck } from 'lucide-react'
import { Card } from '@/components/ui/card'
import {
  customerApi, catalogApi, formatVnd, formatTime, formatDateTime, formatDuration,
  COVER_LABEL, GUARD_LABEL, CCTV_LABEL, FLOOD_LABEL, PARKING_STYLE_LABEL, UNIT_LABEL,
  type GarageDetailData, type GarageService, type Pricing, type Quote, type Vehicle, type OperatingHours,
} from '@/services/api'
import { Stars, AvailabilityPill, BadgeList, EmptyState, Spinner, BarChart } from '@/components/parking/ParkingBits'
import { useAuth } from '@/services/auth-context'
import { cn } from '@/services/utils'

const DAY_NAMES = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
const DAY_KEYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] as const
const UNIT_MINUTES: Record<string, number> = { hour: 60, night: 720, day: 1440, workday: 600, month: 43200, session: 240 }
const HOUR_PRESETS = [1, 2, 3, 4, 6, 8, 12]

export function pricingSummary(p: Pricing | undefined, unit: string): string {
  if (!p) return '—'
  if (p.mode === 'block') {
    const parts = [`${formatVnd(p.first_block_price)} / ${p.first_block_minutes} phút đầu`]
    if (p.next_block_price) parts.push(`${formatVnd(p.next_block_price)} mỗi ${p.next_block_minutes} phút tiếp`)
    if (p.daily_cap) parts.push(`trần ${formatVnd(p.daily_cap)}/ngày`)
    return parts.join(', ')
  }
  return `${formatVnd(p.flat_price)} / ${UNIT_LABEL[unit] ?? unit}`
}

function peakNote(p: Pricing | undefined): string | null {
  if (!p?.peak_rules?.length) return null
  return 'Giờ cao điểm: ' + p.peak_rules.map((r) =>
    `${r.days.length === 7 ? 'mọi ngày' : r.days.map((d) => DAY_NAMES[d]).join(',')} ${r.start}–${r.end} ×${r.multiplier}`).join('; ')
}

function hoursText(h: OperatingHours): string {
  if (h.is_24h) return 'Mở 24/7'
  const today = DAY_KEYS[(new Date().getDay() + 6) % 7]
  const d = h[today]
  if (!d) return 'Chưa cập nhật'
  return d.closed ? 'Hôm nay nghỉ' : `Hôm nay ${d.open}–${d.close}`
}

const pad = (n: number) => String(n).padStart(2, '0')
const localDate = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

function BookingPanel({ data }: { data: GarageDetailData }) {
  const { garage, services } = data
  const { user } = useAuth()
  const navigate = useNavigate()
  const bookable = services.filter((s) => s.category !== 'addon')
  const [code, setCode] = useState(bookable[0]?.code ?? '')
  const [date, setDate] = useState(() => localDate(new Date()))
  const [time, setTime] = useState(() => { const d = new Date(Date.now() + 15 * 60000); return `${pad(d.getHours())}:${pad(d.getMinutes())}` })
  const [hours, setHours] = useState(2)
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [vehicleId, setVehicleId] = useState('')
  const [plate, setPlate] = useState('')
  const [quote, setQuote] = useState<Quote | null>(null)
  const [quoteErr, setQuoteErr] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const svc: GarageService | undefined = bookable.find((s) => s.code === code)
  const isHourly = svc?.pricing?.mode === 'block' || svc?.unit === 'hour'
  const start = useMemo(() => new Date(`${date}T${time}`), [date, time])
  const end = useMemo(() => {
    const mins = isHourly ? hours * 60 : (svc?.pricing?.flat_unit_minutes || UNIT_MINUTES[svc?.unit ?? ''] || 120)
    return new Date(start.getTime() + mins * 60000)
  }, [start, hours, isHourly, svc])

  useEffect(() => {
    if (!user) return
    customerApi.vehicles().then((vs) => { setVehicles(vs); setVehicleId(vs.find((v) => v.is_default)?.id ?? vs[0]?.id ?? '') }).catch(() => {})
  }, [user])

  useEffect(() => {
    setQuote(null); setQuoteErr('')
    if (!code || isNaN(start.getTime())) return
    const t = setTimeout(() => {
      catalogApi.quote(garage.id, code, start.toISOString(), end.toISOString()).then(setQuote).catch((e) => setQuoteErr(e.message))
    }, 400)
    return () => clearTimeout(t)
  }, [garage.id, code, start, end])

  const blocked = garage.integration_level === 1
    ? 'Bãi này chỉ có thông tin danh mục, chưa nhận đặt chỗ qua ứng dụng. Bạn có thể đến trực tiếp.'
    : !garage.is_accepting_bookings ? 'Bãi đang tạm ngưng nhận đặt chỗ.'
    : !bookable.length ? 'Bãi chưa niêm yết dịch vụ để đặt.' : ''

  const submit = async () => {
    setError('')
    if (start.getTime() < Date.now() - 10 * 60000) return setError('Giờ bắt đầu đã qua, vui lòng chọn lại.')
    if (!vehicleId && !plate.trim()) return setError('Vui lòng chọn xe hoặc nhập biển số.')
    setSubmitting(true)
    try {
      const b = await customerApi.createBooking({
        garage_id: garage.id, service_type_code: code, start_time: start.toISOString(), end_time: end.toISOString(),
        ...(vehicleId ? { vehicle_id: vehicleId } : { license_plate: plate.trim().toUpperCase() }),
      })
      navigate(`/app/bookings/${b.id}`)
    } catch (e: any) { setError(e.message); setSubmitting(false) }
  }

  const input = 'w-full h-10 rounded-xl border border-outline-variant bg-surface px-3 text-sm outline-none focus:border-primary'
  return (
    <Card className="p-4 rounded-2xl space-y-3">
      <h2 className="font-bold text-on-surface flex items-center gap-2"><CalendarCheck className="w-4 h-4 text-primary" /> Đặt chỗ</h2>
      {blocked ? <p className="text-sm text-on-surface-variant">{blocked}</p>
        : !user ? <p className="text-sm text-on-surface-variant">Vui lòng <Link to="/login" className="text-primary font-bold">đăng nhập</Link> để đặt chỗ.</p>
        : <>
          {garage.integration_level === 2 && (
            <p className="text-xs bg-warning/10 text-warning rounded-xl p-2.5 flex gap-1.5"><Info className="w-4 h-4 shrink-0" /> Bãi sẽ xác nhận yêu cầu của bạn.</p>
          )}
          <label className="block text-xs font-semibold text-on-surface-variant">Dịch vụ
            <select className={input} value={code} onChange={(e) => setCode(e.target.value)}>
              {bookable.map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
            </select>
          </label>
          <div className="grid grid-cols-2 gap-2">
            <label className="block text-xs font-semibold text-on-surface-variant">Ngày
              <input type="date" className={input} value={date} min={localDate(new Date())} onChange={(e) => setDate(e.target.value)} />
            </label>
            <label className="block text-xs font-semibold text-on-surface-variant">Giờ vào
              <input type="time" className={input} value={time} onChange={(e) => setTime(e.target.value)} />
            </label>
          </div>
          {isHourly ? (
            <div>
              <p className="text-xs font-semibold text-on-surface-variant mb-1">Thời lượng</p>
              <div className="flex flex-wrap gap-1.5">
                {HOUR_PRESETS.map((h) => (
                  <button key={h} onClick={() => setHours(h)} className={cn('px-3 py-1.5 rounded-full border text-xs font-semibold',
                    hours === h ? 'bg-primary text-white border-primary' : 'border-outline-variant text-on-surface-variant')}>{h} giờ</button>
                ))}
              </div>
            </div>
          ) : null}
          <p className="text-xs text-on-surface-variant">Từ {formatDateTime(start.toISOString())} đến {formatDateTime(end.toISOString())}</p>
          <label className="block text-xs font-semibold text-on-surface-variant">Xe
            <select className={input} value={vehicleId} onChange={(e) => setVehicleId(e.target.value)}>
              {vehicles.map((v) => <option key={v.id} value={v.id}>{v.license_plate} · {v.brand} {v.model}</option>)}
              <option value="">Nhập biển số khác</option>
            </select>
          </label>
          {!vehicleId && <input className={input} placeholder="Biển số, VD: 51A-123.45" value={plate} onChange={(e) => setPlate(e.target.value)} />}
          <div className="rounded-xl bg-surface-container-low p-3 text-sm">
            {quote ? (
              <>
                <div className="flex justify-between font-bold"><span>Tạm tính ({formatDuration(quote.minutes)})</span><span className="text-primary">{formatVnd(quote.amount)}</span></div>
                {quote.breakdown.map((b, i) => <div key={i} className="flex justify-between text-xs text-on-surface-variant"><span>{b.label}</span><span>{formatVnd(b.amount)}</span></div>)}
              </>
            ) : <span className="text-xs text-on-surface-variant">{quoteErr || 'Đang báo giá…'}</span>}
          </div>
          {error && <p className="text-xs text-error font-semibold">{error}</p>}
          <button onClick={submit} disabled={submitting || !code} className="w-full h-11 rounded-full bg-primary text-white font-bold text-sm disabled:opacity-50 flex items-center justify-center gap-2">
            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
            {garage.integration_level === 2 ? 'Gửi yêu cầu đặt chỗ' : 'Xác nhận giữ chỗ'}
          </button>
        </>}
    </Card>
  )
}

function Attr({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface-container-low rounded-xl p-2.5">
      <p className="text-[10px] font-semibold text-on-surface-variant">{label}</p>
      <p className="text-sm font-semibold text-on-surface">{value}</p>
    </div>
  )
}

export function CustomerGarageDetail() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<GarageDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    customerApi.garageDetail(id).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <Spinner />
  if (error || !data) return <EmptyState title="Không tải được bãi đỗ" desc={error} />

  const { garage: g, services, hourly_today, forecast, reviews } = data
  const a = g.attributes
  const addr = [g.address.street, g.address.ward, g.address.district, g.address.city].filter(Boolean).join(', ')
  const nowH = new Date().getHours()
  const pct = (r: number) => `${Math.round(r * 100)}%`

  return (
    <div className="max-w-5xl mx-auto w-full space-y-4 pb-8">
      <div className="flex items-start gap-3">
        <Link to="/app/map" className="p-2 rounded-full border border-outline-variant bg-surface shrink-0"><ChevronLeft className="w-5 h-5" /></Link>
        <div className="min-w-0">
          <h1 className="text-xl font-black text-on-surface">{g.name}</h1>
          <p className="text-xs text-on-surface-variant flex items-center gap-1"><MapPin className="w-3.5 h-3.5 shrink-0" /> {addr || 'Chưa có địa chỉ'}</p>
          <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-on-surface-variant">
            {g.grade > 0 ? <Stars value={g.grade} /> : <span>Chưa xếp hạng</span>}
            <span>· {g.lot_type_label}</span>
            <span>· {g.integration_label}</span>
          </div>
          <BadgeList badges={g.badges} className="mt-2" />
        </div>
      </div>

      <div className="grid md:grid-cols-[1fr_360px] gap-4 items-start">
        <div className="space-y-4">
          <Card className="p-4 rounded-2xl space-y-3">
            <div className="flex items-center justify-between gap-2">
              <h2 className="font-bold text-on-surface">Chỗ trống hiện tại</h2>
              <AvailabilityPill a={g.availability} level={g.integration_level} showTime />
            </div>
            {forecast.length > 0 ? (
              <div className="grid grid-cols-3 gap-2">
                {forecast.map((f) => (
                  <div key={f.hours_ahead} className="bg-surface-container-low rounded-xl p-2.5 text-center">
                    <p className="text-[10px] text-on-surface-variant">Sau {f.hours_ahead} giờ</p>
                    <p className="text-base font-bold text-on-surface">{f.expected_available} chỗ</p>
                    <p className="text-[10px] text-on-surface-variant">lấp đầy {pct(f.occupancy_rate)}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-xs text-on-surface-variant">Chưa có dự báo cho bãi này.</p>}
          </Card>

          <Card className="p-4 rounded-2xl">
            <h2 className="font-bold text-on-surface mb-3">Đặc điểm bãi</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <Attr label="Mái che" value={a.cover ? COVER_LABEL[a.cover] : 'Chưa cập nhật'} />
              <Attr label="Giới hạn chiều cao" value={a.max_height_m ? `${a.max_height_m} m` : 'Không giới hạn / chưa rõ'} />
              <Attr label="Bảo vệ" value={a.guard ? GUARD_LABEL[a.guard] + (a.guard === 'hours' && a.guard_hours ? ` (${a.guard_hours})` : '') : 'Chưa cập nhật'} />
              <Attr label="Camera" value={a.cctv ? CCTV_LABEL[a.cctv] : 'Chưa cập nhật'} />
              <Attr label="Sạc xe điện" value={a.ev_chargers?.count ? `${a.ev_chargers.count} trụ${a.ev_chargers.power_kw ? ` · ${a.ev_chargers.power_kw} kW` : ''}` : 'Không có'} />
              <Attr label="Nguy cơ ngập" value={a.flood_risk ? FLOOD_LABEL[a.flood_risk] : 'Chưa cập nhật'} />
              <Attr label="Cách đỗ" value={a.parking_style ? PARKING_STYLE_LABEL[a.parking_style] : 'Chưa cập nhật'} />
              <Attr label="Giờ mở cửa" value={hoursText(g.operating_hours)} />
              <Attr label="Tổng số chỗ" value={g.capacity?.total_spots ? String(g.capacity.total_spots) : 'Chưa cập nhật'} />
            </div>
            {g.description && <p className="text-sm text-on-surface-variant mt-3">{g.description}</p>}
            {g.contacts?.phone && <p className="text-sm mt-2 flex items-center gap-1.5"><Phone className="w-4 h-4" /> {g.contacts.phone}</p>}
          </Card>

          <Card className="p-4 rounded-2xl">
            <h2 className="font-bold text-on-surface mb-3">Bảng giá</h2>
            {services.length === 0 ? <p className="text-xs text-on-surface-variant">Bãi chưa niêm yết giá.</p> : (
              <div className="divide-y divide-outline-variant">
                {services.map((s) => (
                  <div key={s.id} className="py-2.5">
                    <div className="flex justify-between gap-2">
                      <p className="text-sm font-semibold text-on-surface">{s.name}</p>
                      <span className="text-[11px] text-on-surface-variant whitespace-nowrap">theo {UNIT_LABEL[s.unit] ?? s.unit}</span>
                    </div>
                    <p className="text-xs text-on-surface-variant">{pricingSummary(s.pricing, s.unit)}</p>
                    {peakNote(s.pricing) && <p className="text-[11px] text-warning">{peakNote(s.pricing)}</p>}
                    {s.note && <p className="text-[11px] text-on-surface-variant italic">{s.note}</p>}
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card className="p-4 rounded-2xl">
            <h2 className="font-bold text-on-surface mb-1">Mức lấp đầy hôm nay</h2>
            <p className="text-[11px] text-on-surface-variant mb-3">
              {hourly_today.some((h) => h.from_history) ? 'Theo dữ liệu lịch sử của bãi' : 'Ước tính theo loại bãi'}
            </p>
            {hourly_today.length ? (
              <BarChart labels={hourly_today.map((h) => `${h.hour}h`)} values={hourly_today.map((h) => Math.round(h.rate * 100))}
                highlight={hourly_today.findIndex((h) => h.hour === nowH)} format={(v) => `${v}%`} />
            ) : <p className="text-xs text-on-surface-variant">Chưa có dữ liệu.</p>}
          </Card>

          <Card className="p-4 rounded-2xl">
            <h2 className="font-bold text-on-surface mb-3">Độ tin cậy & đánh giá</h2>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <Attr label="Giữ đúng chỗ" value={g.stats?.total_sessions ? pct(g.stats.fulfillment_rate ?? 0) : 'Chưa đủ dữ liệu'} />
              <Attr label="Đánh giá" value={g.stats?.rating_count ? `${(g.stats.avg_rating ?? 0).toFixed(1)}★ (${g.stats.rating_count})` : 'Chưa có'} />
            </div>
            {reviews.length === 0 ? <p className="text-xs text-on-surface-variant">Chưa có nhận xét.</p> : (
              <div className="space-y-2.5">
                {reviews.map((r, i) => (
                  <div key={i} className="text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{r.name}</span>
                      {r.rating != null && <Stars value={r.rating} size={10} />}
                      <span className="text-[10px] text-on-surface-variant">{formatDateTime(r.at)}</span>
                    </div>
                    {r.comment && <p className="text-xs text-on-surface-variant">{r.comment}</p>}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <div className="md:sticky md:top-24">
          <BookingPanel data={data} />
          {g.availability?.updated_at && <p className="text-[10px] text-on-surface-variant mt-2 text-center">Dữ liệu chỗ trống lúc {formatTime(g.availability.updated_at)}</p>}
        </div>
      </div>
    </div>
  )
}
