import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Search, Zap, Loader2, Navigation, Clock, CheckCircle2, Star, Crosshair } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, matchingApi, type Vehicle, type MatchResult, TIER_COLOR } from '@/services/api'

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

export function SmartBookingModal({ isOpen, onClose, defaultService = 'park_hourly' }: SmartBookingModalProps) {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<'input' | 'scanning' | 'results'>('input')

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
      }).catch(() => setError('Không tải được danh sách xe'))
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSearch = async () => {
    setPhase('scanning')
    setLoadingMsg('Đang phân tích mạng lưới bãi đỗ xe...')
    setError('')

    setTimeout(() => setLoadingMsg('Đang kiểm tra chỗ trống & thời gian di chuyển...'), 1000)
    setTimeout(() => setLoadingMsg('Đang chấm điểm và xếp hạng đề xuất tối ưu...'), 2000)

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

      setMatches(res.matches)
      setSearchId(res.search_id)
      setPhase('results')
    } catch (e: any) {
      setError('Lỗi tìm kiếm: ' + (e.message || 'Vui lòng thử lại'))
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
        now.setMinutes(now.getMinutes() + match.travel_minutes + 5)
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
      alert('Không thể đặt chỗ: ' + e.message)
      setBookingLoading(null)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal / Drawer */}
      <div className="bg-surface w-full max-w-xl rounded-t-3xl sm:rounded-3xl border border-outline-variant relative z-10 overflow-hidden flex flex-col max-h-[92vh] sm:max-h-[85vh] animate-in slide-in-from-bottom-6 sm:zoom-in-95 duration-200">
        {/* Mobile Pull Bar */}
        <div className="w-10 h-1 bg-outline-variant rounded-full mx-auto mt-2 sm:hidden" />

        {/* Header */}
        <div className="px-5 sm:px-6 pt-3 sm:pt-5 pb-3 border-b border-outline-variant flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center">
              <Crosshair className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-on-surface">Đặt chỗ thông minh (AI)</h2>
              <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider">Tối ưu chỗ trống & khoảng cách</p>
            </div>
          </div>
          <button className="p-2 rounded-full hover:bg-surface-container-low text-on-surface-variant transition-colors" onClick={onClose}>
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 sm:p-6 overflow-y-auto flex-1">
          {error && (
            <div className="mb-4 p-3 bg-error-container text-error rounded-2xl text-xs font-semibold">
              {error}
            </div>
          )}

          {phase === 'input' && (
            <div className="space-y-4 sm:space-y-6">
              {/* Row 1: Location & Time */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Khu vực tìm kiếm</label>
                  <select
                    value={locationMode}
                    onChange={e => setLocationMode(e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant text-on-surface rounded-2xl p-3 text-xs sm:text-sm outline-none focus:border-primary font-bold cursor-pointer"
                  >
                    {TEST_LOCATIONS.map(l => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Thời điểm sử dụng</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setTimeMode('now')}
                      className={`h-11 rounded-2xl border text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                        timeMode === 'now'
                          ? 'bg-primary text-white border-primary'
                          : 'bg-surface border-outline-variant text-on-surface-variant hover:border-primary'
                      }`}
                    >
                      <Zap className="w-3.5 h-3.5" /> <span>Đến ngay</span>
                    </button>
                    <button
                      onClick={() => setTimeMode('custom')}
                      className={`h-11 rounded-2xl border text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                        timeMode === 'custom'
                          ? 'bg-primary text-white border-primary'
                          : 'bg-surface border-outline-variant text-on-surface-variant hover:border-primary'
                      }`}
                    >
                      <Clock className="w-3.5 h-3.5" /> <span>Đặt trước</span>
                    </button>
                  </div>
                </div>
              </div>

              {timeMode === 'custom' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 animate-in fade-in duration-200">
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Chọn ngày</label>
                    <input 
                      type="date"
                      value={customDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={e => setCustomDate(e.target.value)}
                      className="w-full h-11 rounded-2xl border border-outline-variant bg-surface text-on-surface px-3 text-xs outline-none font-bold"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Chọn giờ</label>
                    <input
                      type="time"
                      value={customTime}
                      onChange={e => setCustomTime(e.target.value)}
                      className="w-full h-11 rounded-2xl border border-outline-variant bg-surface text-on-surface px-3 text-xs outline-none font-bold"
                    />
                  </div>
                </div>
              )}

              {/* Row 2: Service & Vehicle */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Loại dịch vụ</label>
                  <select
                    value={service}
                    onChange={e => setService(e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant text-on-surface rounded-2xl p-3 text-xs sm:text-sm outline-none focus:border-primary font-bold cursor-pointer"
                  >
                    <option value="park_hourly">Gửi theo giờ</option>
                    <option value="park_overnight">Gửi qua đêm</option>
                    <option value="park_daily">Gửi theo ngày</option>
                    <option value="park_monthly">Gói tháng</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Xe của bạn</label>
                  <select
                    value={vehicleId}
                    onChange={e => setVehicleId(e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant text-on-surface rounded-2xl p-3 text-xs sm:text-sm outline-none focus:border-primary font-bold cursor-pointer"
                  >
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
                className="w-full mt-2 bg-primary hover:opacity-90 text-white font-bold py-3.5 rounded-full flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-50 text-sm"
              >
                <Search className="w-4 h-4" /> TÌM BÃI ĐỖ TỐI ƯU
              </button>
            </div>
          )}

          {phase === 'scanning' && (
            <div className="flex flex-col items-center justify-center py-12 animate-in fade-in duration-300 text-center">
              <div className="relative w-16 h-16 mb-4">
                <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
                <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin" />
              </div>
              <h3 className="text-base font-bold text-on-surface">
                {loadingMsg}
              </h3>
              <p className="text-on-surface-variant text-xs mt-1">Hệ thống đang đối chiếu thuật toán Matching Engine...</p>
            </div>
          )}

          {phase === 'results' && (
            <div className="space-y-3">
              {matches.map((m, i) => (
                <Card key={m.garage_id} className={`p-4 rounded-2xl border transition-all ${i === 0 ? 'bg-primary-container/10 border-primary' : 'bg-surface border-outline-variant'}`}>
                  <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {i === 0 && (
                          <span className="bg-primary text-white text-[9px] font-bold uppercase px-2 py-0.5 rounded flex items-center gap-1">
                            <Star className="w-3 h-3 fill-white" /> Top 1
                          </span>
                        )}
                        <h4 className="text-sm font-bold text-on-surface">{m.name}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] font-semibold text-on-surface-variant mb-2">
                        <span className={`px-1.5 py-0.5 rounded uppercase ${TIER_COLOR[m.tier] ?? 'bg-surface-container'}`}>{m.tier}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1"><Navigation className="w-3 h-3 text-outline" /> {m.travel_distance_km.toFixed(1)} km ({m.travel_minutes} phút)</span>
                      </div>
                      
                      <div className="space-y-1">
                        {m.reasons.map((r, ri) => (
                          <div key={ri} className="flex items-start gap-1.5 text-xs text-on-surface-variant">
                            <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                            <span>{r.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex sm:flex-col items-center sm:items-end justify-between pt-2 sm:pt-0 border-t sm:border-t-0 border-outline-variant/50">
                      <div className="sm:text-right mb-0 sm:mb-2">
                        <span className="text-[10px] font-bold text-on-surface-variant uppercase">Điểm phù hợp</span>
                        <p className="text-xl font-black text-primary leading-tight">
                          {Math.round(m.total_score)}
                        </p>
                      </div>
                      
                      <button 
                        onClick={() => handleBook(m)}
                        disabled={!!bookingLoading}
                        className="py-2.5 px-5 rounded-full font-bold text-xs bg-primary hover:opacity-90 text-white transition-opacity flex items-center justify-center gap-1.5 shrink-0"
                      >
                        {bookingLoading === m.garage_id ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Giữ chỗ ngay'}
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
