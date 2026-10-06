import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { SlidersHorizontal, List, Map as MapIcon, Crosshair, X, Search, Navigation } from 'lucide-react'
import { customerApi, formatVnd, formatTime, LOT_TYPE_LABEL, type GarageCard, type LatLng, type LotType, type NearbyFilters } from '@/services/api'
import { ParkingMap, MapLegend, HCM_CENTER } from '@/components/parking/ParkingMap'
import { Stars, AvailabilityPill, BadgeList, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { cn } from '@/services/utils'

const DEFAULT_FILTERS: NearbyFilters = { radius_km: 3 }

/** Dòng mô tả cập nhật chỗ trống theo cấp tích hợp. */
function freshness(g: GarageCard): string | null {
  if (g.integration_level >= 3) return g.availability?.has_data ? 'Thời gian thực' : null
  if (g.integration_level === 2 && g.availability?.updated_at) return `Cập nhật lúc ${formatTime(g.availability.updated_at)}`
  return null
}

export function GarageCardView({ g, active, onClick }: { g: GarageCard; active?: boolean; onClick?: () => void }) {
  const fresh = freshness(g)
  return (
    <div onClick={onClick} className={cn('p-3 rounded-2xl border bg-surface cursor-pointer transition-colors',
      active ? 'border-primary' : 'border-outline-variant hover:border-primary/50')}>
      <div className="flex justify-between gap-2">
        <Link to={`/app/garages/${g.id}`} className="text-sm font-bold text-on-surface hover:text-primary line-clamp-1">{g.name}</Link>
        {g.distance_km != null && <span className="text-[11px] text-on-surface-variant whitespace-nowrap">{g.distance_km.toFixed(1)} km</span>}
      </div>
      <p className="text-[11px] text-on-surface-variant line-clamp-1">{g.address}</p>
      <div className="flex flex-wrap items-center gap-1.5 mt-1.5 text-[11px] text-on-surface-variant">
        {g.grade > 0 && <Stars value={g.grade} />}
        <span>· {g.lot_type_label}</span>
        {fresh && <span>· {fresh}</span>}
      </div>
      <BadgeList badges={g.badges} max={3} className="mt-1.5" />
      <div className="flex items-center justify-between mt-2">
        <AvailabilityPill a={g.availability} level={g.integration_level} />
        <span className="text-xs font-bold text-on-surface">
          {g.hourly_price != null ? `${formatVnd(g.hourly_price)}/giờ` : <span className="font-normal text-on-surface-variant">Chưa có giá giờ</span>}
        </span>
      </div>
    </div>
  )
}

function Toggle({ on, label, onChange }: { on: boolean; label: string; onChange: (v: boolean) => void }) {
  return (
    <button type="button" onClick={() => onChange(!on)}
      className={cn('px-3 py-1.5 rounded-full border text-xs font-semibold', on ? 'bg-primary text-white border-primary' : 'border-outline-variant text-on-surface-variant')}>
      {label}
    </button>
  )
}

function FiltersPanel({ value, onApply, onClose }: { value: NearbyFilters; onApply: (f: NearbyFilters) => void; onClose: () => void }) {
  const [f, setF] = useState<NearbyFilters>(value)
  const set = (patch: Partial<NearbyFilters>) => setF((p) => ({ ...p, ...patch }))
  const toggleType = (t: LotType) => {
    const cur = f.lot_types ?? []
    set({ lot_types: cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t] })
  }
  const input = 'w-full h-10 rounded-xl border border-outline-variant bg-surface px-3 text-sm outline-none focus:border-primary'
  return (
    <div className="absolute inset-0 z-[1100] bg-black/40 flex justify-end" onClick={onClose}>
      <div className="w-full max-w-sm h-full bg-surface overflow-y-auto p-4 space-y-4" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-on-surface">Bộ lọc</h2>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-surface-container-low"><X className="w-5 h-5" /></button>
        </div>
        <label className="block text-xs font-semibold text-on-surface-variant">Bán kính: {f.radius_km ?? 3} km
          <input type="range" min={0.5} max={15} step={0.5} value={f.radius_km ?? 3} onChange={(e) => set({ radius_km: +e.target.value })} className="w-full" />
        </label>
        <div>
          <p className="text-xs font-semibold text-on-surface-variant mb-1.5">Loại bãi</p>
          <div className="flex flex-wrap gap-1.5">
            {(Object.keys(LOT_TYPE_LABEL) as LotType[]).map((t) => (
              <Toggle key={t} on={!!f.lot_types?.includes(t)} label={LOT_TYPE_LABEL[t]} onChange={() => toggleType(t)} />
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-1.5">
          <Toggle on={!!f.covered} label="Có mái che / hầm" onChange={(v) => set({ covered: v })} />
          <Toggle on={!!f.ev} label="Có sạc EV" onChange={(v) => set({ ev: v })} />
          <Toggle on={!!f.guard_24h} label="Bảo vệ 24/7" onChange={(v) => set({ guard_24h: v })} />
          <Toggle on={!!f.no_flood} label="Không ngập" onChange={(v) => set({ no_flood: v })} />
          <Toggle on={!!f.only_available} label="Chỉ bãi còn chỗ" onChange={(v) => set({ only_available: v })} />
          <Toggle on={!!f.is_24h} label="Mở 24h" onChange={(v) => set({ is_24h: v })} />
        </div>
        <div>
          <p className="text-xs font-semibold text-on-surface-variant mb-1.5">Hạng sao tối thiểu</p>
          <div className="flex gap-1.5">
            {[0, 1, 2, 3, 4, 5].map((n) => (
              <Toggle key={n} on={(f.min_grade ?? 0) === n} label={n === 0 ? 'Tất cả' : `Từ ${n}★`} onChange={() => set({ min_grade: n })} />
            ))}
          </div>
        </div>
        <label className="block text-xs font-semibold text-on-surface-variant">Chiều cao xe (m)
          <input type="number" step={0.1} min={0} className={input} value={f.min_height_m ?? ''}
            onChange={(e) => set({ min_height_m: e.target.value ? +e.target.value : null })} placeholder="VD: 2.1" />
        </label>
        <label className="block text-xs font-semibold text-on-surface-variant">Giá giờ tối đa (đ)
          <input type="number" step={1000} min={0} className={input} value={f.max_hourly_price ?? ''}
            onChange={(e) => set({ max_hourly_price: e.target.value ? +e.target.value : null })} placeholder="VD: 30000" />
        </label>
        <div className="flex gap-2 pt-2">
          <button onClick={() => setF(DEFAULT_FILTERS)} className="flex-1 h-10 rounded-full border border-outline-variant text-sm font-semibold">Xoá lọc</button>
          <button onClick={() => onApply(f)} className="flex-1 h-10 rounded-full bg-primary text-white text-sm font-bold">Áp dụng</button>
        </div>
      </div>
    </div>
  )
}

export function CustomerMap() {
  const [point, setPoint] = useState<LatLng>(HCM_CENTER)
  const [filters, setFilters] = useState<NearbyFilters>(DEFAULT_FILTERS)
  const [q, setQ] = useState('')
  const [garages, setGarages] = useState<GarageCard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<GarageCard | null>(null)
  const [flyTo, setFlyTo] = useState<LatLng | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [mobileList, setMobileList] = useState(false)
  const [pending, setPending] = useState<LatLng | null>(null)

  const locate = () => navigator.geolocation?.getCurrentPosition((p) => {
    const ll = { lat: p.coords.latitude, lng: p.coords.longitude }
    setPoint(ll); setFlyTo(ll)
  })
  useEffect(() => { locate() }, [])

  useEffect(() => {
    setLoading(true); setError('')
    const t = setTimeout(() => {
      customerApi.nearbyGarages(point.lat, point.lng, { ...filters, q: q.trim() || undefined })
        .then(setGarages).catch((e) => { setGarages([]); setError(e.message) }).finally(() => setLoading(false))
    }, q ? 350 : 0)
    return () => clearTimeout(t)
  }, [point, filters, q])

  const activeCount = Object.entries(filters).filter(([k, v]) =>
    k !== 'radius_km' && v !== undefined && v !== null && v !== false && v !== 0 && !(Array.isArray(v) && !v.length)).length

  const select = (g: GarageCard) => { setSelected(g); if (g.position) setFlyTo(g.position) }

  const list = (
    <div className="space-y-2">
      {loading ? <Spinner /> : error ? <EmptyState title="Không tải được bãi đỗ" desc={error} />
        : garages.length === 0 ? <EmptyState title="Không có bãi phù hợp" desc="Thử nới rộng bán kính hoặc bỏ bớt bộ lọc." />
        : garages.map((g) => <GarageCardView key={g.id} g={g} active={g.id === selected?.id} onClick={() => { select(g); setMobileList(false) }} />)}
    </div>
  )

  return (
    <div className="relative flex h-[calc(100vh-4rem-4.5rem)] md:h-[calc(100vh-76px)]">
      <aside className="hidden md:flex w-[380px] shrink-0 flex-col border-r border-outline-variant bg-background">
        <div className="p-3 border-b border-outline-variant text-xs text-on-surface-variant">
          {loading ? 'Đang tìm…' : `${garages.length} bãi trong bán kính ${filters.radius_km ?? 3} km`}
        </div>
        <div className="flex-1 overflow-y-auto p-3">{list}</div>
      </aside>

      <div className="relative flex-1">
        <ParkingMap
          garages={garages} selectedId={selected?.id} onSelect={select} center={point} searchPoint={point} flyTo={flyTo}
          onMapClick={(p) => setPending(p)}
          renderPopup={(g) => (
            <div className="min-w-[180px]">
              <p className="font-bold text-sm">{g.name}</p>
              <AvailabilityPill a={g.availability} level={g.integration_level} className="mt-1" />
              <Link to={`/app/garages/${g.id}`} className="block mt-2 text-xs font-bold text-primary">Xem chi tiết & đặt chỗ →</Link>
            </div>
          )}
        />

        <div className="absolute top-3 left-3 right-3 z-[1000] flex gap-2">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm tên bãi, đường…"
              className="w-full h-10 rounded-full bg-surface border border-outline-variant pl-9 pr-3 text-sm outline-none focus:border-primary shadow" />
          </div>
          <button onClick={() => setShowFilters(true)} className="h-10 px-3 rounded-full bg-surface border border-outline-variant shadow flex items-center gap-1.5 text-xs font-bold">
            <SlidersHorizontal className="w-4 h-4" /> Lọc{activeCount > 0 && <span className="bg-primary text-white rounded-full px-1.5">{activeCount}</span>}
          </button>
          <button onClick={locate} title="Vị trí của tôi" className="h-10 w-10 rounded-full bg-surface border border-outline-variant shadow flex items-center justify-center">
            <Navigation className="w-4 h-4" />
          </button>
        </div>

        {pending && (
          <div className="absolute top-16 left-1/2 -translate-x-1/2 z-[1000] flex gap-1 bg-surface rounded-full shadow border border-outline-variant p-1">
            <button onClick={() => { setPoint(pending); setPending(null) }} className="px-3 py-1.5 rounded-full bg-primary text-white text-xs font-bold flex items-center gap-1">
              <Crosshair className="w-3.5 h-3.5" /> Tìm quanh điểm này
            </button>
            <button onClick={() => setPending(null)} className="p-1.5"><X className="w-4 h-4" /></button>
          </div>
        )}

        <div className="absolute bottom-3 left-3 z-[1000] bg-surface/90 rounded-xl px-2.5 py-1.5 border border-outline-variant hidden sm:block">
          <MapLegend />
        </div>

        {selected && !mobileList && (
          <div className="md:hidden absolute bottom-16 left-3 right-3 z-[1000]">
            <GarageCardView g={selected} active />
          </div>
        )}

        <button onClick={() => setMobileList((v) => !v)}
          className="md:hidden absolute bottom-3 left-1/2 -translate-x-1/2 z-[1001] h-10 px-4 rounded-full bg-on-surface text-white text-xs font-bold flex items-center gap-1.5 shadow">
          {mobileList ? <><MapIcon className="w-4 h-4" /> Xem bản đồ</> : <><List className="w-4 h-4" /> Danh sách ({garages.length})</>}
        </button>

        {mobileList && <div className="md:hidden absolute inset-0 z-[1000] bg-background overflow-y-auto p-3 pt-16 pb-16">{list}</div>}
      </div>

      {showFilters && <FiltersPanel value={filters} onClose={() => setShowFilters(false)} onApply={(f) => { setFilters(f); setShowFilters(false) }} />}
    </div>
  )
}
