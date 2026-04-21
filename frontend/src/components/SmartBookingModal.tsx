import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Search, Zap, Loader2, Navigation, Clock, CheckCircle2, Star, Target, Crosshair } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { matchingApi, customerApi, type Vehicle, type MatchResult, TIER_COLOR } from '@/services/api'

interface SmartBookingModalProps {
  isOpen: boolean
  onClose: () => void
  defaultService?: string
}

const DEFAULT_COORDS = { lat: 10.7761, lng: 106.7011 }

const TEST_LOCATIONS = [
  { id: 'current', name: '📍 Vị trí hiện tại' },
  { id: 'q1', name: 'Quận 1, TP.HCM', lat: 10.7761, lng: 106.7011 },
  { id: 'q7', name: 'Quận 7, TP.HCM', lat: 10.7325, lng: 106.7155 },
  { id: 'binh_thanh', name: 'Bình Thạnh, TP.HCM', lat: 10.8061, lng: 106.7130 },
  { id: 'thu_duc', name: 'TP. Thủ Đức', lat: 10.8037, lng: 106.7820 },
]

export function SmartBookingModal({ isOpen, onClose, defaultService = 'wash_premium' }: SmartBookingModalProps) {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<'input' | 'scanning' | 'results'>('input')

  // Inputs
  const [locationMode, setLocationMode] = useState('current')
  const [timeMode, setTimeMode] = useState<'now' | 'custom'>('now')
  const [customDate, setCustomDate] = useState(() => new Date().toISOString().split('T')[0])
  const [customTime, setCustomTime] = useState(() => {
    const d = new Date()
    let nextHour = d.getHours() + 2
    if (nextHour < 8) nextHour = 8
    if (nextHour > 20) nextHour = 20
    return `${nextHour.toString().padStart(2, '0')}:00`
  })
  const [service, setService] = useState(defaultService)
  const [vehicleId, setVehicleId] = useState('')
  const [userVehicles, setUserVehicles] = useState<Vehicle[]>([])

  // State
  const [matches, setMatches] = useState<MatchResult[]>([])
  const [searchId, setSearchId] = useState('')
  const [loadingMsg, setLoadingMsg] = useState('Đang tải dữ liệu...')
  const [bookingLoading, setBookingLoading] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      setPhase('input')
      setMatches([])
      setError('')
      
      const d = new Date()
      let nextHour = d.getHours() + 2
      if (nextHour < 8) nextHour = 8
      if (nextHour > 20) nextHour = 20
      setCustomTime(`${nextHour.toString().padStart(2, '0')}:00`)
      customerApi.vehicles().then(vs => {
        setUserVehicles(vs)
        setVehicleId(vs.find(v => v.is_default)?.id ?? vs[0]?.id ?? '')
      }).catch(e => setError('Failed to load vehicles'))
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSearch = async () => {
    setPhase('scanning')
    setLoadingMsg('Đang quét vệ tinh mạng lưới cửa hàng...')
    setError('')

    // Delay randomly for dramatic effect
    setTimeout(() => setLoadingMsg('Đang đo độ kẹt xe & kiểm tra slot trống...'), 1200)
    setTimeout(() => setLoadingMsg('Đang chấm điểm bằng WashMind Intelligence...'), 2400)

    try {
      let pos: [number, number]
      if (locationMode === 'current') {
        pos = await new Promise<[number, number]>((resolve) => {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              (p) => resolve([p.coords.latitude, p.coords.longitude]),
              () => resolve([DEFAULT_COORDS.lat, DEFAULT_COORDS.lng])
            )
          } else {
            resolve([DEFAULT_COORDS.lat, DEFAULT_COORDS.lng])
          }
        })
      } else {
        const loc = TEST_LOCATIONS.find(l => l.id === locationMode)
        pos = loc ? [loc.lat!, loc.lng!] : [DEFAULT_COORDS.lat, DEFAULT_COORDS.lng]
      }

      let reqTime: string | undefined = undefined
      if (timeMode === 'custom') {
        reqTime = new Date(`${customDate}T${customTime}`).toISOString()
      }

      const res = await matchingApi.search({
        current_location: { lat: pos[0], lng: pos[1] },
        service_type_code: service,
        vehicle_id: vehicleId,
        requested_time: reqTime,
        top_k: 3,
      })

      setTimeout(() => {
        setSearchId(res.search_id)
        setMatches(res.matches)
        setPhase('results')
      }, 3500) // minimum loading time for UX effect

    } catch (e: any) {
      setError(e.message || 'Lỗi kết nối Intelligence Engine')
      setPhase('input')
    }
  }

  const handleBook = async (match: MatchResult) => {
    setBookingLoading(match.garage_id)
    try {
      let reqTime: string
      if (timeMode === 'custom') {
        reqTime = new Date(`${customDate}T${customTime}`).toISOString()
      } else {
        const now = new Date()
        now.setMinutes(now.getMinutes() + match.travel_minutes + 5) // eta + 5 min prep
        reqTime = now.toISOString()
      }

      const res = await customerApi.createBooking({
        garage_id: match.garage_id,
        service_type_code: service,
        vehicle_id: vehicleId,
        requested_time: reqTime,
        matching_context: {
          search_id: searchId,
          match_score: match.total_score,
          rank: match.rank
        }
      })

      onClose()
      navigate(`/app/bookings/${res.id}`)
    } catch (e: any) {
      alert('Không thể đặt lịch: ' + e.message)
      setBookingLoading(null)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 fade-in">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="bg-slate-50 w-full max-w-2xl rounded-[2.5rem] shadow-2xl relative z-10 overflow-hidden border border-white flex flex-col max-h-[90vh]">
        <button className="absolute top-6 right-6 p-2 rounded-full hover:bg-slate-200 text-slate-500 transition-colors z-20" onClick={onClose}>
          <X className="w-6 h-6" />
        </button>

        {/* Header */}
        <div className="bg-white px-8 pt-8 pb-6 border-b border-slate-100 flex items-center gap-4 shrink-0">
          <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Crosshair className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">Smart Matching</h2>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Tìm Gara Tối Ưu Bằng AI</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto">
          {error && (
            <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm font-semibold border border-rose-100">
              {error}
            </div>
          )}

          {phase === 'input' && (
            <div className="space-y-8 slide-up">
              {/* Row 1: Location & Time */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3 flex flex-col">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Khu vực</label>
                  <select value={locationMode} onChange={e => setLocationMode(e.target.value)} className="w-full bg-white border-2 border-slate-200 text-slate-900 rounded-2xl p-4 outline-none focus:border-blue-500 font-bold appearance-none cursor-pointer">
                    {TEST_LOCATIONS.map(l => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Thời điểm rửa xe</label>
                  <div className="flex gap-4">
                    <button onClick={() => setTimeMode('now')} className={`flex-1 min-w-0 px-2 h-[56px] rounded-2xl border-2 flex items-center justify-center gap-2 transition-all font-bold ${timeMode === 'now' ? 'bg-blue-50 border-blue-600 text-blue-700 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:border-blue-200'}`}>
                      <Zap className={`w-4 h-4 shrink-0 px-[1px] ${timeMode === 'now' ? 'text-blue-600' : 'text-slate-400'}`} /> <span className="truncate">Hiện tại</span>
                    </button>
                    <button onClick={() => setTimeMode('custom')} className={`flex-1 min-w-0 px-2 h-[56px] rounded-2xl border-2 flex items-center justify-center gap-2 transition-all font-bold ${timeMode === 'custom' ? 'bg-blue-50 border-blue-600 text-blue-700 shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:border-blue-200'}`}>
                      <Clock className={`w-4 h-4 shrink-0 px-[1px] ${timeMode === 'custom' ? 'text-blue-600' : 'text-slate-400'}`} /> <span className="truncate">Lịch hẹn</span>
                    </button>
                  </div>
                </div>
              </div>

              {timeMode === 'custom' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-top-2 duration-300">
                  <div className="space-y-3 flex flex-col">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Chọn ngày</label>
                    <input 
                      type="date"
                      value={customDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={e => setCustomDate(e.target.value)}
                      className="w-full h-[56px] rounded-2xl border-2 border-slate-200 bg-white text-slate-900 px-4 outline-none font-bold shadow-sm cursor-pointer text-sm focus:border-blue-500 focus:bg-blue-50 transition-colors"
                    />
                  </div>
                  <div className="space-y-3 flex flex-col relative group">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Chọn giờ</label>
                    <input
                      type="time"
                      value={customTime}
                      onChange={e => setCustomTime(e.target.value)}
                      className="w-full h-[56px] rounded-2xl border-2 border-slate-200 bg-white text-slate-900 px-4 outline-none font-bold shadow-sm cursor-pointer text-sm focus:border-blue-500 focus:bg-blue-50 transition-colors custom-time-input"
                    />
                  </div>
                </div>
              )}

              {/* Row 2: Service & Vehicle */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3 flex flex-col">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Dịch vụ</label>
                  <select value={service} onChange={e => setService(e.target.value)} className="w-full bg-white border-2 border-slate-200 text-slate-900 rounded-2xl p-4 outline-none focus:border-blue-500 font-bold appearance-none cursor-pointer">
                    <option value="wash_standard">Rửa Tiêu Chuẩn</option>
                    <option value="wash_premium">Rửa Premium</option>
                    <option value="detailing">Detailing Chuyên Sâu</option>
                    <option value="interior">Vệ Sinh Nội Thất</option>
                  </select>
                </div>
                <div className="space-y-3 flex flex-col">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Xe của bạn</label>
                  <select value={vehicleId} onChange={e => setVehicleId(e.target.value)} className="w-full bg-white border-2 border-slate-200 text-slate-900 rounded-2xl p-4 outline-none focus:border-blue-500 font-bold appearance-none cursor-pointer relative">
                    {userVehicles.length === 0 ? <option value="">Chưa có xe nào</option> : null}
                    {userVehicles.map(v => (
                      <option key={v.id} value={v.id}>{v.license_plate} - {v.brand} {v.model}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={handleSearch}
                disabled={!vehicleId}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-black tracking-wide py-5 rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-blue-500/30 transition-transform active:scale-[0.98] disabled:opacity-50"
              >
                <Search className="w-5 h-5" /> TÌM GARA TỐI ƯU
              </button>
            </div>
          )}

          {phase === 'scanning' && (
            <div className="flex flex-col items-center justify-center py-20 animate-in fade-in zoom-in duration-500">
              <div className="relative w-24 h-24 mb-8">
                <div className="absolute inset-0 border-4 border-blue-100 rounded-full" />
                <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin" />
                <Target className="absolute inset-0 m-auto text-blue-500 w-8 h-8 animate-pulse" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight transition-all duration-300">
                {loadingMsg}
              </h3>
              <p className="text-slate-500 text-sm font-medium mt-2">Dựa trên toạ độ hiện tại của bạn</p>
            </div>
          )}

          {phase === 'results' && (
            <div className="space-y-6 slide-up">
              {matches.map((m, i) => (
                <Card key={m.garage_id} className={`p-6 rounded-3xl border-2 transition-all ${i === 0 ? 'bg-blue-50/30 border-blue-400 shadow-lg shadow-blue-500/10' : 'bg-white border-slate-200 hover:border-blue-200'}`}>
                  <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {i === 0 && <span className="bg-blue-600 text-white text-[10px] font-black tracking-widest uppercase px-2 py-0.5 rounded-md flex items-center gap-1 shadow-sm"><Star className="w-3 h-3 fill-white" /> Top 1</span>}
                        <h4 className="text-xl font-black text-slate-900 tracking-tight">{m.name}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-4">
                        <span className={`px-2 py-0.5 rounded-md uppercase ${TIER_COLOR[m.tier] ?? 'bg-slate-100 text-slate-600'}`}>{m.tier}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md"><Navigation className="w-3.5 h-3.5" /> {m.travel_distance_km.toFixed(1)} km ({m.travel_minutes}p)</span>
                      </div>
                      
                      <div className="space-y-1.5">
                        {m.reasons.map((r, ri) => (
                          <div key={ri} className="flex items-start gap-2 text-sm text-slate-600 font-medium">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                            <span>{r.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col items-end shrink-0 sm:border-l border-slate-200 sm:pl-6">
                      <p className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">Điểm phù hợp</p>
                      <p className={`text-4xl font-black tracking-tight mb-4 ${i === 0 ? 'bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600' : 'text-slate-900'}`}>
                        {Math.round(m.total_score)}
                      </p>
                      
                      <button 
                        onClick={() => handleBook(m)}
                        disabled={!!bookingLoading}
                        className={`w-full py-3 px-6 rounded-xl font-bold uppercase tracking-wider text-xs transition-colors flex items-center justify-center gap-2 ${i === 0 ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md' : 'bg-slate-900 hover:bg-slate-800 text-white'}`}
                      >
                        {bookingLoading === m.garage_id ? <Loader2 className="w-4 h-4 animate-spin" /> : 'ĐẶT LỊCH NGAY'}
                      </button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
