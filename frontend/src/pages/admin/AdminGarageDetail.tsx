import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, BadgeCheck, Wand2 } from 'lucide-react'
import {
  adminApi, COVER_LABEL, CCTV_LABEL, FLOOD_LABEL, GARAGE_STATUS_LABEL, GUARD_LABEL, LOT_TYPE_LABEL, formatDateTime,
  type AdminGarageDetail as Detail, type AdminMeta, type GarageCard,
} from '@/services/api'
import { Card } from '@/components/ui/card'
import { ParkingMap } from '@/components/parking/ParkingMap'
import { AvailabilityPill, BadgeList, EmptyState, Spinner, Stars } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const STATUS_TONE: Record<string, string> = {
  active: 'bg-success/10 text-success', pending_review: 'bg-warning/10 text-warning', suspended: 'bg-error/10 text-error',
}
const gradeOf = (s: number) => (s >= 85 ? 5 : s >= 70 ? 4 : s >= 55 ? 3 : s >= 40 ? 2 : 1)

function Row({ k, v }: { k: string; v: ReactNode }) {
  return <div className="flex justify-between gap-3 py-1 text-sm"><span className="text-on-surface-variant">{k}</span><span className="text-right">{v === '' || v == null || v === false ? '—' : v}</span></div>
}

export function AdminGarageDetail() {
  const { id = '' } = useParams()
  const [d, setD] = useState<Detail | null>(null)
  const [meta, setMeta] = useState<AdminMeta | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [confirmSuspend, setConfirmSuspend] = useState(false)
  const [items, setItems] = useState<Record<string, boolean>>({})
  const [note, setNote] = useState('')

  const load = (r: Detail) => {
    setD(r)
    const a = r.garage.grade_assessment
    setItems(a?.items && Object.keys(a.items).length ? { ...a.items } : { ...r.suggested_checklist })
    setNote(a?.note ?? '')
  }
  useEffect(() => {
    Promise.all([adminApi.garage(id), adminApi.meta()]).then(([r, m]) => { load(r); setMeta(m) }).catch((e) => setError(e.message))
  }, [id])

  const preview = useMemo(() => {
    const score = (meta?.grade_checklist ?? []).reduce((s, c) => s + (items[c.key] ? c.points : 0), 0)
    return { score, grade: gradeOf(score) }
  }, [items, meta])

  if (error && !d) return <div className="p-6"><EmptyState title="Không tải được bãi" desc={error} /></div>
  if (!d || !meta) return <div className="p-10 flex justify-center"><Spinner /></div>
  const g = d.garage
  const at = g.attributes ?? {}

  const update = async (data: Parameters<typeof adminApi.updateGarage>[1], ok: string) => {
    setBusy(true); setError(''); setMsg('')
    try { load(await adminApi.updateGarage(id, data)); setMsg(ok) } catch (e: any) { setError(e.message) } finally { setBusy(false); setConfirmSuspend(false) }
  }
  const save = async () => {
    setBusy(true); setError(''); setMsg('')
    try { load(await adminApi.saveAssessment(id, items, note)); setMsg('Đã lưu kết quả kiểm định') } catch (e: any) { setError(e.message) } finally { setBusy(false) }
  }
  const card: GarageCard = {
    id: g.id, name: g.name, position: g.position, address: g.address.street ?? '', district: g.address.district ?? '',
    lot_type: g.lot_type, lot_type_label: g.lot_type_label, integration_level: g.integration_level, grade: g.grade,
    quality_score: g.quality_score, cover: at.cover ?? 'open', max_height_m: at.max_height_m ?? null, ev_count: at.ev_chargers?.count ?? 0,
    guard: at.guard ?? 'none', flood_risk: at.flood_risk ?? 'none', hourly_price: null, distance_km: null, is_24h: false,
    availability: g.availability ?? { has_data: false, total_spots: g.capacity.total_spots, occupied: null, held: null, available: null, occupancy_rate: null, status: 'unknown', source: '', updated_at: null },
    badges: g.badges, status: g.status, is_accepting_bookings: g.is_accepting_bookings,
  }
  const address = [g.address.street, g.address.ward, g.address.district, g.address.city].filter(Boolean).join(', ')
  const btn = 'text-sm font-semibold rounded-full px-4 py-2 disabled:opacity-50'

  return (
    <div className="p-4 md:p-8 space-y-4 max-w-6xl mx-auto">
      <Link to="/admin/garages" className="inline-flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary"><ArrowLeft className="w-4 h-4" /> Danh sách bãi</Link>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">{g.name}{g.is_verified && <BadgeCheck className="w-5 h-5 text-success" />}</h1>
          <p className="text-sm text-on-surface-variant">{address}</p>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className={cn('text-xs px-2 py-0.5 rounded-full', STATUS_TONE[g.status])}>{GARAGE_STATUS_LABEL[g.status] ?? g.status}</span>
            <Stars value={g.grade} /><span className="text-xs text-on-surface-variant">{g.grade_score}/100 điểm</span>
            <AvailabilityPill a={g.availability} level={g.integration_level} showTime />
          </div>
          <BadgeList badges={g.badges} className="mt-2" />
        </div>
        <div className="flex flex-wrap gap-2">
          {g.status !== 'active' && <button disabled={busy} onClick={() => update({ status: 'active' }, 'Đã chuyển sang hoạt động')} className={cn(btn, 'bg-success text-white')}>{g.status === 'pending_review' ? 'Duyệt' : 'Mở lại'}</button>}
          {g.status === 'active' && !confirmSuspend && <button disabled={busy} onClick={() => setConfirmSuspend(true)} className={cn(btn, 'border border-error text-error')}>Tạm ngưng</button>}
          {confirmSuspend && (
            <div className="flex items-center gap-2 text-sm">
              <span>Tạm ngưng bãi này?</span>
              <button disabled={busy} onClick={() => update({ status: 'suspended' }, 'Đã tạm ngưng bãi')} className={cn(btn, 'bg-error text-white')}>Xác nhận</button>
              <button onClick={() => setConfirmSuspend(false)} className={cn(btn, 'border border-outline-variant')}>Huỷ</button>
            </div>
          )}
        </div>
      </div>
      {(msg || error) && <p className={cn('text-sm', error ? 'text-error' : 'text-success')}>{error || msg}</p>}

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="p-4 lg:col-span-2">
          <h3 className="font-semibold mb-2">Thông tin bãi</h3>
          <div className="grid sm:grid-cols-2 gap-x-6">
            <div>
              <Row k="Loại bãi" v={g.lot_type_label || LOT_TYPE_LABEL[g.lot_type]} />
              <Row k="Tổng số chỗ" v={g.capacity.total_spots} />
              <Row k="Chỗ vãng lai / tháng" v={`${g.capacity.walk_in_spots} / ${g.capacity.monthly_spots}`} />
              <Row k="Tỉ lệ cho đặt trước" v={`${Math.round((g.capacity.reservable_ratio ?? 0) * 100)}%`} />
              <Row k="Thời gian ân hạn" v={`${g.capacity.grace_minutes} phút`} />
              <Row k="Mái che" v={at.cover && COVER_LABEL[at.cover]} />
              <Row k="Chiều cao tối đa" v={at.max_height_m ? `${at.max_height_m} m` : ''} />
            </div>
            <div>
              <Row k="Bảo vệ" v={at.guard && GUARD_LABEL[at.guard] + (at.guard_hours ? ` (${at.guard_hours})` : '')} />
              <Row k="Camera" v={at.cctv && CCTV_LABEL[at.cctv]} />
              <Row k="Ngập nước" v={at.flood_risk && FLOOD_LABEL[at.flood_risk]} />
              <Row k="Sạc xe điện" v={at.ev_chargers?.count ? `${at.ev_chargers.count} trụ` : ''} />
              <Row k="Liên hệ" v={[g.contacts.manager_name, g.contacts.phone].filter(Boolean).join(' · ')} />
              <Row k="Chủ bãi" v={d.owner && [d.owner.name, d.owner.phone || d.owner.email].filter(Boolean).join(' · ')} />
              <Row k="Đơn vị (tenant)" v={d.tenant?.name} />
            </div>
          </div>
          <h3 className="font-semibold mt-4 mb-1">Hiệu quả</h3>
          <div className="grid sm:grid-cols-2 gap-x-6">
            <Row k="Tổng lượt gửi" v={g.stats.total_sessions ?? 0} />
            <Row k="Đánh giá" v={g.stats.rating_count ? `${g.stats.avg_rating?.toFixed(1)} (${g.stats.rating_count})` : 'Chưa có'} />
            <Row k="Giữ đúng chỗ" v={g.stats.fulfillment_rate != null ? `${Math.round(g.stats.fulfillment_rate * 100)}%` : 'Chưa có'} />
            <Row k="Khiếu nại" v={String(g.stats.complaint_count ?? 0)} />
          </div>
        </Card>
        <Card className="p-0 overflow-hidden min-h-[260px]">
          {g.position ? <ParkingMap garages={[card]} selectedId={g.id} center={g.position} zoom={16} className="h-full min-h-[260px] w-full" /> : <EmptyState title="Chưa có toạ độ" className="p-6" />}
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="font-semibold mb-3">Cấp kết nối</h3>
          <div className="space-y-2">
            {meta.integration_levels.map((l) => (
              <button key={l.level} disabled={busy || l.level === g.integration_level}
                onClick={() => update({ integration_level: l.level }, `Đã chuyển sang cấp ${l.level}`)}
                className={cn('w-full text-left p-3 rounded-lg border', l.level === g.integration_level ? 'border-primary bg-primary/5' : 'border-outline-variant hover:bg-surface-container-low')}>
                <p className="text-sm font-semibold">Cấp {l.level} · {l.name}</p>
                <p className="text-xs text-on-surface-variant">{l.desc}</p>
              </button>
            ))}
          </div>
        </Card>
        <Card className="p-4 space-y-3">
          <h3 className="font-semibold">Vận hành</h3>
          <label className="flex items-center justify-between gap-3 text-sm">
            <span>Nhận đặt chỗ qua ứng dụng</span>
            <input type="checkbox" disabled={busy} checked={g.is_accepting_bookings}
              onChange={(e) => update({ is_accepting_bookings: e.target.checked }, e.target.checked ? 'Đã mở nhận đặt chỗ' : 'Đã ngừng nhận đặt chỗ')} className="w-5 h-5 accent-primary" />
          </label>
          <Row k="Kiểm định gần nhất" v={g.grade_assessment?.assessed_at ? `${formatDateTime(g.grade_assessment.assessed_at)}${g.grade_assessment.assessed_by ? ` · ${g.grade_assessment.assessed_by}` : ''}` : 'Chưa kiểm định'} />
          <Row k="Kiểm định tiếp theo" v={g.next_inspection_at ? formatDateTime(g.next_inspection_at) : 'Chưa lên lịch'} />
          <Row k="Ngày tạo" v={g.created_at ? formatDateTime(g.created_at) : ''} />
        </Card>
      </div>

      <Card className="p-4 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold">Phiếu kiểm định</h3>
            <p className="text-xs text-on-surface-variant">Thang 100 điểm · 5★ ≥85 · 4★ ≥70 · 3★ ≥55 · 2★ ≥40</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold">{preview.score}/100</span><Stars value={preview.grade} size={16} />
            <button onClick={() => setItems({ ...d.suggested_checklist })} className="inline-flex items-center gap-1 text-xs font-semibold text-primary border border-primary rounded-full px-3 py-1.5">
              <Wand2 className="w-3.5 h-3.5" /> Dùng gợi ý từ thuộc tính
            </button>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {meta.grade_groups.map((grp) => {
            const list = meta.grade_checklist.filter((c) => c.group === grp.key)
            const max = list.reduce((s, c) => s + c.points, 0)
            const got = list.reduce((s, c) => s + (items[c.key] ? c.points : 0), 0)
            return (
              <div key={grp.key} className="border border-outline-variant rounded-lg p-3">
                <div className="flex justify-between text-sm font-semibold mb-2"><span>{grp.label}</span><span>{got}/{max}</span></div>
                {list.map((c) => (
                  <label key={c.key} className="flex items-start gap-2 py-1 text-sm cursor-pointer">
                    <input type="checkbox" className="mt-0.5 accent-primary" checked={!!items[c.key]} onChange={(e) => setItems({ ...items, [c.key]: e.target.checked })} />
                    <span className="flex-1">{c.label}</span><span className="text-xs text-on-surface-variant">{c.points}đ</span>
                  </label>
                ))}
              </div>
            )
          })}
        </div>
        <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={3} placeholder="Ghi chú kiểm định…" className="w-full text-sm border border-outline-variant rounded-lg p-3 bg-surface" />
        <div className="flex flex-wrap items-center gap-3">
          <button disabled={busy} onClick={save} className={cn(btn, 'bg-primary text-white')}>Lưu kết quả kiểm định</button>
          <span className="text-xs text-on-surface-variant">Lưu sẽ cập nhật hạng sao, đánh dấu đã xác minh và đặt lịch kiểm định tiếp theo.</span>
        </div>
      </Card>
    </div>
  )
}
