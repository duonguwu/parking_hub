import { useEffect, useMemo, useRef, type ReactNode } from 'react'
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet'
import L from 'leaflet'
import { X, FastForward } from 'lucide-react'
import { CARTO_TILE_URL } from '@/components/parking/ParkingMap'
import { RouteCameraList } from '@/components/traffic-camera/RouteCameraList'
import type { LatLng, MatchCandidatePin, MatchResult } from '@/services/api'
import { type MatchStageName } from './useMatchChoreography'

const STAGE_LABEL: Record<MatchStageName, string> = {
  searching: 'Đang xác định vị trí và tìm bãi...',
  candidates: 'Tìm các bãi quanh bạn',
  filtering: 'Loại bãi không phù hợp',
  routing: 'Tính đường đi tới các bãi tốt nhất',
  analyzing: 'Kiểm tra tình trạng đường đi',
  ranking: 'Xếp hạng đề xuất',
  result: '',
}

const ROUTE_COLORS = { win: '#16a34a', other: '#3b82f6', dim: '#9ca3af' }
const USER_ICON = L.divIcon({ className: '', html: '<div class="mc-user"></div>', iconSize: [18, 18], iconAnchor: [9, 9] })
const stageIdx = (s: MatchStageName) => ['searching', 'candidates', 'filtering', 'routing', 'analyzing', 'ranking', 'result'].indexOf(s)

/** Điều khiển camera bản đồ theo từng trạng thái. */
function StageCamera({ stage, origin, spread, routes }: {
  stage: MatchStageName
  origin: LatLng
  spread: LatLng[]
  routes: [number, number][][]
}) {
  const map = useMap()
  useEffect(() => {
    const narrow = window.innerWidth < 640
    if (stage === 'searching') {
      map.flyTo([origin.lat, origin.lng], 15, { duration: 0.8 })
    } else if (stage === 'candidates' && spread.length) {
      const b = L.latLngBounds([[origin.lat, origin.lng], ...spread.map((p) => [p.lat, p.lng] as [number, number])])
      map.flyToBounds(b, { padding: [50, 50], duration: 0.9, maxZoom: 16 })
    } else if ((stage === 'routing' || stage === 'result') && routes.length) {
      const pts = routes.flat()
      const bottom = stage === 'result' ? (narrow ? 330 : 60) : 60
      const right = stage === 'result' && !narrow ? 420 : 40
      map.flyToBounds(L.latLngBounds(pts), {
        paddingTopLeft: [40, 70], paddingBottomRight: [right, bottom], duration: 0.9, maxZoom: 17,
      })
    }
  }, [stage])
  return null
}

/** Marker bãi: bật tắt class để có transition, không dựng lại DOM. */
function CandidateDots({ candidates, rejected, stage }: {
  candidates: MatchCandidatePin[]; rejected: MatchCandidatePin[]; stage: MatchStageName
}) {
  const map = useMap()
  const items = useRef<{ el: HTMLElement | null; kind: 'win' | 'top' | 'other' | 'closed'; m: L.Marker }[]>([])

  useEffect(() => {
    const created = [
      ...candidates.map((c) => ({ c, kind: (c.selected ? 'top' : 'other') as 'top' | 'other' })),
      ...rejected.map((c) => ({ c, kind: 'closed' as const })),
    ].map(({ c, kind }, i) => {
      const m = L.marker([c.location.lat, c.location.lng], {
        interactive: false, keyboard: false,
        icon: L.divIcon({ className: '', html: '<div class="mc-dot"></div>', iconSize: [14, 14], iconAnchor: [7, 7] }),
      }).addTo(map)
      const el = m.getElement()?.firstElementChild as HTMLElement | null
      if (el) el.style.transitionDelay = `${Math.min(i, 20) * 25}ms`
      return { el, kind, m }
    })
    items.current = created
    return () => { created.forEach((x) => x.m.remove()); items.current = [] }
  }, [candidates, rejected])

  useEffect(() => {
    const s = stageIdx(stage)
    const frame = requestAnimationFrame(() => {
      items.current.forEach(({ el, kind }, i) => {
        if (!el) return
        el.classList.toggle('mc-in', s >= 1)
        el.classList.toggle('mc-closed', kind === 'closed')
        el.classList.toggle('mc-bad', kind === 'other' && s >= 2)
        el.classList.toggle('mc-out', (kind === 'other' || kind === 'closed') && s >= 2)
        // đổi delay sau khi hiện để việc mờ đi không bị trễ theo thứ tự
        if (s >= 2) el.style.transitionDelay = `${(i % 6) * 40}ms`
        el.classList.toggle('mc-win', kind === 'top' && s >= 5)
      })
    })
    return () => cancelAnimationFrame(frame)
  }, [stage, candidates, rejected])
  return null
}

