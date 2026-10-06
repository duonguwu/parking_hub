import { useEffect, useMemo, useState } from 'react'
import {
  PlusCircle, Clock, Moon, CalendarDays, Briefcase, CreditCard, Zap, Droplets, KeyRound,
  Pencil, Trash2, X, Plus, Loader2, Layers, TrendingUp, Tag,
} from 'lucide-react'
import {
  garageApi, formatVnd, UNIT_LABEL,
  type PortalService, type PortalServicesOverview, type Pricing, type PeakRule, type ServiceType,
} from '@/services/api'

const ICONS: Record<string, typeof Clock> = {
  clock: Clock, moon: Moon, 'calendar-days': CalendarDays, briefcase: Briefcase,
  'credit-card': CreditCard, zap: Zap, droplets: Droplets, 'key-round': KeyRound,
}

const CATEGORY_LABEL: Record<string, string> = {
  parking: 'Gửi lượt', subscription: 'Gói định kỳ', addon: 'Dịch vụ kèm',
}

const CATEGORY_STYLE: Record<string, string> = {
  parking: 'bg-blue-50 border-blue-100 text-blue-600',
  subscription: 'bg-violet-50 border-violet-100 text-violet-600',
  addon: 'bg-emerald-50 border-emerald-100 text-emerald-600',
}

const DAY_LABELS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

function ServiceIcon({ name, className }: { name: string; className?: string }) {
  const Icon = ICONS[name] || Clock
  return <Icon className={className} />
}

/** Mô tả bảng giá ngắn gọn cho thẻ dịch vụ. */
function describePricing(p: Pricing, unit: string): string[] {
  if (p.mode === 'flat') {
    const per = p.flat_unit_minutes
      ? p.flat_unit_minutes >= 43200 ? '/ 30 ngày' : p.flat_unit_minutes >= 1440 ? `/ ${p.flat_unit_minutes / 1440} ngày` : `/ ${p.flat_unit_minutes} phút`
      : `/ ${UNIT_LABEL[unit] || 'lượt'}`
    return [`${formatVnd(p.flat_price)} ${per}`]
  }
  const lines = [
    `${p.first_block_minutes} phút đầu: ${formatVnd(p.first_block_price)}`,
    `Mỗi ${p.next_block_minutes} phút tiếp: ${formatVnd(p.next_block_price)}`,
  ]
  if (p.daily_cap) lines.push(`Tối đa ${formatVnd(p.daily_cap)} / ngày`)
  return lines
}

/** Ước tính nhanh phía client (không tính cao điểm) để chủ bãi hình dung khi chỉnh. */
function previewBlock(p: Pricing, minutes: number): number {
  if (p.mode === 'flat') return p.flat_price || 0
  let total = p.first_block_price || 0
  const rest = Math.max(0, minutes - (p.first_block_minutes || 60))
  total += Math.ceil(rest / (p.next_block_minutes || 60)) * (p.next_block_price || 0)
  return p.daily_cap ? Math.min(total, p.daily_cap) : total
}

// ── Editor modal ──────────────────────────────────────────────────

interface EditorProps {
  title: string
  initial: Pricing
  initialNote: string
  unit: string
  saving: boolean
  error: string
  onClose: () => void
  onSave: (pricing: Pricing, note: string) => void
}

function NumberField({ label, value, onChange, suffix, id }: {
  label: string; value: number | null | undefined; onChange: (v: number) => void; suffix?: string; id: string
}) {
  return (
    <label htmlFor={id} className="block">
      <span className="text-xs font-bold text-slate-500">{label}</span>
      <div className="mt-1 flex items-center rounded-xl border border-slate-200 bg-white focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100">
        <input
          id={id} type="number" min={0} value={value ?? ''}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full bg-transparent px-3 py-2.5 text-sm font-bold text-slate-900 outline-none"
        />
        {suffix && <span className="pr-3 text-xs font-bold text-slate-400">{suffix}</span>}
      </div>
    </label>
  )
}

