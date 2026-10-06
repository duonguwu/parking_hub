import { useEffect, useState, type ChangeEvent } from 'react'
import { Plus } from 'lucide-react'
import { adminApi, formatVnd, UNIT_LABEL, type ServiceType } from '@/services/api'
import { Card } from '@/components/ui/card'
import { EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const CATEGORY_LABEL: Record<string, string> = { parking: 'Gửi xe', subscription: 'Gói tháng', addon: 'Dịch vụ kèm' }
const UNITS = ['hour', 'night', 'day', 'workday', 'month', 'session']
const inp = 'text-sm border border-outline-variant rounded-lg px-3 py-1.5 bg-surface w-full'

type Form = { code: string; name: string; description: string; category: ServiceType['category']; unit: string;
  base_price_min: number; base_price_max: number; is_popular: boolean; sort_order: number }
const EMPTY: Form = { code: '', name: '', description: '', category: 'parking', unit: 'hour', base_price_min: 0, base_price_max: 0, is_popular: false, sort_order: 100 }

function Fields({ f, set, withCode }: { f: Form; set: (f: Form) => void; withCode?: boolean }) {
  const num = (k: keyof Form) => (e: ChangeEvent<HTMLInputElement>) => set({ ...f, [k]: Number(e.target.value) || 0 })
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
      {withCode && <label>Mã<input className={inp} value={f.code} onChange={(e) => set({ ...f, code: e.target.value.trim() })} placeholder="vd: hourly_parking" /></label>}
      <label>Tên<input className={inp} value={f.name} onChange={(e) => set({ ...f, name: e.target.value })} /></label>
      <label>Nhóm<select className={inp} value={f.category} onChange={(e) => set({ ...f, category: e.target.value as Form['category'] })}>
        {Object.entries(CATEGORY_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
      <label>Đơn vị<select className={inp} value={f.unit} onChange={(e) => set({ ...f, unit: e.target.value })}>
        {UNITS.map((u) => <option key={u} value={u}>{UNIT_LABEL[u] ?? u}</option>)}</select></label>
      <label>Giá thấp nhất (đ)<input type="number" min={0} className={inp} value={f.base_price_min} onChange={num('base_price_min')} /></label>
      <label>Giá cao nhất (đ)<input type="number" min={0} className={inp} value={f.base_price_max} onChange={num('base_price_max')} /></label>
      <label>Thứ tự<input type="number" className={inp} value={f.sort_order} onChange={num('sort_order')} /></label>
      <label className="flex items-center gap-2 pt-4"><input type="checkbox" className="accent-primary" checked={f.is_popular} onChange={(e) => set({ ...f, is_popular: e.target.checked })} /> Phổ biến</label>
      <label className="sm:col-span-2 lg:col-span-4">Mô tả<textarea rows={2} className={inp} value={f.description} onChange={(e) => set({ ...f, description: e.target.value })} /></label>
    </div>
  )
}

export function AdminServices() {
  const [list, setList] = useState<ServiceType[] | null>(null)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState<Form>(EMPTY)
  const [editing, setEditing] = useState<string | null>(null)
  const [edit, setEdit] = useState<Form>(EMPTY)
  const [busy, setBusy] = useState(false)

  const load = () => adminApi.serviceTypes().then((r) => setList([...r].sort((a, b) => a.sort_order - b.sort_order))).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const run = async (fn: () => Promise<unknown>, after?: () => void) => {
    setBusy(true); setError('')
    try { await fn(); after?.(); await load() } catch (e: any) { setError(e.message) } finally { setBusy(false) }
  }
  const { code: _c, ...editBody } = edit
  void _c

  return (
    <div className="p-4 md:p-8 space-y-4 max-w-7xl mx-auto">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Danh mục dịch vụ</h1>
          <p className="text-sm text-on-surface-variant">Loại dịch vụ dùng chung cho các bãi trong mạng lưới</p>
        </div>
        {!creating && <button onClick={() => { setForm(EMPTY); setCreating(true) }} className="inline-flex items-center gap-1 text-sm font-semibold bg-primary text-white rounded-full px-4 py-2"><Plus className="w-4 h-4" /> Thêm dịch vụ</button>}
      </div>
      {error && <p className="text-sm text-error">{error}</p>}
      {creating && (
        <Card className="p-4 space-y-3">
          <h3 className="font-semibold">Dịch vụ mới</h3>
          <Fields f={form} set={setForm} withCode />
          <div className="flex gap-2">
            <button disabled={busy || !form.code || !form.name} onClick={() => run(() => adminApi.createServiceType(form), () => setCreating(false))} className="text-sm font-semibold bg-primary text-white rounded-full px-4 py-2 disabled:opacity-50">Tạo</button>
            <button onClick={() => setCreating(false)} className="text-sm rounded-full px-4 py-2 border border-outline-variant">Huỷ</button>
          </div>
        </Card>
      )}
      {!list ? <div className="p-10 flex justify-center"><Spinner /></div> : list.length === 0 ? <EmptyState title="Chưa có dịch vụ nào" /> : (
        <Card className="p-0 overflow-x-auto">
          <table className="w-full text-sm min-w-[860px]">
            <thead className="text-xs text-on-surface-variant text-left border-b border-outline-variant">
              <tr>{['Mã', 'Tên', 'Nhóm', 'Đơn vị', 'Khoảng giá', 'Phổ biến', 'Thứ tự', 'Hiển thị', ''].map((h) => <th key={h} className="px-3 py-2 font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {list.map((s) => editing === s.code ? (
                <tr key={s.code} className="border-b border-outline-variant"><td colSpan={9} className="p-3 space-y-3">
                  <p className="text-xs font-mono text-on-surface-variant">{s.code}</p>
                  <Fields f={edit} set={setEdit} />
                  <div className="flex gap-2">
                    <button disabled={busy || !edit.name} onClick={() => run(() => adminApi.updateServiceType(s.code, editBody), () => setEditing(null))} className="text-xs font-semibold bg-primary text-white rounded-full px-3 py-1.5 disabled:opacity-50">Lưu</button>
                    <button onClick={() => setEditing(null)} className="text-xs rounded-full px-3 py-1.5 border border-outline-variant">Huỷ</button>
                  </div>
                </td></tr>
              ) : (
                <tr key={s.code} className={cn('border-b border-outline-variant last:border-0', s.is_active === false && 'opacity-50')}>
                  <td className="px-3 py-2 font-mono text-xs">{s.code}</td>
                  <td className="px-3 py-2"><p className="font-semibold">{s.name}</p>{s.description && <p className="text-xs text-on-surface-variant line-clamp-1">{s.description}</p>}</td>
                  <td className="px-3 py-2 text-xs">{CATEGORY_LABEL[s.category] ?? s.category}</td>
                  <td className="px-3 py-2 text-xs">{UNIT_LABEL[s.unit] ?? s.unit}</td>
                  <td className="px-3 py-2 text-xs whitespace-nowrap">{s.base_price_min || s.base_price_max ? `${formatVnd(s.base_price_min)} – ${formatVnd(s.base_price_max)}` : '—'}</td>
                  <td className="px-3 py-2 text-xs">{s.is_popular ? 'Có' : '—'}</td>
                  <td className="px-3 py-2 text-xs">{s.sort_order}</td>
                  <td className="px-3 py-2">
                    <button disabled={busy} onClick={() => run(() => adminApi.updateServiceType(s.code, { is_active: s.is_active === false }))}
                      className={cn('text-xs font-semibold rounded-full px-3 py-1 whitespace-nowrap', s.is_active === false ? 'bg-surface-container-low text-on-surface-variant' : 'bg-success/10 text-success')}>
                      {s.is_active === false ? 'Đang ẩn · Hiện' : 'Đang hiện · Ẩn'}
                    </button>
                  </td>
                  <td className="px-3 py-2">
                    <button onClick={() => { setEditing(s.code); setEdit({ code: s.code, name: s.name, description: s.description ?? '', category: s.category, unit: s.unit,
                      base_price_min: s.base_price_min, base_price_max: s.base_price_max, is_popular: s.is_popular, sort_order: s.sort_order }) }}
                      className="text-xs font-semibold text-primary">Sửa</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
