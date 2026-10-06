import { useEffect, useState, type ReactNode } from 'react'
import { Save, Info } from 'lucide-react'
import {
  garageApi, catalogApi, formatDateTime,
  COVER_LABEL, GUARD_LABEL, CCTV_LABEL, FLOOD_LABEL, PARKING_STYLE_LABEL, LOT_TYPE_LABEL, GARAGE_STATUS_LABEL,
  type Garage, type Taxonomy, type GarageProfileUpdate, type GarageAttributes, type GarageCapacity,
  type OperatingHours, type DayHours, type LatLng, type LotType,
} from '@/services/api'
import { Stars, BadgeList, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { ParkingMap } from '@/components/parking/ParkingMap'
import { cn } from '@/services/utils'

const DAYS = [
  ['monday', 'Thứ 2'], ['tuesday', 'Thứ 3'], ['wednesday', 'Thứ 4'], ['thursday', 'Thứ 5'],
  ['friday', 'Thứ 6'], ['saturday', 'Thứ 7'], ['sunday', 'Chủ nhật'],
] as const

const LIGHTING_LABEL: Record<string, string> = { good: 'Tốt', basic: 'Cơ bản', poor: 'Yếu' }
const SURFACE_LABEL: Record<string, string> = { concrete: 'Bê tông', asphalt: 'Nhựa đường', gravel: 'Sỏi / đất' }

interface Form {
  name: string
  description: string
  lot_type: LotType
  address: Record<string, string>
  contacts: Record<string, string>
  is_accepting_bookings: boolean
  capacity: GarageCapacity
  attributes: GarageAttributes
  operating_hours: OperatingHours
  entrance: LatLng | null
}

const toForm = (g: Garage): Form => ({
  name: g.name || '',
  description: g.description || '',
  lot_type: g.lot_type,
  address: { street: '', ward: '', district: '', city: '', ...(g.address as Record<string, string>) },
  contacts: { phone: '', zalo: '', manager_name: '', ...(g.contacts as Record<string, string>) },
  is_accepting_bookings: g.is_accepting_bookings,
  capacity: { ...g.capacity },
  attributes: { ...g.attributes, ev_chargers: { ...(g.attributes.ev_chargers || {}) } },
  operating_hours: JSON.parse(JSON.stringify(g.operating_hours || {})),
  entrance: g.entrance,
})

const input = 'w-full px-3 py-2 rounded-xl border border-outline-variant bg-surface-container-low text-sm outline-none focus:border-primary'
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b)