/** Một tuyến vẽ dần bằng stroke-dashoffset. */
function AnimatedRoute({ path, show, tone }: {
  path: [number, number][]; show: boolean; tone: 'win' | 'other' | 'dim'
}) {
  const map = useMap()
  const poly = useRef<L.Polyline | null>(null)

  useEffect(() => {
    if (!show || poly.current) return
    const p = L.polyline(path, { className: 'mc-route', color: ROUTE_COLORS.other, weight: 5, opacity: 0.9, lineCap: 'round' }).addTo(map)
    poly.current = p
    const el = p.getElement() as SVGPathElement | null
    if (el && typeof el.getTotalLength === 'function') {
      const len = el.getTotalLength()
      el.style.strokeDasharray = `${len}`
      el.style.strokeDashoffset = `${len}`
      void el.getBoundingClientRect()
      el.style.transition = 'stroke-dashoffset 1s ease-out, stroke .4s ease, stroke-opacity .4s ease'
      el.style.strokeDashoffset = '0'
      window.setTimeout(() => { if (el) el.style.strokeDasharray = 'none' }, 1100)
    }
  }, [show])

  useEffect(() => {
    poly.current?.setStyle({
      color: ROUTE_COLORS[tone],
      weight: tone === 'win' ? 7 : 4,
      opacity: tone === 'dim' ? 0.45 : 0.95,
    })
  }, [tone, show])

  useEffect(() => () => { poly.current?.remove(); poly.current = null }, [])
  return null
}

interface MatchStageProps {
  origin: LatLng
  matches: MatchResult[]
  candidates: MatchCandidatePin[]
  rejected: MatchCandidatePin[]
  stage: MatchStageName
  onSkip: () => void
  onClose: () => void
  children?: ReactNode // bảng kết quả, hiện khi stage = result
}

export function MatchStage({ origin, matches, candidates, rejected, stage, onSkip, onClose, children }: MatchStageProps) {
  const s = stageIdx(stage)
  const routes = useMemo(
    () => matches.map((m) => (m.route && m.route.length >= 2 ? m.route : [[origin.lat, origin.lng], [m.location.lat, m.location.lng]]) as [number, number][]),
    [matches, origin.lat, origin.lng],
  )
  const spread = useMemo(() => [...candidates, ...rejected].map((c) => c.location), [candidates, rejected])
  return (
    <div className="fixed inset-0 z-[100] bg-surface">
      <MapContainer center={[origin.lat, origin.lng]} zoom={14} zoomControl={false} className="w-full h-full">
        <TileLayer url={CARTO_TILE_URL} attribution='&copy; OpenStreetMap &copy; CARTO' />
        <Marker position={[origin.lat, origin.lng]} icon={USER_ICON} interactive={false} />
        <CandidateDots candidates={candidates} rejected={rejected} stage={stage} />
        {routes.map((r, i) => (
          <AnimatedRoute
            key={matches[i].garage_id}
            path={r}
            show={s >= 3}
            tone={s >= 5 ? (i === 0 ? 'win' : 'dim') : 'other'}
          />
        ))}
        <StageCamera stage={stage} origin={origin} spread={spread} routes={routes} />
      </MapContainer>

      <button onClick={onClose} aria-label="Đóng"
        className="absolute top-4 right-4 z-[1000] p-2.5 rounded-full bg-surface shadow-lg text-on-surface-variant hover:bg-surface-container-low">
        <X className="w-5 h-5" />
      </button>

      {stage !== 'result' && (
        <>
          <div className="absolute top-4 left-4 z-[1000] max-w-[70%] bg-surface/95 backdrop-blur rounded-full shadow-lg px-4 py-2.5 text-xs font-bold text-on-surface" role="status">
            {STAGE_LABEL[stage]}
          </div>
          {s >= 1 && (
            <button onClick={onSkip}
              className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[1000] bg-surface shadow-lg rounded-full px-4 py-2 text-xs font-bold text-on-surface-variant flex items-center gap-1.5 hover:bg-surface-container-low">
              <FastForward className="w-3.5 h-3.5" /> Bỏ qua
            </button>
          )}
        </>
      )}

      {stage === 'result' && (
        <div className="absolute z-[1000] inset-x-0 bottom-0 sm:inset-x-auto sm:right-4 sm:top-16 sm:bottom-4 sm:w-[400px] max-h-[62vh] sm:max-h-none bg-surface rounded-t-3xl sm:rounded-3xl shadow-2xl border border-outline-variant overflow-y-auto p-4 animate-in slide-in-from-bottom-6 duration-300">
          {children}
          {matches[0] && <RouteCameraList match={matches[0]} />}
        </div>
      )}
    </div>
  )
}
