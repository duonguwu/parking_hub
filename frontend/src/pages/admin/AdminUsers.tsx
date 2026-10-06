import { useEffect, useState } from 'react'
import { adminApi, ROLE_LABEL, type AdminUser, type Pagination } from '@/services/api'
import { Card } from '@/components/ui/card'
import { EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const sel = 'text-xs border border-outline-variant rounded-full px-3 py-1.5 bg-surface'

export function AdminUsers() {
  const [role, setRole] = useState('')
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [items, setItems] = useState<AdminUser[] | null>(null)
  const [pg, setPg] = useState<Pagination | null>(null)
  const [error, setError] = useState('')
  const [rowErr, setRowErr] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState<string | null>(null)

  useEffect(() => { const t = setTimeout(() => { setQuery(q); setPage(1) }, 350); return () => clearTimeout(t) }, [q])
  useEffect(() => {
    setError('')
    adminApi.users({ role: role || undefined, q: query || undefined, page, limit: 20 })
      .then((r) => { setItems(r.items); setPg(r.pagination) }).catch((e) => setError(e.message))
  }, [role, query, page])

  const toggle = async (u: AdminUser) => {
    setBusy(u.id); setRowErr((m) => ({ ...m, [u.id]: '' }))
    try {
      const r = await adminApi.setUserActive(u.id, !u.is_active)
      setItems((list) => list?.map((x) => (x.id === u.id ? { ...x, is_active: r.is_active } : x)) ?? null)
    } catch (e: any) { setRowErr((m) => ({ ...m, [u.id]: e.message })) } finally { setBusy(null) }
  }

  return (
    <div className="p-4 md:p-8 space-y-4 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">Người dùng</h1>
        <p className="text-sm text-on-surface-variant">{pg ? `${pg.total_items} tài khoản` : 'Đang tải…'}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm tên, tài khoản, email, SĐT…" className={cn(sel, 'w-full sm:w-64')} />
        <select className={sel} value={role} onChange={(e) => { setRole(e.target.value); setPage(1) }}>
          <option value="">Mọi vai trò</option>
          {Object.entries(ROLE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      {error && <p className="text-sm text-error">{error}</p>}
      {!items ? <div className="p-10 flex justify-center"><Spinner /></div> : items.length === 0 ? <EmptyState title="Không có người dùng phù hợp" /> : (
        <Card className="p-0 overflow-x-auto">
          <table className="w-full text-sm min-w-[820px]">
            <thead className="text-xs text-on-surface-variant text-left border-b border-outline-variant">
              <tr>{['Họ tên', 'Tài khoản', 'Email', 'Điện thoại', 'Vai trò', 'Bãi', 'Trạng thái'].map((h) => <th key={h} className="px-3 py-2 font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {items.map((u) => (
                <tr key={u.id} className="border-b border-outline-variant last:border-0 align-top">
                  <td className="px-3 py-2 font-semibold">{u.name || '—'}</td>
                  <td className="px-3 py-2">{u.username}</td>
                  <td className="px-3 py-2 text-xs">{u.email || '—'}</td>
                  <td className="px-3 py-2 text-xs">{u.phone || '—'}</td>
                  <td className="px-3 py-2 text-xs whitespace-nowrap">{ROLE_LABEL[u.role] ?? u.role}</td>
                  <td className="px-3 py-2 text-xs">{u.garage_name || '—'}</td>
                  <td className="px-3 py-2">
                    <button disabled={busy === u.id} onClick={() => toggle(u)}
                      className={cn('text-xs font-semibold rounded-full px-3 py-1 whitespace-nowrap disabled:opacity-50', u.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error')}>
                      {u.is_active ? 'Đang hoạt động · Khoá' : 'Đã khoá · Mở khoá'}
                    </button>
                    {rowErr[u.id] && <p className="text-[11px] text-error mt-1 max-w-[180px]">{rowErr[u.id]}</p>}
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