export function GarageProfile() {
  const [garage, setGarage] = useState<Garage | null>(null)
  const [tax, setTax] = useState<Taxonomy | null>(null)
  const [form, setForm] = useState<Form | null>(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null)

  useEffect(() => {
    garageApi.myGarage().then((g) => { setGarage(g); setForm(toForm(g)) }).catch((e) => setError(e.message))
    catalogApi.taxonomy().then(setTax).catch(() => setTax(null))
  }, [])

  if (!form || !garage) {
    return error ? <div className="p-6"><EmptyState title="Không tải được hồ sơ bãi" desc={error} /></div> : <Spinner />
  }

  const orig = toForm(garage)
  const set = <K extends keyof Form>(k: K, v: Form[K]) => setForm({ ...form, [k]: v })
  const setAttr = <K extends keyof GarageAttributes>(k: K, v: GarageAttributes[K]) => set('attributes', { ...form.attributes, [k]: v })
  const setCap = (k: keyof GarageCapacity, v: number) => set('capacity', { ...form.capacity, [k]: v })
  const setDay = (d: string, v: Partial<DayHours>) => {
    const cur = (form.operating_hours as Record<string, DayHours>)[d] || { open: '06:00', close: '22:00' }
    set('operating_hours', { ...form.operating_hours, [d]: { ...cur, ...v } })
  }

  const buildUpdate = (): GarageProfileUpdate => {
    const u: GarageProfileUpdate = {}
    if (form.name !== orig.name) u.name = form.name.trim()
    if (form.description !== orig.description) u.description = form.description
    if (form.lot_type !== orig.lot_type) u.lot_type = form.lot_type
    if (!same(form.address, orig.address)) u.address = form.address
    if (!same(form.contacts, orig.contacts)) u.contacts = form.contacts
    if (form.is_accepting_bookings !== orig.is_accepting_bookings) u.is_accepting_bookings = form.is_accepting_bookings
    const cap: Partial<GarageCapacity> = {}
    ;(Object.keys(form.capacity) as (keyof GarageCapacity)[]).forEach((k) => { if (form.capacity[k] !== orig.capacity[k]) cap[k] = form.capacity[k] })
    if (Object.keys(cap).length) u.capacity = cap
    const attrs: Record<string, unknown> = {}
    ;(Object.keys(form.attributes) as (keyof GarageAttributes)[]).forEach((k) => {
      if (!same(form.attributes[k], orig.attributes[k])) attrs[k] = form.attributes[k]
    })
    if (Object.keys(attrs).length) u.attributes = attrs as GarageAttributes
    if (!same(form.operating_hours, orig.operating_hours)) u.operating_hours = form.operating_hours
    if (form.entrance && !same(form.entrance, orig.entrance)) u.entrance = form.entrance
    return u
  }

  const dirty = Object.keys(buildUpdate()).length > 0

  const save = async () => {
    const u = buildUpdate()
    if (!Object.keys(u).length) return
    setSaving(true); setMsg(null)
    try {
      const g = await garageApi.updateGarage(u)
      setGarage(g); setForm(toForm(g))
      setMsg({ ok: true, text: 'Đã lưu hồ sơ bãi' })
    } catch (e: any) {
      setMsg({ ok: false, text: e.message })
    } finally {
      setSaving(false)
    }
  }

  const a = form.attributes
  const lotTypes = tax?.lot_types ?? Object.entries(LOT_TYPE_LABEL).map(([code, label]) => ({ code: code as LotType, label }))
  const levelDesc = tax?.integration_levels.find((l) => l.level === garage.integration_level)?.desc
  const hours = form.operating_hours as Record<string, DayHours | undefined>
  const center = form.entrance ?? garage.position ?? undefined

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 pb-28 md:pb-24 space-y-5">
      <h1 className="text-2xl font-bold">Hồ sơ bãi</h1>

      <div className="grid lg:grid-cols-3 gap-5 items-start">
        <div className="lg:col-span-2 space-y-5">
          <Section title="Thông tin chung">
            <Field label="Tên bãi" wide><input className={input} value={form.name} onChange={(e) => set('name', e.target.value)} /></Field>
            <Field label="Mô tả" wide>
              <textarea className={cn(input, 'min-h-20')} value={form.description} onChange={(e) => set('description', e.target.value)} />
            </Field>
            <Field label="Loại hình bãi">
              <select className={input} value={form.lot_type} onChange={(e) => set('lot_type', e.target.value as LotType)}>
                {lotTypes.map((t) => <option key={t.code} value={t.code}>{t.label}</option>)}
              </select>
            </Field>
            <Field label="Nhận đặt chỗ qua ứng dụng">
              <Toggle on={form.is_accepting_bookings} onChange={(v) => set('is_accepting_bookings', v)}
                label={form.is_accepting_bookings ? 'Đang nhận' : 'Tạm ngưng'} />
            </Field>
            {([['street', 'Số nhà, đường'], ['ward', 'Phường / xã'], ['district', 'Quận / huyện'], ['city', 'Tỉnh / thành phố']] as const).map(([k, l]) => (
              <Field key={k} label={l}>
                <input className={input} value={form.address[k] || ''} onChange={(e) => set('address', { ...form.address, [k]: e.target.value })} />
              </Field>
            ))}
            {([['phone', 'Số điện thoại'], ['zalo', 'Zalo'], ['manager_name', 'Người quản lý']] as const).map(([k, l]) => (
              <Field key={k} label={l}>
                <input className={input} value={form.contacts[k] || ''} onChange={(e) => set('contacts', { ...form.contacts, [k]: e.target.value })} />
              </Field>
            ))}
            <Field label="Vị trí lối vào (bấm lên bản đồ để đặt)" wide>
              <div className="h-56 rounded-xl overflow-hidden border border-outline-variant">
                <ParkingMap garages={[]} center={center} zoom={17} searchPoint={form.entrance} flyTo={form.entrance}
                  onMapClick={(p) => set('entrance', p)} />
              </div>
              {form.entrance && <p className="text-[11px] text-on-surface-variant mt-1">{form.entrance.lat.toFixed(6)}, {form.entrance.lng.toFixed(6)}</p>}
            </Field>
          </Section>

          <Section title="Sức chứa">
            <Field label="Tổng số chỗ"><Num value={form.capacity.total_spots} min={1} onChange={(v) => setCap('total_spots', v)} /></Field>
            <Field label="Chỗ dành cho xe vãng lai"><Num value={form.capacity.walk_in_spots} onChange={(v) => setCap('walk_in_spots', v)} /></Field>
            <Field label="Chỗ thuê tháng"><Num value={form.capacity.monthly_spots} onChange={(v) => setCap('monthly_spots', v)} /></Field>
            <Field label="Tỉ lệ cho giữ trước (%)">
              <Num value={Math.round((form.capacity.reservable_ratio || 0) * 100)} max={100}
                onChange={(v) => setCap('reservable_ratio', Math.min(100, v) / 100)} />
            </Field>
            <Field label="Thời gian giữ chỗ quá giờ (phút)"><Num value={form.capacity.grace_minutes} onChange={(v) => setCap('grace_minutes', v)} /></Field>
          </Section>

          <Section title="Thuộc tính">
            <Field label="Mái che"><Select value={a.cover} labels={COVER_LABEL} onChange={(v) => setAttr('cover', v as GarageAttributes['cover'])} /></Field>
            <Field label="Chiều cao tối đa (m)">
              <input type="number" step="0.1" min={0} className={input} value={a.max_height_m ?? ''}
                onChange={(e) => setAttr('max_height_m', e.target.value === '' ? null : Number(e.target.value))} placeholder="Không giới hạn" />
            </Field>
            <Field label="Bảo vệ"><Select value={a.guard} labels={GUARD_LABEL} onChange={(v) => setAttr('guard', v as GarageAttributes['guard'])} /></Field>
            {a.guard === 'hours' && (
              <Field label="Giờ có bảo vệ"><input className={input} value={a.guard_hours || ''} placeholder="06:00-22:00" onChange={(e) => setAttr('guard_hours', e.target.value)} /></Field>
            )}
            <Field label="Camera"><Select value={a.cctv} labels={CCTV_LABEL} onChange={(v) => setAttr('cctv', v as GarageAttributes['cctv'])} /></Field>
            <Field label="Nguy cơ ngập"><Select value={a.flood_risk} labels={FLOOD_LABEL} onChange={(v) => setAttr('flood_risk', v as GarageAttributes['flood_risk'])} /></Field>
            <Field label="Cách đỗ"><Select value={a.parking_style} labels={PARKING_STYLE_LABEL} onChange={(v) => setAttr('parking_style', v as GarageAttributes['parking_style'])} /></Field>
            <Field label="Số trụ sạc xe điện">
              <Num value={a.ev_chargers?.count ?? 0} onChange={(v) => setAttr('ev_chargers', { ...a.ev_chargers, count: v })} />
            </Field>
            {(a.ev_chargers?.count ?? 0) > 0 && (
              <Field label="Công suất sạc (kW)">
                <Num value={a.ev_chargers?.power_kw ?? 0} onChange={(v) => setAttr('ev_chargers', { ...a.ev_chargers, power_kw: v })} />
              </Field>
            )}
            <Field label="Chiếu sáng"><Select value={a.lighting} labels={LIGHTING_LABEL} onChange={(v) => setAttr('lighting', v as GarageAttributes['lighting'])} /></Field>
            <Field label="Mặt sàn"><Select value={a.surface} labels={SURFACE_LABEL} onChange={(v) => setAttr('surface', v as GarageAttributes['surface'])} /></Field>
            <Field label="Phòng cháy chữa cháy"><Toggle on={!!a.fire_safety} onChange={(v) => setAttr('fire_safety', v)} label={a.fire_safety ? 'Có' : 'Không'} /></Field>
            <Field label="Nhà vệ sinh"><Toggle on={!!a.restroom} onChange={(v) => setAttr('restroom', v)} label={a.restroom ? 'Có' : 'Không'} /></Field>
          </Section>

          <Section title="Giờ mở cửa">
            <Field label="Mở cửa 24/7" wide>
              <Toggle on={!!form.operating_hours.is_24h} onChange={(v) => set('operating_hours', { ...form.operating_hours, is_24h: v })}
                label={form.operating_hours.is_24h ? 'Có' : 'Không'} />
            </Field>
            {!form.operating_hours.is_24h && (
              <div className="sm:col-span-2 space-y-2">
                {DAYS.map(([d, l]) => {
                  const h = hours[d]
                  const closed = !!h?.closed
                  return (
                    <div key={d} className="flex flex-wrap items-center gap-2 text-sm">
                      <span className="w-20 font-medium">{l}</span>
                      <input type="time" disabled={closed} className={cn(input, 'w-28')} value={h?.open || ''} onChange={(e) => setDay(d, { open: e.target.value })} />
                      <span>–</span>
                      <input type="time" disabled={closed} className={cn(input, 'w-28')} value={h?.close || ''} onChange={(e) => setDay(d, { close: e.target.value })} />
                      <label className="flex items-center gap-1 text-xs text-on-surface-variant">
                        <input type="checkbox" checked={closed} onChange={(e) => setDay(d, { closed: e.target.checked })} /> Nghỉ
                      </label>
                    </div>
                  )
                })}
              </div>
            )}
          </Section>
        </div>

        <aside className="bg-surface rounded-2xl border border-outline-variant p-5 space-y-4 lg:sticky lg:top-20">
          <div>
            <p className="text-xs text-on-surface-variant">Trạng thái</p>
            <p className="font-semibold">{GARAGE_STATUS_LABEL[garage.status] ?? garage.status}</p>
          </div>
          <div>
            <p className="text-xs text-on-surface-variant">Cấp tích hợp</p>
            <p className="font-semibold">Cấp {garage.integration_level} · {garage.integration_label}</p>
            {levelDesc && <p className="text-xs text-on-surface-variant mt-0.5">{levelDesc}</p>}
          </div>
          <div>
            <p className="text-xs text-on-surface-variant">Hạng sao</p>
            {garage.grade > 0
              ? <div className="flex items-center gap-2"><Stars value={garage.grade} size={16} /><span className="text-sm">{garage.grade_score}/100</span></div>
              : <p className="text-sm">Chưa kiểm định</p>}
            {garage.grade_assessment?.assessed_at && <p className="text-xs text-on-surface-variant mt-0.5">Kiểm định lúc {formatDateTime(garage.grade_assessment.assessed_at)}</p>}
          </div>
          {garage.badges.length > 0 && <BadgeList badges={garage.badges} />}
          <p className="flex gap-2 text-xs text-on-surface-variant bg-surface-container-low rounded-xl p-3">
            <Info className="w-4 h-4 shrink-0" /> Cấp tích hợp và hạng sao do admin kiểm định, chủ bãi không tự sửa.
          </p>
        </aside>
      </div>

      <div className="fixed bottom-16 md:bottom-0 left-0 md:left-64 right-0 z-30 bg-surface/95 backdrop-blur border-t border-outline-variant px-4 py-3 flex items-center justify-end gap-3">
        {msg && <p className={cn('text-sm mr-auto', msg.ok ? 'text-success' : 'text-error')}>{msg.text}</p>}
        {dirty && <button onClick={() => { setForm(orig); setMsg(null) }} className="px-4 py-2 rounded-full border border-outline-variant text-sm font-semibold">Huỷ thay đổi</button>}
        <button onClick={save} disabled={!dirty || saving} className="flex items-center gap-1.5 px-5 py-2 rounded-full bg-primary text-white text-sm font-semibold disabled:opacity-50">
          <Save className="w-4 h-4" /> {saving ? 'Đang lưu…' : 'Lưu hồ sơ'}
        </button>
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="bg-surface rounded-2xl border border-outline-variant p-5">
      <h2 className="font-bold mb-4">{title}</h2>
      <div className="grid sm:grid-cols-2 gap-4">{children}</div>
    </section>
  )
}

