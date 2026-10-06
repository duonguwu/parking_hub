// Các mẩu hiển thị nhỏ dùng chung cho mọi vai trò.
import { Star, ShieldCheck, Building2, Flame, Radio, Zap, BadgeCheck } from 'lucide-react'
import {
  AVAILABILITY_META, BOOKING_STATUS_MAP, STATUS_COLOR_CLASS, formatTime,
  type Availability, type Badge, type BookingStatus,
} from '@/services/api'
import { cn } from '@/services/utils'

export function Stars({ value, size = 12, className }: { value: number; size?: number; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-0.5', className)} aria-label={`${value} sao`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <Star key={i} style={{ width: size, height: size }}
          className={i <= value ? 'fill-warning text-warning' : 'text-outline-variant'} />
      ))}
    </span>
  )
}

/** Chỗ trống: "12 chỗ trống" + mốc cập nhật, hoặc "Chưa có dữ liệu chỗ trống" với bãi cấp 1. */
export function AvailabilityPill({ a, level, showTime = false, className }: {
  a: Availability | null | undefined; level?: number; showTime?: boolean; className?: string
}) {
  const status = a?.status ?? 'unknown'
  const meta = AVAILABILITY_META[status]
  let text: string
  if (!a?.has_data) text = level === 1 ? 'Chưa có dữ liệu chỗ trống' : 'Chưa cập nhật'
  else if (status === 'full') text = 'Hết chỗ'
  else text = `${a.available} chỗ trống`
  return (
    <span className={cn('inline-flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-full', meta.color, className)}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: meta.hex }} />
      {text}
      {showTime && a?.has_data && a.updated_at && (
        <span className="font-normal opacity-80">· {a.source === 'simulated' || a.source === 'camera' ? 'trực tiếp' : `lúc ${formatTime(a.updated_at)}`}</span>
      )}
    </span>
  )
}

const BADGE_ICON: Record<string, typeof Star> = {
  verified: BadgeCheck, purpose_built: Building2, fire_safe: Flame, realtime: Radio, ev: Zap, reliable: ShieldCheck,
}

export function BadgeList({ badges, max, className }: { badges: Badge[]; max?: number; className?: string }) {
  const list = max ? badges.slice(0, max) : badges
  if (!list.length) return null
  return (
    <div className={cn('flex flex-wrap gap-1', className)}>
      {list.map((b) => {
        const Icon = BADGE_ICON[b.key] ?? BadgeCheck
        return (
          <span key={b.key} className="inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded bg-primary/10 text-primary">
            <Icon className="w-3 h-3" /> {b.label}
          </span>
        )
      })}
    </div>
  )
}

export function BookingStatusBadge({ status, className }: { status: BookingStatus | string; className?: string }) {
  const meta = BOOKING_STATUS_MAP[status as BookingStatus] ?? { label: status, color: 'gray' }
  return (
    <span className={cn('inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap', STATUS_COLOR_CLASS[meta.color], className)}>
      {meta.label}
    </span>
  )
}

/** Khối trạng thái rỗng / lỗi / đang tải — thay cho số liệu bịa. */
export function EmptyState({ title, desc, className }: { title: string; desc?: string; className?: string }) {
  return (
    <div className={cn('text-center py-10 px-4', className)}>
      <p className="text-sm font-semibold text-on-surface">{title}</p>
      {desc && <p className="text-xs text-on-surface-variant mt-1">{desc}</p>}
    </div>
  )
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={cn('flex justify-center py-10', className)}>
      <div className="w-7 h-7 border-[3px] border-primary/20 border-t-primary rounded-full animate-spin" />
    </div>
  )
}

/** Thanh cột đơn giản (không dùng thư viện chart). values 0..100, null = không có dữ liệu. */
export function BarChart({ labels, values, height = 120, highlight, format, className }: {
  labels: string[]; values: (number | null)[]; height?: number; highlight?: number
  format?: (v: number) => string; className?: string
}) {
  const max = Math.max(1, ...values.map((v) => v ?? 0))
  const step = Math.ceil(labels.length / 8)
  return (
    <div className={cn('w-full', className)}>
      <div className="flex items-end gap-[2px]" style={{ height }}>
        {values.map((v, i) => (
          <div key={i} className="flex-1 flex flex-col justify-end h-full group relative">
            <div
              className={cn('w-full rounded-t-sm transition-colors',
                v === null ? 'bg-surface-container-low' : i === highlight ? 'bg-primary' : 'bg-primary/40 group-hover:bg-primary/70')}
              style={{ height: v === null ? 2 : `${Math.max(2, (v / max) * 100)}%` }}
            />
            {v !== null && (
              <span className="pointer-events-none absolute -top-6 left-1/2 -translate-x-1/2 hidden group-hover:block text-[10px] font-semibold bg-on-surface text-white px-1.5 py-0.5 rounded whitespace-nowrap z-10">
                {labels[i]}: {format ? format(v) : v}
              </span>
            )}
          </div>
        ))}
      </div>
      <div className="flex gap-[2px] mt-1">
        {labels.map((l, i) => (
          <span key={i} className="flex-1 text-[9px] text-on-surface-variant text-center truncate">{i % step === 0 ? l : ''}</span>
        ))}
      </div>
    </div>
  )
}
