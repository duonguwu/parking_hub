import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { Search, Star, Navigation, Filter, ShieldCheck, Activity, RadioTower, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type NearbyGarage, TIER_COLOR } from '@/services/api'
import { Link } from 'react-router-dom'

const DEFAULT_CENTER: [number, number] = [10.7761, 106.7011]

const makeIcon = (active: boolean, selected: boolean) => L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="width:${selected ? 52 : 44}px;height:${selected ? 52 : 44}px;background:${selected ? '#2563eb' : active ? '#3b82f6' : '#94a3b8'};border-radius:50%;box-shadow:${selected ? '0 0 0 6px rgba(59,130,246,0.25),0 4px 16px rgba(0,0,0,0.2)' : '0 4px 12px rgba(0,0,0,0.15)'};display:flex;align-items:center;justify-content:center;border:3px solid white;transition:all .3s;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
  </div>`,
  iconSize: [selected ? 52 : 44, selected ? 52 : 44],
  iconAnchor: [selected ? 26 : 22, selected ? 52 : 44],
  popupAnchor: [0, selected ? -52 : -44],
})

function MapFly({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => { map.flyTo(center, 14, { duration: 1.2 }) }, [center])
  return null
}

export function CustomerMap() {
  const [garages, setGarages] = useState<NearbyGarage[]>([])
  const [selected, setSelected] = useState<NearbyGarage | null>(null)
  const [userPos, setUserPos] = useState<[number, number]>(DEFAULT_CENTER)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    const load = (lat: number, lng: number) => {
      setUserPos([lat, lng])
      customerApi.nearbyGarages(lat, lng, 20)
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
    <div className="relative w-full h-[calc(100vh-88px)] flex bg-slate-50 overflow-hidden">

      {/* ── Sidebar ── */}
      <div className="w-[400px] bg-white z-[1000] shadow-[12px_0_24px_rgba(0,0,0,0.03)] flex flex-col h-full">
        <div className="p-8 pb-6 border-b border-slate-100">
          <h2 className="text-3xl font-black text-slate-900 tracking-tight mb-8">Intelligence Hub</h2>
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-slate-50 border-2 border-slate-100/80 text-slate-900 text-sm rounded-2xl block pl-12 p-3.5 outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all font-semibold placeholder:font-medium placeholder:text-slate-400"
              placeholder="Tìm cửa hàng..."
            />
            <button className="absolute inset-y-2 right-2 p-2 bg-white rounded-xl shadow-sm border border-slate-200 hover:text-blue-600 transition-colors">
              <Filter className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-1">
              {loading ? 'Đang tải...' : `${filtered.length} cửa hàng gần đây`}
            </span>
            {!loading && <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>}
          </div>

          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-blue-500" /></div>
          ) : filtered.map(g => (
            <Card
              key={g.id}
              className={`p-5 rounded-2xl cursor-pointer transition-all border-2 shadow-sm ${selected?.id === g.id ? 'border-blue-500 bg-blue-50/20 translate-x-2' : 'border-slate-100 bg-white hover:border-blue-200 hover:shadow-md'}`}
              onClick={() => setSelected(g)}
            >
              <div className="flex justify-between items-start mb-2">
                <span className={`text-[9px] uppercase tracking-widest font-black px-2.5 py-1 rounded-md ${TIER_COLOR[g.tier] ?? 'bg-slate-100 text-slate-600'}`}>{g.tier}</span>
                <div className="flex items-center gap-1 font-bold text-slate-900">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  <span className="text-sm">{g.score.toFixed(0)}</span>
                </div>
              </div>
              <h3 className="font-bold text-slate-900 text-base mb-1">{g.name}</h3>
              <div className="flex items-center gap-3 text-slate-500 text-xs font-bold">
                <span className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded-md"><Navigation className="w-3 h-3" /> {g.distance}</span>
                <span className={`flex items-center gap-1 ${g.active ? 'text-emerald-600' : 'text-slate-400'}`}>
                  <span className={`w-2 h-2 rounded-full ${g.active ? 'bg-emerald-500' : 'bg-slate-300'}`} />
                  {g.active ? 'Có sẵn' : 'Bận'}
                </span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* ── Map ── */}
      <div className="flex-1 relative z-0">
        <MapContainer
          center={userPos}
          zoom={13}
          className="w-full h-full"
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
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
                <div className="p-1 min-w-[180px]">
                  <h4 className="font-bold text-slate-900 mb-1">{g.name}</h4>
                  <p className="text-xs font-semibold text-slate-500 mb-3">{g.distance} • {g.tier}</p>
                  <Link to={`/app/garages/${g.id}`}>
                    <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2.5 rounded-xl shadow-sm transition-colors uppercase tracking-widest">
                      Xem chi tiết
                    </button>
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}

          {selected && <MapFly center={[selected.lat, selected.lng]} />}
        </MapContainer>

        {/* Top badges */}
        <div className="absolute top-6 left-6 right-6 z-[400] flex justify-between pointer-events-none">
          <div className="bg-white/90 backdrop-blur-md px-5 py-3.5 rounded-2xl shadow-lg border border-slate-200/60 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center relative">
              <div className="absolute inset-0 bg-blue-400 rounded-xl animate-ping opacity-20" />
              <ShieldCheck className="w-5 h-5 text-blue-600 relative z-10" />
            </div>
            <div>
              <span className="block text-[10px] font-bold text-blue-600 uppercase tracking-widest">Network Brain</span>
              <span className="block text-[15px] font-black text-slate-900 tracking-tight">Active Optimization</span>
            </div>
          </div>
          <div className="flex gap-4 pointer-events-auto">
            <div className="bg-white/90 backdrop-blur-md px-5 py-3.5 rounded-2xl shadow-lg border border-slate-200/60 flex items-center gap-4 hover:-translate-y-1 transition-transform">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                <RadioTower className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Nodes</span>
                <span className="block text-[15px] font-black text-slate-900">{garages.filter(g => g.active).length} Online</span>
              </div>
            </div>
            <div className="bg-white/90 backdrop-blur-md px-5 py-3.5 rounded-2xl shadow-lg border border-slate-200/60 flex items-center gap-4 hover:-translate-y-1 transition-transform">
              <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center">
                <Activity className="w-5 h-5 text-rose-500" />
              </div>
              <div>
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest">Total Nodes</span>
                <span className="block text-[15px] font-black text-slate-900">{garages.length} Found</span>
              </div>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-[400] pointer-events-none">
          <div className="bg-black/80 backdrop-blur-md text-white px-6 py-3 rounded-full flex items-center gap-6 shadow-2xl border border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.6)]" />
              <span className="text-[11px] font-bold uppercase tracking-widest text-white/80">Đã chọn</span>
            </div>
            <div className="w-px h-3 bg-white/20" />
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-slate-400" />
              <span className="text-[11px] font-bold uppercase tracking-widest text-white/80">Có sẵn</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