function Field({ label, wide, children }: { label: string; wide?: boolean; children: ReactNode }) {
  return (
    <div className={cn('space-y-1', wide && 'sm:col-span-2')}>
      <p className="text-xs font-semibold text-on-surface-variant">{label}</p>
      {children}
    </div>
  )
}

function Num({ value, onChange, min = 0, max }: { value: number | undefined; onChange: (v: number) => void; min?: number; max?: number }) {
  return <input type="number" min={min} max={max} className={input} value={value ?? 0} onChange={(e) => onChange(Math.max(min, Number(e.target.value) || 0))} />
}

function Select({ value, labels, onChange }: { value: string | undefined; labels: Record<string, string>; onChange: (v: string) => void }) {
  return (
    <select className={input} value={value ?? ''} onChange={(e) => onChange(e.target.value)}>
      {!value && <option value="">Chưa chọn</option>}
      {Object.entries(labels).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
    </select>
  )
}

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button type="button" onClick={() => onChange(!on)} className="flex items-center gap-2 py-1.5">
      <span className={cn('w-10 h-6 rounded-full p-0.5 transition-colors', on ? 'bg-primary' : 'bg-outline-variant')}>
        <span className={cn('block w-5 h-5 rounded-full bg-white transition-transform', on && 'translate-x-4')} />
      </span>
      <span className="text-sm">{label}</span>
    </button>
  )
}
