import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, Lightbulb, CalendarClock } from 'lucide-react'
import { garageApi, formatDateTime, type PortalScore } from '@/services/api'
import { Stars, BadgeList, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const box = 'bg-surface rounded-2xl border border-outline-variant p-5'
const pct = (v?: number) => (v == null ? '—' : `${Math.round(v * 100)}%`)

export function GarageScore() {
  const [data, setData] = useState<PortalScore | null>(null)
  const [error, setError] = useState('')

  useEffect(() => { garageApi.score().then(setData).catch((e) => setError(e.message)) }, [])

  if (!data) return error ? <div className="p-6"><EmptyState title="Không tải được điểm chất lượng" desc={error} /></div> : <Spinner />

  const s = data.stats
  const g = data.grade
  const groups = Array.from(new Set(g.items.map((i) => i.group)))
  const groupLabel = Object.fromEntries(g.groups.map((x) => [x.key, x.label]))

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-5">
      <h1 className="text-2xl font-bold">Chất lượng bãi</h1>

      <div className="grid md:grid-cols-3 gap-4">
        <div className={box}>
          <p className="text-xs font-semibold text-on-surface-variant uppercase">Điểm chất lượng vận hành</p>
          {data.has_enough_data ? (
            <p className="text-5xl font-black mt-2">{Math.round(data.quality_score)}<span className="text-lg text-on-surface-variant font-semibold">/100</span></p>
          ) : (
            <p className="text-lg font-semibold mt-3 text-on-surface-variant">Chưa đủ dữ liệu</p>
          )}
          <p className="text-xs text-on-surface-variant mt-2">Tính từ tỉ lệ giữ chỗ, khiếu nại, khách quay lại và đánh giá.</p>
        </div>

        <div className={box}>
          <p className="text-xs font-semibold text-on-surface-variant uppercase">Cấp tích hợp</p>
          <p className="text-xl font-bold mt-2">Cấp {data.integration.level} · {data.integration.name}</p>
          {data.integration.desc && <p className="text-sm text-on-surface-variant mt-1">{data.integration.desc}</p>}
        </div>

        <div className={box}>
          <p className="text-xs font-semibold text-on-surface-variant uppercase">Hạng sao cơ sở vật chất</p>
          {g.stars > 0 ? (
            <div className="flex items-center gap-2 mt-2"><Stars value={g.stars} size={20} /><span className="font-bold">{g.score}/100</span></div>
          ) : <p className="text-lg font-semibold mt-2 text-on-surface-variant">Chưa kiểm định</p>}
          {g.assessed_at && <p className="text-xs text-on-surface-variant mt-2">Kiểm định lúc {formatDateTime(g.assessed_at)}</p>}
          {data.next_inspection_at && (
            <p className="text-xs text-on-surface-variant mt-1 flex items-center gap-1">
              <CalendarClock className="w-3.5 h-3.5" /> Kiểm định lại: {new Date(data.next_inspection_at).toLocaleDateString('vi-VN')}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatBox label="Tỉ lệ giữ chỗ thành công" value={pct(s.fulfillment_rate)} />
        <StatBox label="Tỉ lệ khách không đến" value={pct(s.no_show_rate)} />
        <StatBox label="Khách quay lại" value={pct(s.return_rate)} />
        <StatBox label="Khiếu nại" value={s.complaint_count == null ? '—' : String(s.complaint_count)} />
        <StatBox label="Đánh giá trung bình" value={s.avg_rating ? `${s.avg_rating.toFixed(1)}/5` : '—'}
          hint={s.rating_count ? `${s.rating_count} lượt đánh giá` : undefined} />
      </div>

      {data.badges.length > 0 && (
        <div className={box}>
          <h2 className="font-bold mb-3">Huy hiệu</h2>
          <BadgeList badges={data.badges} />
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-4">
        <div className={cn(box, 'lg:col-span-2')}>
          <h2 className="font-bold mb-4">Kết quả kiểm định</h2>
          {g.groups.length > 0 && (
            <div className="space-y-2 mb-5">
              {g.groups.map((x) => (
                <div key={x.key}>
                  <div className="flex justify-between text-xs mb-1"><span>{x.label}</span><span className="font-semibold">{x.score}/{x.max}</span></div>
                  <div className="h-2 rounded-full bg-surface-container-low overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${x.max ? (x.score / x.max) * 100 : 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
          {g.items.length === 0 ? <EmptyState title="Chưa có kết quả kiểm định" /> : groups.map((grp) => (
            <div key={grp} className="mb-4 last:mb-0">
              <p className="text-xs font-semibold text-on-surface-variant uppercase mb-1.5">{groupLabel[grp] ?? grp}</p>
              <ul className="space-y-1">
                {g.items.filter((i) => i.group === grp).map((i) => (
                  <li key={i.key} className="flex items-start gap-2 text-sm">
                    {i.passed ? <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" /> : <XCircle className="w-4 h-4 text-outline-variant shrink-0 mt-0.5" />}
                    <span className={cn('flex-1', !i.passed && 'text-on-surface-variant')}>{i.label}</span>
                    <span className="text-xs text-on-surface-variant">{i.points} điểm</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {g.note && <p className="text-xs text-on-surface-variant mt-4 bg-surface-container-low rounded-xl p-3">Ghi chú kiểm định: {g.note}</p>}
        </div>

        <div className={box}>
          <h2 className="font-bold mb-3 flex items-center gap-2"><Lightbulb className="w-4 h-4 text-warning" /> Gợi ý cải thiện</h2>
          {data.tips.length === 0 ? <EmptyState title="Chưa có gợi ý" className="py-4" /> : (
            <ul className="space-y-2 text-sm list-disc pl-4">
              {data.tips.map((t, i) => <li key={i}>{t}</li>)}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className={cn(box, 'p-4')}>
      <p className="text-[11px] font-semibold text-on-surface-variant">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
      {hint && <p className="text-[11px] text-on-surface-variant">{hint}</p>}
    </div>
  )
}
