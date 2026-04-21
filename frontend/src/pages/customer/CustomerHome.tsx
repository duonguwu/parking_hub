import { useState, useEffect } from 'react'
import { Search, ChevronRight, Zap, CheckCircle2, AlertTriangle, Car } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type DashboardSummary } from '@/services/api'
import { useAuth } from '@/services/auth-context'
import { Link } from 'react-router-dom'
import { SmartBookingModal } from '@/components/SmartBookingModal'

const DEFAULT_COORDS = { lat: 10.7761, lng: 106.7011 } // HCMC centre

export function CustomerHome() {
  const { user } = useAuth()
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    const load = async (lat?: number, lng?: number) => {
      try {
        const res = await customerApi.dashboardSummary(lat, lng)
        setData(res)
      } catch (e) {
        setError('Could not load dashboard data')
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

  const diag = data?.vehicle_diagnostics
  const recs = data?.smart_recommendations ?? []

  return (
    <div className="max-w-5xl mx-auto space-y-16 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* ── Search Hero ── */}
      <section className="text-center space-y-8 pt-8">
        <h1 className="text-5xl font-extrabold text-slate-900 tracking-tight">
          {user ? `Xin chào, ${user.name.split(' ').slice(-1)[0]}!` : 'Where do you want to wash?'}
        </h1>
        <div className="max-w-3xl mx-auto relative group flex items-center shadow-lg shadow-blue-500/5 rounded-2xl overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <input
            type="text"
            className="w-full bg-white border border-slate-200 outline-none pl-8 pr-36 py-6 text-lg focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all placeholder:text-slate-400"
            placeholder="Nhập địa chỉ hoặc tên cửa hàng..."
          />
          <Link to="/app/map">
            <button className="absolute right-3 top-3 bottom-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-8 flex items-center justify-center font-semibold tracking-wide transition-colors">
              <Search className="w-[18px] h-[18px] mr-2" />
              TÌM
            </button>
          </Link>
        </div>
        <div className="flex justify-center gap-4 items-center">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Gần đây:</span>
          <button className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors bg-blue-50 px-3 py-1 rounded-full">Quận 7, TPHCM</button>
          <button className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors bg-blue-50 px-3 py-1 rounded-full">Thảo Điền</button>
        </div>
        <div className="pt-6">
          <button 
            onClick={() => setModalOpen(true)}
            className="group relative inline-flex items-center justify-center px-12 py-5 text-xl font-black text-white transition-all duration-300 ease-in-out bg-slate-900 border border-transparent rounded-[2rem] hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-blue-500/20 active:scale-95 shadow-xl shadow-slate-900/20"
          >
            <span className="absolute inset-0 w-full h-full -mt-1 rounded-[2rem] opacity-30 bg-gradient-to-b from-transparent via-transparent to-white" />
            <Zap className="w-6 h-6 mr-3 text-blue-400 group-hover:scale-110 group-hover:-rotate-6 transition-transform" />
            ĐẶT LỊCH THÔNG MINH
          </button>
          <p className="text-xs font-bold text-slate-400 mt-4 uppercase tracking-widest">A.I MATCHING ENGINE • RỬA NGAY HOẶC TỐI NAY</p>
        </div>
      </section>

      {/* ── Smart Recommendations ── */}
      <section className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-slate-200 pb-4">
          <div>
            <h4 className="text-2xl font-bold text-slate-900">Smart Recommendations</h4>
            <p className="text-sm text-slate-500 mt-1 font-medium">Tối ưu theo vị trí và loại xe của bạn</p>
          </div>
          <Link to="/app/map" className="text-blue-600 font-bold uppercase text-xs tracking-widest flex items-center group hover:text-blue-800 transition-colors">
            Xem tất cả
            <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 rounded-3xl bg-slate-100 animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12 text-slate-500">{error}</div>
        ) : recs.length === 0 ? (
          <div className="text-center py-12 text-slate-400 font-medium">
            Không tìm thấy cửa hàng gần đây. Hãy cấp quyền vị trí để xem gợi ý.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recs.map((rec, idx) => (
              <Link key={rec.id} to={`/app/garages/${rec.id}`}>
                <Card className={`flex flex-col border bg-white shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group rounded-3xl overflow-hidden p-6 relative h-full ${idx === 0 ? 'border-blue-200 bg-gradient-to-b from-blue-50/50 to-transparent' : 'border-slate-200'}`}>
                  {idx === 0 && (
                    <div className="absolute top-0 right-0 p-5">
                      <CheckCircle2 className="text-blue-600 w-6 h-6" />
                    </div>
                  )}
                  <div className="flex justify-between items-start mb-6">
                    <span className={`text-[10px] font-bold uppercase px-3 py-1 rounded-full tracking-widest ${rec.status === 'AVAILABLE' ? (idx === 0 ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20' : 'bg-emerald-100 text-emerald-700') : 'bg-slate-100 text-slate-600'}`}>
                      {rec.status === 'AVAILABLE' && idx === 0 ? 'Gần nhất' : rec.status === 'AVAILABLE' ? 'Có sẵn' : 'Bận'}
                    </span>
                    <span className="text-sm font-semibold text-slate-400">{rec.distance}</span>
                  </div>
                  <h5 className="text-xl font-bold text-slate-900 mb-1">{rec.name}</h5>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-8">{rec.tier} · Score {rec.score.toFixed(0)}</p>

                  <div className="mt-auto pt-6 border-t border-slate-100 flex items-center justify-between">
                    <div>
                      <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mb-1.5">Thời gian chờ</p>
                      <p className={`text-lg font-black ${idx === 0 ? 'text-blue-600' : 'text-slate-900'}`}>{rec.wait_time}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-md transition-all duration-300 ${idx === 0 ? 'bg-blue-600 text-white shadow-blue-600/30 group-hover:scale-110' : 'bg-slate-50 text-slate-400 group-hover:bg-blue-600 group-hover:text-white'}`}>
                      {idx === 0 ? <Zap className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* ── Vehicle Health ── */}
      <section>
        <Card className="flex flex-col md:flex-row gap-8 items-center bg-slate-900 text-white rounded-3xl overflow-hidden relative border-none p-8 lg:p-12 shadow-2xl">
          <div className="absolute top-0 right-0 w-1/2 h-full opacity-5 pointer-events-none stroke-white">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
              <path d="M0,0 L100,100 M100,0 L0,100" strokeWidth="0.5" fill="none" />
            </svg>
          </div>

          <div className="flex-1 z-10 space-y-6">
            <div>
              <span className="inline-block px-3 py-1 bg-white/10 text-white/90 text-[10px] font-bold uppercase tracking-widest rounded-full mb-4">
                Chẩn đoán phương tiện
              </span>
              <h4 className="text-3xl font-bold mb-3">Trạng thái xe</h4>
            </div>

            {loading ? (
              <div className="space-y-3">
                <div className="h-4 bg-white/10 rounded animate-pulse w-3/4" />
                <div className="h-4 bg-white/10 rounded animate-pulse w-1/2" />
              </div>
            ) : diag ? (
              <>
                <p className="text-white/70 max-w-md leading-relaxed text-sm font-medium">
                  {diag.brand} {diag.model} ({diag.license_plate}) — lần rửa cuối {diag.days_since_last_service} ngày trước. Bề mặt sơn có dấu hiệu hao mòn nhẹ.
                </p>
                <div className="space-y-4 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full border-[3px] ${diag.finish_degradation < -10 ? 'border-amber-400' : 'border-emerald-400'}`} />
                    <span className="text-sm font-semibold tracking-wide text-white/90 uppercase text-[11px] flex items-center gap-2">
                      {diag.finish_degradation < -10 && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                      Hao mòn bề mặt: {diag.finish_degradation}%
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 rounded-full bg-blue-500" />
                    <span className="text-sm font-semibold tracking-wide text-white/90 uppercase text-[11px]">
                      Lần rửa cuối: {diag.days_since_last_service} ngày trước
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-white/50 text-sm">Chưa có xe nào. <Link to="/app/vehicles" className="text-blue-400 hover:underline">Thêm xe ngay</Link></p>
            )}
          </div>

          <div className="w-full md:w-[320px] aspect-video rounded-2xl bg-white/5 border border-white/10 relative flex items-center justify-center p-2 z-10 overflow-hidden shadow-inner">
            <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '16px 16px' }} />
            <Car className="w-28 h-28 text-white/20 stroke-[1px]" />
            <div className="absolute top-4 left-4 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10">
              <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-400">
                {diag ? `${diag.brand} ${diag.model}` : 'No Vehicle'}
              </span>
            </div>
          </div>
        </Card>
      </section>

      <SmartBookingModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}
