import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { Search, Star, Navigation, List, Map as MapIcon, Loader2, ChevronRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type NearbyGarage, TIER_COLOR } from '@/services/api'
import { Link } from 'react-router-dom'
import { cn } from '@/services/utils'

const DEFAULT_CENTER: [number, number] = [10.7761, 106.7011]
const CARTO_BASEMAP_KEY = import.meta.env.VITE_CARTO_BASEMAP_KEY?.trim()
const CARTO_TILE_URL = `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png${
  CARTO_BASEMAP_KEY ? `?key=${encodeURIComponent(CARTO_BASEMAP_KEY)}` : ''
}`

const makeIcon = (active: boolean, selected: boolean) => L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="width:${selected ? 44 : 36}px;height:${selected ? 44 : 36}px;background:${selected ? '#3b82f6' : active ? '#059669' : '#94a3b8'};border-radius:50%;display:flex;align-items:center;justify-content:center;border:2.5px solid white;transition:all .2s;">
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
  </div>`,
  iconSize: [selected ? 44 : 36, selected ? 44 : 36],
  iconAnchor: [selected ? 22 : 18, selected ? 44 : 36],
  popupAnchor: [0, selected ? -44 : -36],
})

function MapFly({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => { map.flyTo(center, 14, { duration: 1.0 }) }, [center])
  return null
}

export function CustomerMap() {
  const [garages, setGarages] = useState<NearbyGarage[]>([])
  const [selected, setSelected] = useState<NearbyGarage | null>(null)
  const [userPos, setUserPos] = useState<[number, number]>(DEFAULT_CENTER)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showMobileList, setShowMobileList] = useState(false)

  useEffect(() => {
    const load = (lat: number, lng: number) => {
      setUserPos([lat, lng])
      customerApi.nearbyGarages(lat, lng, 30)
        .then(gs => { setGarages(gs); if (gs.length) setSelected(gs[0]) })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        p => load(p.coords.latitude, p.coords.longitude),
        () => load(...DEFAULT_CENTER),
      )
    } else {
      load(...DEFAULT_CENTER)
    }
  }, [])

  const filtered = garages.filter(g => g.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="relative w-full h-[calc(100vh-64px-60px)] md:h-[calc(100vh-76px)] flex bg-background overflow-hidden">

      {/* ── Left Sidebar (Desktop: md và lớn hơn) hoặc List View trên Mobile ── */}
      <div className={cn(
        "w-full md:w-[380px] bg-surface z-20 flex flex-col h-full border-r border-outline-variant transition-all",
        showMobileList ? "fixed inset-x-0 top-16 bottom-16 z-30 flex" : "hidden md:flex"
      )}>
        {/* Search header */}
        <div className="p-4 sm:p-5 border-b border-outline-variant space-y-3">
          <div className="flex justify-between items-center">
            <h2 className="text-lg md:text-xl font-bold text-on-surface">Mạng lưới bãi đỗ</h2>
            <span className="text-xs font-semibold text-primary bg-primary-container/30 px-2.5 py-0.5 rounded-full">
              {filtered.length} bãi
            </span>
          </div>

          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-outline" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-surface-container-low border border-outline-variant text-on-surface text-xs rounded-full pl-9 pr-4 py-2.5 outline-none focus:border-primary transition-colors placeholder:text-outline"
              placeholder="Tìm bãi đỗ theo tên..."
            />
          </div>
        </div>

        {/* List items */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-2.5">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12 text-on-surface-variant text-xs font-medium">
              Không tìm thấy bãi đỗ nào phù hợp.
            </div>
          ) : filtered.map(g => {
            const isSel = selected?.id === g.id
            return (
              <Card
                key={g.id}
                className={cn(
                  "p-3.5 rounded-2xl cursor-pointer transition-all border",
                  isSel
                    ? "border-primary bg-primary-container/10"
                    : "border-outline-variant bg-surface hover:border-primary/40"
                )}
                onClick={() => {
                  setSelected(g)
                  setShowMobileList(false)
                }}
              >
                <div className="flex justify-between items-start mb-1.5">
                  <span className={`text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded ${TIER_COLOR[g.tier] ?? 'bg-surface-container'}`}>
                    {g.tier}
                  </span>
                  <div className="flex items-center gap-1 font-bold text-on-surface text-xs">
                    <Star className="w-3 h-3 fill-warning text-warning" />
                    <span>{g.score.toFixed(0)}</span>
                  </div>
                </div>

                <h3 className="font-bold text-on-surface text-sm mb-1 line-clamp-1">{g.name}</h3>

                <div className="flex items-center justify-between text-xs font-medium text-on-surface-variant pt-1 border-t border-outline-variant/60">
                  <span className="flex items-center gap-1">
                    <Navigation className="w-3 h-3 text-outline" /> {g.distance}
                  </span>
                  <span className={cn(
                    "font-semibold text-[11px]",
                    g.active ? "text-success" : "text-on-surface-variant"
                  )}>
                    {g.active ? '● Còn chỗ' : '○ Tạm đóng'}
                  </span>
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      {/* ── Map Canvas ── */}
      <div className="flex-1 relative z-0 h-full w-full">
        <MapContainer
          center={userPos}
          zoom={13}
          className="w-full h-full"
          zoomControl={false}
        >
          <TileLayer
            url={CARTO_TILE_URL}
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {filtered.map(g => (
            <Marker
              key={g.id}
              position={[g.lat, g.lng]}
              icon={makeIcon(g.active, selected?.id === g.id)}
              eventHandlers={{ click: () => setSelected(g) }}
            >
              <Popup>
                <div className="p-1 min-w-[160px]">
                  <h4 className="font-bold text-on-surface text-sm mb-0.5">{g.name}</h4>
                  <p className="text-[11px] text-on-surface-variant mb-2">{g.distance} • {g.tier}</p>
                  <Link to={`/app/garages/${g.id}`}>
                    <button className="w-full bg-primary hover:opacity-90 text-white font-bold text-xs py-2 rounded-full transition-colors uppercase tracking-wider">
                      Chi tiết
                    </button>
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}

          {selected && <MapFly center={[selected.lat, selected.lng]} />}
        </MapContainer>

        {/* Mobile View Switcher (Danh sách / Bản đồ) */}
        <div className="md:hidden absolute top-3 left-3 right-3 z-[400] flex justify-between items-center gap-2">
          <div className="flex-1 bg-surface/95 backdrop-blur-md px-3.5 py-2 rounded-full border border-outline-variant flex items-center gap-2 text-xs font-semibold text-on-surface">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span>{garages.filter(g => g.active).length} bãi đang hoạt động</span>
          </div>

          <button
            onClick={() => setShowMobileList(!showMobileList)}
            className="bg-surface text-on-surface border border-outline-variant p-2.5 rounded-full font-bold text-xs flex items-center gap-1.5 active:scale-95 transition-all shrink-0"
          >
            {showMobileList ? <MapIcon className="w-4 h-4 text-primary" /> : <List className="w-4 h-4 text-primary" />}
            <span>{showMobileList ? 'Bản đồ' : 'Danh sách'}</span>
          </button>
        </div>

        {/* Selected Garage Mobile Preview Card (Floating at bottom on mobile) */}
        {selected && !showMobileList && (
          <div className="md:hidden absolute bottom-3 left-3 right-3 z-[400] animate-in slide-in-from-bottom-4 duration-200">
            <Card className="p-4 bg-surface/95 backdrop-blur-md border border-outline-variant rounded-3xl">
              <div className="flex justify-between items-start mb-1.5">
                <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${TIER_COLOR[selected.tier] ?? 'bg-surface-container'}`}>
                  {selected.tier}
                </span>
                <span className={cn(
                  "text-xs font-bold",
                  selected.active ? "text-success" : "text-on-surface-variant"
                )}>
                  {selected.active ? '● Còn chỗ' : '○ Tạm đóng'}
                </span>
              </div>

              <h3 className="font-bold text-on-surface text-sm mb-1">{selected.name}</h3>
              <p className="text-xs text-on-surface-variant mb-3 flex items-center gap-1">
                <Navigation className="w-3 h-3 text-outline" /> {selected.distance} • Đánh giá: {selected.score.toFixed(0)} điểm
              </p>

              <div className="flex gap-2">
                <Link to={`/app/garages/${selected.id}`} className="flex-1">
                  <button className="w-full bg-primary text-white text-xs font-bold py-2.5 rounded-full hover:opacity-90 transition-opacity flex items-center justify-center gap-1">
                    <span>Xem bãi & Đặt chỗ</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </Link>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