function PricingEditor({ title, initial, initialNote, unit, saving, error, onClose, onSave }: EditorProps) {
  const [p, setP] = useState<Pricing>({ ...initial, peak_rules: [...(initial.peak_rules || [])] })
  const [note, setNote] = useState(initialNote)
  const set = (patch: Partial<Pricing>) => setP((prev) => ({ ...prev, ...patch }))

  const switchMode = (mode: 'block' | 'flat') => {
    if (mode === p.mode) return
    if (mode === 'flat') set({ mode, flat_price: p.flat_price ?? p.first_block_price ?? 0, flat_unit_minutes: p.flat_unit_minutes ?? null })
    else set({
      mode, first_block_minutes: p.first_block_minutes ?? 60, first_block_price: p.first_block_price ?? p.flat_price ?? 0,
      next_block_minutes: p.next_block_minutes ?? 60, next_block_price: p.next_block_price ?? p.flat_price ?? 0,
    })
  }

  const updateRule = (i: number, patch: Partial<PeakRule>) =>
    set({ peak_rules: p.peak_rules.map((r, idx) => (idx === i ? { ...r, ...patch } : r)) })

  const toggleDay = (i: number, d: number) => {
    const days = p.peak_rules[i].days
    updateRule(i, { days: days.includes(d) ? days.filter((x) => x !== d) : [...days, d].sort() })
  }

  const preview = useMemo(() => [60, 180, 480].map((m) => ({ m, v: previewBlock(p, m) })), [p])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white/95 px-8 py-5 backdrop-blur">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-widest text-blue-500">Bảng giá</p>
            <h3 className="text-xl font-black text-slate-900">{title}</h3>
          </div>
          <button id="pricing-close" onClick={onClose} className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label="Đóng">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-8 px-8 py-6">
          {/* Mode */}
          <div className="grid grid-cols-2 gap-3">
            {([
              ['block', 'Theo block thời gian', 'Block đầu + block tiếp theo, có trần ngày'],
              ['flat', 'Trọn gói', 'Một giá cho mỗi lượt / ngày / tháng'],
            ] as const).map(([m, t, d]) => (
              <button
                key={m} id={`pricing-mode-${m}`} onClick={() => switchMode(m)}
                className={`rounded-2xl border-2 p-4 text-left transition-all ${p.mode === m ? 'border-blue-500 bg-blue-50/60' : 'border-slate-100 hover:border-slate-200'}`}
              >
                <p className="font-black text-slate-900">{t}</p>
                <p className="mt-1 text-xs font-medium text-slate-500">{d}</p>
              </button>
            ))}
          </div>

          {p.mode === 'block' ? (
            <div className="grid grid-cols-2 gap-4">
              <NumberField id="pf-first-min" label="Block đầu" suffix="phút" value={p.first_block_minutes} onChange={(v) => set({ first_block_minutes: v })} />
              <NumberField id="pf-first-price" label="Giá block đầu" suffix="đ" value={p.first_block_price} onChange={(v) => set({ first_block_price: v })} />
              <NumberField id="pf-next-min" label="Block tiếp theo" suffix="phút" value={p.next_block_minutes} onChange={(v) => set({ next_block_minutes: v })} />
              <NumberField id="pf-next-price" label="Giá mỗi block tiếp" suffix="đ" value={p.next_block_price} onChange={(v) => set({ next_block_price: v })} />
              <NumberField id="pf-cap" label="Trần mỗi ngày (0 = không trần)" suffix="đ" value={p.daily_cap ?? 0} onChange={(v) => set({ daily_cap: v || null })} />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <NumberField id="pf-flat-price" label="Giá trọn gói" suffix="đ" value={p.flat_price} onChange={(v) => set({ flat_price: v })} />
              <label htmlFor="pf-flat-unit" className="block">
                <span className="text-xs font-bold text-slate-500">Tính theo</span>
                <select
                  id="pf-flat-unit" value={p.flat_unit_minutes ?? 0}
                  onChange={(e) => set({ flat_unit_minutes: Number(e.target.value) || null })}
                  className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-bold text-slate-900 outline-none focus:border-blue-400"
                >
                  <option value={0}>Mỗi lượt (một lần)</option>
                  <option value={1440}>Mỗi 24 giờ</option>
                  <option value={43200}>Mỗi 30 ngày</option>
                </select>
              </label>
            </div>
          )}

          {/* Peak rules */}
          <div>
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="font-black text-slate-900">Giờ cao điểm</p>
                <p className="text-xs font-medium text-slate-500">Nhân hệ số cho block bắt đầu trong khung giờ</p>
              </div>
              <button
                id="pricing-add-peak"
                onClick={() => set({ peak_rules: [...p.peak_rules, { days: [0, 1, 2, 3, 4], start: '17:00', end: '20:00', multiplier: 1.2 }] })}
                className="flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-200"
              >
                <Plus className="h-3.5 w-3.5" /> Thêm khung
              </button>
            </div>
            <div className="space-y-3">
              {p.peak_rules.length === 0 && <p className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-500">Không áp giá cao điểm.</p>}
              {p.peak_rules.map((r, i) => (
                <div key={i} className="rounded-2xl border border-slate-100 bg-slate-50/60 p-4">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {DAY_LABELS.map((d, idx) => (
                      <button
                        key={d} onClick={() => toggleDay(i, idx)}
                        className={`h-8 w-9 rounded-lg text-xs font-bold transition-colors ${r.days.includes(idx) ? 'bg-blue-600 text-white' : 'bg-white text-slate-500 border border-slate-200'}`}
                      >{d}</button>
                    ))}
                    <button onClick={() => set({ peak_rules: p.peak_rules.filter((_, idx) => idx !== i) })} className="ml-auto rounded-lg p-2 text-slate-400 hover:bg-rose-50 hover:text-rose-600" aria-label="Xoá khung">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-3">
                    <input type="time" value={r.start} onChange={(e) => updateRule(i, { start: e.target.value })} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold" />
                    <input type="time" value={r.end} onChange={(e) => updateRule(i, { end: e.target.value })} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold" />
                    <div className="flex items-center rounded-xl border border-slate-200 bg-white">
                      <span className="pl-3 text-xs font-bold text-slate-400">×</span>
                      <input type="number" step={0.1} min={0.5} max={3} value={r.multiplier} onChange={(e) => updateRule(i, { multiplier: Number(e.target.value) })} className="w-full bg-transparent px-2 py-2 text-sm font-bold outline-none" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <label htmlFor="pf-note" className="block">
            <span className="text-xs font-bold text-slate-500">Ghi chú cho khách (ví dụ: khung đêm 18:00 – 07:00)</span>
            <input id="pf-note" value={note} maxLength={200} onChange={(e) => setNote(e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-blue-400" />
          </label>

          {/* Preview */}
          <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-5 text-white">
            <p className="text-[11px] font-bold uppercase tracking-widest text-slate-400">Xem trước (giờ thường, {UNIT_LABEL[unit] || unit})</p>
            <div className="mt-3 grid grid-cols-3 gap-3">
              {preview.map(({ m, v }) => (
                <div key={m}>
                  <p className="text-xs text-slate-400">{p.mode === 'flat' ? 'Một đơn vị' : `Gửi ${m / 60} giờ`}</p>
                  <p className="text-lg font-black">{formatVnd(v)}</p>
                </div>
              ))}
            </div>
          </div>

          {error && <p className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-bold text-rose-700">{error}</p>}
        </div>

        <div className="sticky bottom-0 flex justify-end gap-3 border-t border-slate-100 bg-white px-8 py-4">
          <button onClick={onClose} className="rounded-full px-6 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-100">Huỷ</button>
          <button
            id="pricing-save" disabled={saving} onClick={() => onSave(p, note)}
            className="flex items-center gap-2 rounded-full bg-blue-600 px-6 py-2.5 text-sm font-black text-white shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-60"
          >
            {saving && <Loader2 className="h-4 w-4 animate-spin" />} Lưu bảng giá
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────

type EditorState =
  | { kind: 'edit'; service: PortalService }
  | { kind: 'create'; type: ServiceType }
  | null

export function GarageServices() {
  const [data, setData] = useState<PortalServicesOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [editor, setEditor] = useState<EditorState>(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [showPicker, setShowPicker] = useState(false)

  const load = () => {
    setLoading(true)
    garageApi.services()
      .then((res) => { setData(res); setLoadError('') })
      .catch((e) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const closeEditor = () => { setEditor(null); setSaveError('') }

  const save = async (pricing: Pricing, note: string) => {
    if (!editor) return
    setSaving(true); setSaveError('')
    try {
      if (editor.kind === 'edit') await garageApi.updateService(editor.service.id, { pricing, note })
      else await garageApi.createService({ service_type_code: editor.type.code, pricing, note })
      closeEditor(); load()
    } catch (e: any) {
      setSaveError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const [confirmRemove, setConfirmRemove] = useState<string | null>(null)
  const remove = async (svc: PortalService) => {
    // Bấm lần 1 để hỏi xác nhận, lần 2 mới xoá (không dùng window.confirm)
    if (confirmRemove !== svc.id) { setConfirmRemove(svc.id); return }
    setConfirmRemove(null); setLoadError('')
    try { await garageApi.deleteService(svc.id) } catch (e: any) { setLoadError(e.message) }
    load()
  }

  if (!data && loading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
      </div>
    )
  }

  const grouped = ['parking', 'subscription', 'addon'].map((cat) => ({
    cat, items: (data?.services || []).filter((s) => s.category === cat),
  })).filter((g) => g.items.length)

  return (
    <div className="mx-auto max-w-7xl space-y-10 p-4 sm:p-8 md:p-12">
      <header className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
        <div className="space-y-2">
          <span className="text-[0.6875rem] font-bold uppercase tracking-[0.1em] text-blue-500">Cấu hình bãi</span>
          <h1 className="text-4xl font-black tracking-tighter text-slate-900 md:text-5xl">Dịch vụ &amp; bảng giá</h1>
          <p className="max-w-xl text-sm font-medium text-slate-500">Giá ở đây được dùng để báo giá khi khách đặt chỗ và tính tiền lúc xe ra.</p>
        </div>
        <button
          id="service-add" onClick={() => setShowPicker(true)} disabled={!data?.available_types.length}
          className="flex items-center justify-center gap-2 rounded-full bg-blue-600 px-7 py-3.5 font-bold text-white shadow-lg shadow-blue-600/20 transition-all hover:bg-blue-700 active:scale-95 disabled:opacity-50"
        >
          <PlusCircle className="h-5 w-5" /> Thêm dịch vụ
        </button>
      </header>

      {loadError && <p className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-bold text-rose-700">{loadError}</p>}

      {data?.stats && (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          {[
            { label: 'Dịch vụ đang bật', value: String(data.stats.active_services), icon: Layers },
            { label: 'Lượt đặt 30 ngày', value: data.stats.bookings_30d.toLocaleString('vi-VN'), icon: TrendingUp },
            { label: 'Đặt nhiều nhất', value: data.stats.top_service || '—', icon: Tag },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-7 shadow-sm transition-all hover:border-blue-200">
              <p className="text-[0.6875rem] font-bold uppercase tracking-widest text-slate-500">{label}</p>
              <p className="mt-2 truncate text-3xl font-black text-slate-900">{value}</p>
              <Icon className="pointer-events-none absolute -bottom-4 -right-4 h-28 w-28 opacity-[0.04] transition-transform duration-500 group-hover:scale-110" />
            </div>
          ))}
        </div>
      )}

      {grouped.length === 0 && !loading && (
        <div className="rounded-3xl border-2 border-dashed border-slate-200 p-12 text-center">
          <p className="text-lg font-black text-slate-700">Bãi chưa có dịch vụ nào</p>
          <p className="mt-2 text-sm text-slate-500">Thêm ít nhất "Gửi theo giờ" để khách có thể đặt chỗ.</p>
        </div>
      )}

      {grouped.map(({ cat, items }) => (
        <section key={cat} className="space-y-4">
          <h2 className="text-sm font-black uppercase tracking-widest text-slate-400">{CATEGORY_LABEL[cat]}</h2>
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
            {items.map((svc) => (
              <article key={svc.id} className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:border-blue-300 hover:shadow-md">
                <div className="mb-5 flex items-start justify-between">
                  <div className={`rounded-2xl border p-3.5 ${CATEGORY_STYLE[svc.category] || CATEGORY_STYLE.parking}`}>
                    <ServiceIcon name={svc.icon} className="h-6 w-6" />
                  </div>
                  <div className="flex items-center gap-2">
                    {svc.tags.map((t) => (
                      <span key={t} className="rounded-md border border-emerald-200 bg-emerald-100 px-2 py-1 text-[10px] font-black uppercase text-emerald-800">{t}</span>
                    ))}
                  </div>
                </div>
                <h3 className="text-xl font-black tracking-tight text-slate-900">{svc.name}</h3>
                <p className="mt-1 text-sm font-medium leading-relaxed text-slate-500">{svc.description}</p>

                <ul className="mt-5 flex-grow space-y-2 border-t border-slate-100 pt-4">
                  {describePricing(svc.pricing, svc.unit).map((l) => (
                    <li key={l} className="text-sm font-bold text-slate-800">{l}</li>
                  ))}
                  {svc.pricing.peak_rules.map((r, i) => (
                    <li key={i} className="text-xs font-bold text-amber-700">
                      Cao điểm {r.start}–{r.end} ({r.days.map((d) => DAY_LABELS[d]).join(', ')}) ×{r.multiplier}
                    </li>
                  ))}
                  {svc.note && <li className="text-xs italic text-slate-500">{svc.note}</li>}
                </ul>

                <div className="mt-5 flex items-center justify-between text-xs font-bold text-slate-400">
                  <span>{svc.bookings_30d.toLocaleString('vi-VN')} lượt / 30 ngày</span>
                </div>
                <div className="mt-4 flex gap-2">
                  <button
                    id={`service-edit-${svc.service_type_code}`} onClick={() => setEditor({ kind: 'edit', service: svc })}
                    className="flex flex-1 items-center justify-center gap-2 rounded-full border-2 border-slate-100 py-2.5 text-sm font-bold text-slate-700 transition-all hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                  >
                    <Pencil className="h-4 w-4" /> Sửa giá
                  </button>
                  <button
                    id={`service-remove-${svc.service_type_code}`} onClick={() => remove(svc)}
                    className={confirmRemove === svc.id
                      ? 'rounded-full border-2 border-rose-300 bg-rose-50 px-3.5 text-xs font-bold text-rose-600'
                      : 'rounded-full border-2 border-slate-100 px-3.5 text-slate-400 transition-all hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600'}
                    aria-label="Ngừng dịch vụ"
                  >
                    {confirmRemove === svc.id ? 'Bấm lần nữa để ngừng' : <Trash2 className="h-4 w-4" />}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ))}

      {/* Picker */}
      {showPicker && data && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
          <div className="w-full max-w-xl rounded-3xl bg-white p-8 shadow-2xl">
            <div className="mb-6 flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">Chọn dịch vụ để thêm</h3>
              <button onClick={() => setShowPicker(false)} className="rounded-full p-2 text-slate-400 hover:bg-slate-100" aria-label="Đóng"><X className="h-5 w-5" /></button>
            </div>
            <div className="grid gap-3">
              {data.available_types.map((t) => (
                <button
                  key={t.code} id={`service-pick-${t.code}`}
                  onClick={() => { setShowPicker(false); setEditor({ kind: 'create', type: t }) }}
                  className="flex items-center gap-4 rounded-2xl border border-slate-100 p-4 text-left transition-all hover:border-blue-300 hover:bg-blue-50/50"
                >
                  <div className={`rounded-xl border p-3 ${CATEGORY_STYLE[t.category]}`}><ServiceIcon name={t.icon} className="h-5 w-5" /></div>
                  <div className="flex-1">
                    <p className="font-black text-slate-900">{t.name}</p>
                    <p className="text-xs text-slate-500">{t.description}</p>
                  </div>
                  <span className="whitespace-nowrap text-xs font-bold text-slate-400">
                    {formatVnd(t.base_price_min)} – {formatVnd(t.base_price_max)}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {editor && (
        <PricingEditor
          title={editor.kind === 'edit' ? editor.service.name : editor.type.name}
          initial={editor.kind === 'edit' ? editor.service.pricing : editor.type.default_pricing}
          initialNote={editor.kind === 'edit' ? editor.service.note : ''}
          unit={editor.kind === 'edit' ? editor.service.unit : editor.type.unit}
          saving={saving} error={saveError} onClose={closeEditor} onSave={save}
        />
      )}
    </div>
  )
}
