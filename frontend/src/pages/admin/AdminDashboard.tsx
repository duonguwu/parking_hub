import { useEffect, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import { adminApi, formatVnd, ROLE_LABEL, type AdminOverview } from '@/services/api'
import { Card } from '@/components/ui/card'
import { BarChart, EmptyState, Spinner, Stars } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const pct = (v: number) => `${Math.round(v * 1000) / 10}%`

function Kpi({ label, value, sub, tone }: { label: string; value: string; sub?: string; tone?: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-on-surface-variant">{label}</p>
      <p className={cn('text-xl font-bold mt-1', tone)}>{value}</p>
      {sub && <p className="text-[11px] text-on-surface-variant mt-0.5">{sub}</p>}
    </Card>
  )
}

function HBars({ title, rows }: { title: string; rows: { label: ReactNode; count: number; key: string }[] }) {
  const max = Math.max(1, ...rows.map((r) => r.count))
  return (
    <Card className="p-4">
      <h3 className="font-semibold text-sm mb-3">{title}</h3>
      {rows.length === 0 || rows.every((r) => !r.count) ? <p className="text-xs text-on-surface-variant">Chưa có dữ liệu</p> : (
        <div className="space-y-2">
          {rows.map((r) => (
            <div key={r.key} className="text-xs">
              <div className="flex justify-between mb-0.5"><span className="truncate">{r.label}</span><span className="font-semibold">{r.count}</span></div>
              <div className="h-1.5 bg-surface-container-low rounded-full"><div className="h-full bg-primary rounded-full" style={{ width: `${(r.count / max) * 100}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

export function AdminDashboard() {
  const [data, setData] = useState<AdminOverview | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { adminApi.overview().then(setData).catch((e) => setError(e.message)) }, [])

  if (error) return <div className="p-6"><EmptyState title="Không tải được dữ liệu" desc={error} /></div>
  if (!data) return <div className="p-10 flex justify-center"><Spinner /></div>
  const g = data.garages
  const hasDaily = data.daily.some((d) => d.bookings || d.revenue)
  const users = Object.entries(data.users).sort((a, b) => b[1] - a[1])

  return (
    <div className="p-4 md:p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Tổng quan mạng lưới</h1>
          <p className="text-sm text-on-surface-variant">{g.total} bãi đỗ trên toàn hệ thống</p>
        </div>
        {g.pending_review > 0 && (
          <Link to="/admin/garages?status=pending_review" className="inline-flex items-center gap-2 text-sm font-semibold text-warning bg-warning/10 px-4 py-2 rounded-full">
            <AlertCircle className="w-4 h-4" /> {g.pending_review} bãi chờ duyệt
          </Link>
        )}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Kpi label="Bãi đang hoạt động" value={String(g.active)} tone="text-success" />
        <Kpi label="Bãi chờ duyệt" value={String(g.pending_review)} tone={g.pending_review ? 'text-warning' : undefined} />
        <Kpi label="Bãi tạm ngưng" value={String(g.suspended)} tone={g.suspended ? 'text-error' : undefined} />
        <Kpi label="Tổng số chỗ" value={data.spots.total.toLocaleString('vi-VN')} />
        <Kpi label="Lấp đầy toàn mạng" value={data.spots.network_occupancy == null ? 'Chưa có dữ liệu' : pct(data.spots.network_occupancy)}
          sub={`${data.spots.tracked_lots} bãi có cập nhật chỗ trống`} />
        <Kpi label="Lượt đặt 30 ngày" value={data.bookings_30d.toLocaleString('vi-VN')} />
        <Kpi label="Doanh thu 30 ngày" value={formatVnd(data.revenue_30d)} />
        <Kpi label="Tỉ lệ giữ đúng chỗ" value={data.bookings_30d ? pct(data.fulfillment_30d) : 'Chưa có dữ liệu'} sub="30 ngày qua" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="font-semibold text-sm mb-3">Lượt đặt theo ngày</h3>
          {hasDaily ? <BarChart labels={data.daily.map((d) => d.date)} values={data.daily.map((d) => d.bookings)} /> : <p className="text-xs text-on-surface-variant">Chưa có lượt đặt</p>}
        </Card>
        <Card className="p-4">
          <h3 className="font-semibold text-sm mb-3">Doanh thu theo ngày</h3>
          {hasDaily ? <BarChart labels={data.daily.map((d) => d.date)} values={data.daily.map((d) => d.revenue)} format={formatVnd} /> : <p className="text-xs text-on-surface-variant">Chưa có doanh thu</p>}
        </Card>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <HBars title="Theo quận" rows={data.by_district.map((r) => ({ key: r.name, label: r.name || 'Chưa rõ', count: r.count }))} />
        <HBars title="Theo cấp kết nối" rows={data.by_level.map((r) => ({ key: String(r.level), label: `Cấp ${r.level} · ${r.label}`, count: r.count }))} />
        <HBars title="Theo loại bãi" rows={data.by_type.map((r) => ({ key: r.code, label: r.label, count: r.count }))} />
        <HBars title="Theo hạng sao" rows={[...data.by_grade].reverse().map((r) => ({ key: String(r.grade), label: <Stars value={r.grade} />, count: r.count }))} />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="font-semibold text-sm mb-3">Bãi nhiều lượt gửi nhất (30 ngày)</h3>
          {data.top_garages.length === 0 ? <p className="text-xs text-on-surface-variant">Chưa có dữ liệu</p> : (
            <ol className="space-y-2 text-sm">
              {data.top_garages.map((t, i) => (
                <li key={t.id} className="flex justify-between gap-2">
                  <Link to={`/admin/garages/${t.id}`} className="truncate hover:text-primary">{i + 1}. {t.name || '—'}</Link>
                  <span className="font-semibold shrink-0">{t.sessions} lượt</span>
                </li>
              ))}
            </ol>
          )}
        </Card>
        <HBars title="Người dùng theo vai trò" rows={users.map(([k, v]) => ({ key: k, label: ROLE_LABEL[k] ?? k, count: v }))} />
      </div>
    </div>
  )
}
