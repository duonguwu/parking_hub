// Bản đồ bãi đỗ dùng chung cho tài xế, chủ bãi và admin.
// Marker tô màu theo tình trạng chỗ trống (xanh / vàng / đỏ / xám nếu chưa có dữ liệu).
import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents, CircleMarker } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import type { ReactNode } from 'react'
import { AVAILABILITY_META, type GarageCard, type LatLng } from '@/services/api'

export const HCM_CENTER: LatLng = { lat: 10.7769, lng: 106.7009 }

// Key CARTO lấy từ env (prod cần key, dev bỏ trống vẫn chạy)
const CARTO_BASEMAP_KEY = import.meta.env.VITE_CARTO_BASEMAP_KEY?.trim()
export const CARTO_TILE_URL = `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png${
  CARTO_BASEMAP_KEY ? `?key=${encodeURIComponent(CARTO_BASEMAP_KEY)}` : ''
}`

const iconCache = new Map<string, L.DivIcon>()

function markerIcon(g: GarageCard, selected: boolean): L.DivIcon {
  const meta = AVAILABILITY_META[g.availability?.status ?? 'unknown']
  const label = g.availability?.has_data ? String(g.availability.available ?? '') : 'P'
  const key = `${meta.hex}-${label}-${selected}`
  const cached = iconCache.get(key)
  if (cached) return cached
  const size = selected ? 40 : 32
  const icon = L.divIcon({
    className: 'parking-marker',
    html: `<div style="width:${size}px;height:${size}px;background:${meta.hex};border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center">
      <span style="transform:rotate(45deg);color:#fff;font:700 ${selected ? 13 : 11}px/1 system-ui,sans-serif">${label}</span>
    </div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  })
  iconCache.set(key, icon)
  return icon
}

function FlyTo({ target, zoom }: { target: LatLng | null; zoom?: number }) {
  const map = useMap()
  useEffect(() => {
    if (target) map.flyTo([target.lat, target.lng], zoom ?? Math.max(map.getZoom(), 15), { duration: 0.6 })
  }, [target?.lat, target?.lng])
  return null
}

function ClickHandler({ onClick }: { onClick: (p: LatLng) => void }) {
  useMapEvents({ click: (e) => onClick({ lat: e.latlng.lat, lng: e.latlng.lng }) })
  return null
}

/** Khi danh sách bãi đổi, tự fit khung nhìn (chỉ dùng cho admin / chủ bãi). */
function FitBounds({ points }: { points: LatLng[] }) {
  const map = useMap()
  useEffect(() => {
    if (points.length === 0) return
    if (points.length === 1) { map.setView([points[0].lat, points[0].lng], 16); return }
    map.fitBounds(L.latLngBounds(points.map((p) => [p.lat, p.lng] as [number, number])), { padding: [32, 32] })
  }, [points.length])
  return null
}

interface ParkingMapProps {
  garages: GarageCard[]
  selectedId?: string | null
  onSelect?: (g: GarageCard) => void
  /** Nội dung popup khi bấm marker. Bỏ trống thì không hiện popup. */
  renderPopup?: (g: GarageCard) => ReactNode
  center?: LatLng
  zoom?: number
  /** Điểm tìm kiếm (vị trí hiện tại hoặc điểm bấm trên bản đồ). */
  searchPoint?: LatLng | null
  onMapClick?: (p: LatLng) => void
  flyTo?: LatLng | null
  fitToGarages?: boolean
  className?: string
}

export function ParkingMap({
  garages, selectedId, onSelect, renderPopup, center = HCM_CENTER, zoom = 14,
  searchPoint, onMapClick, flyTo, fitToGarages, className,
}: ParkingMapProps) {
  const withPos = garages.filter((g) => g.position)
  return (
    <MapContainer center={[center.lat, center.lng]} zoom={zoom} className={className ?? 'w-full h-full'} zoomControl={false}>
      <TileLayer
        url={CARTO_TILE_URL}
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      {searchPoint && (
        <CircleMarker center={[searchPoint.lat, searchPoint.lng]} radius={8}
          pathOptions={{ color: '#fff', weight: 3, fillColor: '#3b82f6', fillOpacity: 1 }} />
      )}
      {withPos.map((g) => (
        <Marker
          key={g.id}
          position={[g.position!.lat, g.position!.lng]}
          icon={markerIcon(g, g.id === selectedId)}
          zIndexOffset={g.id === selectedId ? 1000 : 0}
          eventHandlers={{ click: () => onSelect?.(g) }}
        >
          {renderPopup && <Popup>{renderPopup(g)}</Popup>}
        </Marker>
      ))}
      {onMapClick && <ClickHandler onClick={onMapClick} />}
      <FlyTo target={flyTo ?? null} />
      {fitToGarages && <FitBounds points={withPos.map((g) => g.position!)} />}
    </MapContainer>
  )
}

/** Chú thích màu marker. */
export function MapLegend({ className }: { className?: string }) {
  return (
    <div className={className ?? 'flex flex-wrap gap-3 text-[11px] text-on-surface-variant'}>
      {(['available', 'limited', 'full', 'unknown'] as const).map((k) => (
        <span key={k} className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: AVAILABILITY_META[k].hex }} />
          {AVAILABILITY_META[k].label}
        </span>
      ))}
    </div>
  )
}
