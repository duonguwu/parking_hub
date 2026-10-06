import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle2, BadgeCheck } from 'lucide-react'
import { adminApi, GARAGE_STATUS_LABEL, INTEGRATION_LABEL, LOT_TYPE_LABEL, formatDateTime, type AdminGarageList } from '@/services/api'
import { Card } from '@/components/ui/card'
import { AvailabilityPill, EmptyState, Spinner, Stars } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const STATUS_TONE: Record<string, string> = {
  active: 'bg-success/10 text-success', pending_review: 'bg-warning/10 text-warning', suspended: 'bg-error/10 text-error',
}
const sel = 'text-xs border border-outline-variant rounded-full px-3 py-1.5 bg-surface'

export function AdminGarages() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const status = params.get('status') ?? ''
  const [level, setLevel] = useState('')
  const [lotType, setLotType] = useState('')
  const [district, setDistrict] = useState('')
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<AdminGarageList | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  useEffect(() => { const t = setTimeout(() => { setQuery(q); setPage(1) }, 350); return () => clearTimeout(t) }, [q])
  useEffect(() => {
    setError('')
    adminApi.garages({ status: status || undefined, level: level ? Number(level) : undefined, lot_type: lotType || undefined,
      district: district || undefined, q: query || undefined, page, limit: 20 })
      .then(setData).catch((e) => setError(e.message))
  }, [status, level, lotType, district, query, page, tick])

  const setStatus = (v: string) => { const p = new URLSearchParams(params); v ? p.set('status', v) : p.delete('status'); setParams(p); setPage(1) }
  const approve = async (id: string) => {
    setBusy(id)
    try { await adminApi.updateGarage(id, { status: 'active' }); setTick((t) => t + 1) } catch (e: any) { setError(e.message) } finally { setBusy(null) }
  }
  const pg = data?.pagination

  return (
    <div className="p-4 md:p-8 space-y-4 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">Bãi đỗ</h1>
        <p className="text-sm text-on-surface-variant">{pg ? `${pg.total_items} bãi` : 'Đang tải…'}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm tên, địa chỉ, mã tenant…" className={cn(sel, 'w-full sm:w-64')} />
        <select className={sel} value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Mọi trạng thái</option>
          {Object.entries(GARAGE_STATUS_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select className={sel} value={level} onChange={(e) => { setLevel(e.target.value); setPage(1) }}>
          <option value="">Mọi cấp</option>
          {Object.entries(INTEGRATION_LABEL).map(([k, v]) => <option key={k} value={k}>Cấp {k} · {v}</option>)}
        </select>
        <select className={sel} value={lotType} onChange={(e) => { setLotType(e.target.value); setPage(1) }}>
          <option value="">Mọi loại bãi</option>
          {Object.entries(LOT_TYPE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select className={sel} value={district} onChange={(e) => { setDistrict(e.target.value); setPage(1) }}>
          <option value="">Mọi quận</option>
          {(data?.districts ?? []).map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>
      {error && <p className="text-sm text-error">{error}</p>}
      {!data ? <div className="p-10 flex justify-center"><Spinner /></div> : data.items.length === 0 ? <EmptyState title="Không có bãi phù hợp" desc="Thử bỏ bớt bộ lọc." /> : (
        <Card className="p-0 overflow-x-auto">
          <table className="w-full text-sm min-w-[960px]">
            <thead className="text-xs text-on-surface-variant text-left border-b border-outline-variant">
              <tr>{['Bãi đỗ', 'Loại', 'Cấp', 'Hạng', 'Trạng thái', 'Xác minh', 'Số chỗ', 'Chỗ trống', 'Kiểm định tới', ''].map((h) => <th key={h} className="px-3 py-2 font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {data.items.map((g) => (
                <tr key={g.id} onClick={() => navigate(`/admin/garages/${g.id}`)} className="border-b border-outline-variant last:border-0 hover:bg-surface-container-low cursor-pointer">
                  <td className="px-3 py-2 max-w-[240px]"><p className="font-semibold truncate">{g.name}</p><p className="text-xs text-on-surface-variant truncate">{g.address}</p></td>
                  <td className="px-3 py-2 text-xs">{g.lot_type_label || LOT_TYPE_LABEL[g.lot_type]}</td>
                  <td className="px-3 py-2 text-xs whitespace-nowrap">Cấp {g.integration_level}</td>
                  <td className="px-3 py-2"><Stars value={g.grade} /></td>
                  <td className="px-3 py-2"><span className={cn('text-xs px-2 py-0.5 rounded-full whitespace-nowrap', STATUS_TONE[g.status])}>{GARAGE_STATUS_LABEL[g.status] ?? g.status}</span></td>
                  <td className="px-3 py-2">{g.is_verified ? <BadgeCheck className="w-4 h-4 text-success" /> : <span className="text-xs text-on-surface-variant">—</span>}</td>
                  <td className="px-3 py-2">{g.total_spots}</td>
                  <td className="px-3 py-2"><AvailabilityPill a={g.availability} level={g.integration_level} /></td>
                  <td className="px-3 py-2 text-xs whitespace-nowrap">{g.next_inspection_at ? formatDateTime(g.next_inspection_at) : '—'}</td>
                  <td className="px-3 py-2" onClick={(e) => e.stopPropagation()}>
                    {g.status === 'pending_review' && (
                      <button disabled={busy === g.id} onClick={() => approve(g.id)} className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-success rounded-full px-3 py-1 disabled:opacity-50">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Duyệt
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {pg && pg.total_pages > 1 && (
        <div className="flex items-center justify-center gap-3 text-sm">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="px-3 py-1 rounded-full border border-outline-variant disabled:opacity-40">Trước</button>
          <span>Trang {pg.current_page}/{pg.total_pages}</span>
          <button disabled={page >= pg.total_pages} onClick={() => setPage(page + 1)} className="px-3 py-1 rounded-full border border-outline-variant disabled:opacity-40">Sau</button>
        </div>
      )}
    </div>
  )
}
