import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { garageApi, formatVnd, formatDuration, BOOKING_STATUS_MAP, type PortalAnalytics, type BookingStatus } from '@/services/api'
import { BarChart, BookingStatusBadge, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

type Range = '7D' | '30D' | '90D'
const RANGES: { key: Range; label: string }[] = [{ key: '7D', label: '7 ngày' }, { key: '30D', label: '30 ngày' }, { key: '90D', label: '90 ngày' }]
const box = 'bg-surface rounded-2xl border border-outline-variant p-5'
const hasAny = (arr: number[]) => arr.some((v) => v > 0)

export function GarageAnalytics() {
  const [range, setRange] = useState<Range>('30D')
  const [data, setData] = useState<PortalAnalytics | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    garageApi.analytics(range).then((d) => { setData(d); setError('') }).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [range])

  const m = data?.metrics
  const totalSource = data ? data.source_split.app + data.source_split.walk_in : 0
  const statusEntries = data ? (Object.entries(data.booking_status) as [BookingStatus, number][]).filter(([, n]) => n > 0) : []
  const statusTotal = statusEntries.reduce((s, [, n]) => s + n, 0)

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Phân tích</h1>
        <div className="flex bg-surface border border-outline-variant rounded-full p-0.5 text-sm font-semibold">
          {RANGES.map((r) => (
            <button key={r.key} onClick={() => setRange(r.key)}
              className={cn('px-3 py-1 rounded-full', range === r.key ? 'bg-primary text-white' : 'text-on-surface-variant')}>{r.label}</button>
          ))}
        </div>
      </div>

      {error && <EmptyState title="Không tải được phân tích" desc={error} />}
      {!data && loading && <Spinner />}

      {data && m && (
        <div className={cn('space-y-5', loading && 'opacity-60')}>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Metric label="Doanh thu" value={formatVnd(m.revenue.value)} trend={m.revenue.trend} />
            <Metric label="Lượt gửi xe" value={m.sessions.value.toLocaleString('vi-VN')} trend={m.sessions.trend} />
            <Metric label="Thời gian gửi trung bình" value={m.avg_duration_minutes ? formatDuration(m.avg_duration_minutes) : '—'} />
            <Metric label="Giá trị trung bình / lượt" value={m.avg_ticket ? formatVnd(m.avg_ticket) : '—'} />
          </div>

          <div className={box}>
            <h2 className="font-bold mb-4">Doanh thu theo ngày</h2>
            {hasAny(data.revenue_chart.data)
              ? <BarChart labels={data.revenue_chart.labels} values={data.revenue_chart.data} height={150} format={formatVnd} />
              : <EmptyState title="Chưa có doanh thu trong khoảng này" />}
          </div>

          <div className={box}>
            <h2 className="font-bold mb-4">Lấp đầy theo giờ</h2>
            {hasAny(data.occupancy_by_hour.weekday) || hasAny(data.occupancy_by_hour.weekend) ? (
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <p className="text-xs font-semibold text-on-surface-variant mb-2">Ngày thường</p>
                  <BarChart labels={data.occupancy_by_hour.labels} values={data.occupancy_by_hour.weekday} format={(v) => `${Math.round(v)}%`} />
                </div>
                <div>
                  <p className="text-xs font-semibold text-on-surface-variant mb-2">Cuối tuần</p>
                  <BarChart labels={data.occupancy_by_hour.labels} values={data.occupancy_by_hour.weekend} format={(v) => `${Math.round(v)}%`} />
                </div>
              </div>
            ) : <EmptyState title="Chưa có dữ liệu lấp đầy" />}
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div className={box}>
              <h2 className="font-bold mb-3">Nguồn khách</h2>
              {totalSource === 0 ? <EmptyState title="Chưa có lượt nào" className="py-4" /> : (
                <div className="space-y-3">
                  <div className="flex h-3 rounded-full overflow-hidden bg-surface-container-low">
                    <div className="bg-primary" style={{ width: `${(data.source_split.app / totalSource) * 100}%` }} />
                    <div className="bg-warning" style={{ width: `${(data.source_split.walk_in / totalSource) * 100}%` }} />
                  </div>
                  <Row dot="bg-primary" label="Đặt qua ứng dụng" value={data.source_split.app} total={totalSource} />
                  <Row dot="bg-warning" label="Xe vãng lai" value={data.source_split.walk_in} total={totalSource} />
                </div>
              )}
            </div>

            <div className={box}>
              <h2 className="font-bold mb-3">Khách hàng</h2>
              {data.customers.total === 0 ? <EmptyState title="Chưa có khách đặt qua ứng dụng" className="py-4" /> : (
                <div className="space-y-2">
                  <p className="text-3xl font-bold">{data.customers.total.toLocaleString('vi-VN')}</p>
                  <p className="text-sm text-on-surface-variant">
                    {data.customers.returning} khách quay lại ({Math.round((data.customers.returning / data.customers.total) * 100)}%)
                  </p>
                </div>
              )}
            </div>

            <div className={box}>
              <h2 className="font-bold mb-3">Trạng thái lượt đặt</h2>
              {statusTotal === 0 ? <EmptyState title="Chưa có lượt đặt" className="py-4" /> : (
                <ul className="space-y-2">
                  {statusEntries.map(([s, n]) => (
                    <li key={s} className="flex items-center justify-between text-sm">
                      <BookingStatusBadge status={s} />
                      <span className="font-semibold" title={BOOKING_STATUS_MAP[s]?.label}>{n} <span className="text-xs text-on-surface-variant font-normal">({Math.round((n / statusTotal) * 100)}%)</span></span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className={box}>
            <h2 className="font-bold mb-3">Theo dịch vụ</h2>
            {data.services.length === 0 ? <EmptyState title="Chưa có lượt sử dụng dịch vụ" /> : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-on-surface-variant border-b border-outline-variant">
                      <th className="py-2 font-semibold">Dịch vụ</th>
                      <th className="py-2 font-semibold text-right">Số lượt</th>
                      <th className="py-2 font-semibold text-right">Doanh thu</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.services.map((s) => (
                      <tr key={s.code} className="border-b border-outline-variant last:border-0">
                        <td className="py-2">{s.name}</td>
                        <td className="py-2 text-right">{s.count.toLocaleString('vi-VN')}</td>
                        <td className="py-2 text-right font-semibold">{formatVnd(s.revenue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function Metric({ label, value, trend }: { label: string; value: string; trend?: number | null }) {
  return (
    <div className={cn(box, 'p-4')}>
      <p className="text-xs font-semibold text-on-surface-variant">{label}</p>
      <p className="text-xl md:text-2xl font-bold mt-1 break-words">{value}</p>
      {trend !== undefined && (
        trend === null
          ? <p className="text-[11px] text-on-surface-variant mt-1">Chưa có kỳ trước để so sánh</p>
          : <p className={cn('text-xs font-semibold mt-1 flex items-center gap-1', trend >= 0 ? 'text-success' : 'text-error')}>
              {trend >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              {trend >= 0 ? '+' : ''}{trend}% so với kỳ trước
            </p>
      )}
    </div>
  )
}

function Row({ dot, label, value, total }: { dot: string; label: string; value: number; total: number }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="flex items-center gap-2"><span className={cn('w-2.5 h-2.5 rounded-full', dot)} />{label}</span>
      <span className="font-semibold">{value} <span className="text-xs text-on-surface-variant font-normal">({Math.round((value / total) * 100)}%)</span></span>
    </div>
  )
}
