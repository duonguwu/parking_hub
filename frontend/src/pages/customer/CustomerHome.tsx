import { useState, useEffect } from 'react'
import { Search, ChevronRight, Zap, CheckCircle2, Navigation, Car, Sparkles } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type DashboardSummary, TIER_COLOR } from '@/services/api'
import { useAuth } from '@/services/auth-context'
import { Link, useNavigate } from 'react-router-dom'
import { SmartBookingModal } from '@/components/SmartBookingModal'

const DEFAULT_COORDS = { lat: 10.7761, lng: 106.7011 } // HCMC centre

export function CustomerHome() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [searchInput, setSearchInput] = useState('')

  useEffect(() => {
    const load = async (lat?: number, lng?: number) => {
      try {
        const res = await customerApi.dashboardSummary(lat, lng)
        setData(res)
      } catch (e) {
        setError('Không thể tải dữ liệu bãi đỗ xe')
        console.error(e)
      } finally {
        setLoading(false)
      }
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => load(pos.coords.latitude, pos.coords.longitude),
        () => load(DEFAULT_COORDS.lat, DEFAULT_COORDS.lng),
      )
    } else {
      load(DEFAULT_COORDS.lat, DEFAULT_COORDS.lng)
    }
  }, [])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    navigate('/app/map')
  }

  const diag = data?.vehicle_diagnostics
  const recs = data?.smart_recommendations ?? []

  return (
    <div className="max-w-5xl mx-auto space-y-8 md:space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-300">

      {/* ── Search Hero ── */}
      <section className="text-center space-y-4 md:space-y-6 pt-2 md:pt-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-primary-container/20 text-primary rounded-full text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Hệ thống điều phối bãi đỗ xe thông minh</span>
        </div>

        <h1 className="text-2xl sm:text-3xl md:text-5xl font-black text-on-surface tracking-tight">
          {user ? `Xin chào, ${user.name.split(' ').slice(-1)[0]}!` : 'Bạn muốn đỗ xe ở đâu?'}
        </h1>

        <form onSubmit={handleSearchSubmit} className="max-w-2xl mx-auto relative group">
          <div className="relative flex items-center bg-surface border border-outline-variant rounded-full p-1.5 sm:p-2 focus-within:border-primary transition-colors">
            <Search className="w-5 h-5 text-outline ml-3 shrink-0" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-transparent outline-none px-3 py-2 text-sm sm:text-base text-on-surface placeholder:text-outline"
              placeholder="Nhập địa điểm, tòa nhà, bệnh viện, nhà hàng..."
            />
            <button
              type="submit"
              className="bg-primary hover:opacity-90 text-white rounded-full px-5 py-2.5 text-xs sm:text-sm font-bold tracking-wide transition-all shrink-0 flex items-center gap-1.5"
            >
              <span>TÌM BÃI</span>
            </button>
          </div>
        </form>

        {/* Quick Location Chips */}
        <div className="flex flex-wrap justify-center gap-2 items-center text-xs">
          <span className="font-semibold text-outline uppercase tracking-wider text-[11px]">Khu vực phổ biến:</span>
          {['Quận 1', 'Quận 3', 'Quận 7', 'Thảo Điền'].map((loc) => (
            <button
              key={loc}
              onClick={() => navigate('/app/map')}
              className="font-medium text-primary hover:bg-surface-container-low transition-colors bg-surface border border-outline-variant px-3 py-1 rounded-full"
            >
              {loc}
            </button>
          ))}
        </div>

        {/* Smart Booking CTA */}
        <div className="pt-2 md:pt-4">
          <button 
            onClick={() => setModalOpen(true)}
            className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-3.5 sm:py-4 text-sm sm:text-base font-bold text-white transition-all bg-primary hover:opacity-90 rounded-full active:scale-98 border border-primary/30"
          >
            <Zap className="w-5 h-5 mr-2 text-white" />
            ĐẶT CHỖ THÔNG MINH (AI)
          </button>
          <p className="text-[11px] font-bold text-on-surface-variant mt-2 uppercase tracking-wider">
            Tự động tìm bãi đỗ tối ưu nhất theo điểm đến
          </p>
        </div>
      </section>

      {/* ── Smart Recommendations ── */}
      <section className="space-y-4 md:space-y-6">
        <div className="flex justify-between items-end border-b border-outline-variant pb-3">
          <div>
            <h2 className="text-lg md:text-2xl font-bold text-on-surface">Bãi đỗ gợi ý tối ưu</h2>
            <p className="text-xs md:text-sm text-on-surface-variant mt-0.5">Tối ưu theo khoảng cách và dự báo chỗ trống</p>
          </div>
          <Link to="/app/map" className="text-primary font-bold text-xs tracking-wider flex items-center hover:opacity-80 transition-opacity">
            <span>Xem bản đồ</span>
            <ChevronRight className="w-4 h-4 ml-0.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-44 rounded-3xl bg-surface-container-low border border-outline-variant animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8 text-on-surface-variant text-sm bg-surface rounded-3xl border border-outline-variant">{error}</div>
        ) : recs.length === 0 ? (
          <div className="text-center py-8 text-on-surface-variant text-sm bg-surface rounded-3xl border border-outline-variant">
            Không tìm thấy bãi đỗ gần đây. Vui lòng bật định vị hoặc tìm trên bản đồ.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
            {recs.map((rec, idx) => (
              <Link key={rec.id} to={`/app/garages/${rec.id}`} className="block group">
                <Card className={`flex flex-col bg-surface border rounded-3xl p-5 relative h-full transition-all hover:border-primary/50 ${idx === 0 ? 'border-primary/40 bg-surface-container-low/30' : 'border-outline-variant'}`}>
                  {idx === 0 && (
                    <div className="absolute top-4 right-4 text-primary" title="Đề xuất tốt nhất">
                      <CheckCircle2 className="w-5 h-5" />
                    </div>
                  )}

                  <div className="flex justify-between items-start mb-3 pr-6">
                    <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                      rec.status === 'AVAILABLE'
                        ? 'bg-success-soft text-success'
                        : 'bg-error-container text-error'
                    }`}>
                      {rec.status === 'AVAILABLE' ? (idx === 0 ? 'Gần nhất • Còn chỗ' : 'Còn chỗ') : 'Đầy chỗ'}
                    </span>
                    <span className="text-xs font-semibold text-on-surface-variant flex items-center gap-1">
                      <Navigation className="w-3 h-3 text-outline" />
                      {rec.distance}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-on-surface mb-1 group-hover:text-primary transition-colors line-clamp-1">{rec.name}</h3>
                  <p className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider mb-4">
                    <span className={`px-2 py-0.5 rounded ${TIER_COLOR[rec.tier] ?? 'bg-surface-container'}`}>{rec.tier}</span> • Điểm {rec.score.toFixed(0)}
                  </p>

                  <div className="mt-auto pt-3 border-t border-outline-variant flex items-center justify-between">
                    <div>
                      <p className="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider">Thời gian chờ</p>
                      <p className="text-base font-black text-on-surface">{rec.wait_time}</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-colors">
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* ── Connected Vehicle / Diagnostics ── */}
      <section>
        <Card className="flex flex-col md:flex-row gap-6 items-center bg-surface border border-outline-variant rounded-3xl p-6 md:p-8">
          <div className="flex-1 space-y-3 w-full">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 bg-primary-container text-on-primary-container text-[10px] font-bold uppercase tracking-wider rounded-full">
                Phương tiện kết nối
              </span>
            </div>

            <h3 className="text-xl md:text-2xl font-bold text-on-surface">Thông tin xe</h3>

            {loading ? (
              <div className="space-y-2">
                <div className="h-4 bg-surface-container rounded animate-pulse w-3/4" />
                <div className="h-4 bg-surface-container rounded animate-pulse w-1/2" />
              </div>
            ) : diag ? (
              <div className="space-y-2">
                <p className="text-on-surface text-sm font-semibold">
                  {diag.brand} {diag.model} — Biển số: <span className="font-bold text-primary">{diag.license_plate}</span>
                </p>
                <p className="text-xs text-on-surface-variant">
                  Phương tiện đã sẵn sàng cho hệ thống nhận diện biển số tự động (ANPR) tại các bãi đỗ đối tác.
                </p>
              </div>
            ) : (
              <p className="text-on-surface-variant text-sm">
                Bạn chưa thêm phương tiện nào. <Link to="/app/vehicles" className="text-primary font-bold hover:underline">Thêm xe ngay</Link>
              </p>
            )}
          </div>

          <div className="w-full md:w-56 h-28 rounded-2xl bg-surface-container-low border border-outline-variant relative flex items-center justify-center p-3 shrink-0">
            <Car className="w-16 h-16 text-outline/40" />
            <div className="absolute top-2 left-2 bg-surface px-2 py-0.5 rounded text-[10px] font-bold text-on-surface-variant border border-outline-variant">
              {diag ? `${diag.brand}` : 'Chưa có xe'}
            </div>
          </div>
        </Card>
      </section>

      <SmartBookingModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}

