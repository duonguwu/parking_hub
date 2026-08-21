import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Calendar, Wifi, Coffee, BatteryCharging, Snowflake, ChevronLeft, Zap, Droplets, Loader2, Star, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type GaragePortal, TIER_COLOR } from '@/services/api'

const AMENITY_MAP: Record<string, { icon: React.ElementType; label: string; color: string; bg: string }> = {
  wifi:         { icon: Wifi,           label: 'WiFi',            color: 'text-blue-500',   bg: 'bg-blue-50' },
  coffee:       { icon: Coffee,         label: 'Cà phê',          color: 'text-amber-600',  bg: 'bg-amber-50' },
  ev_charging:  { icon: BatteryCharging,label: 'Sạc EV',          color: 'text-emerald-500',bg: 'bg-emerald-50' },
  climate:      { icon: Snowflake,      label: 'Điều hòa',        color: 'text-cyan-500',   bg: 'bg-cyan-50' },
  waiting_area: { icon: Coffee,         label: 'Khu vực chờ',     color: 'text-amber-600',  bg: 'bg-amber-50' },
}

const HERO_IMAGES = [
  'https://images.unsplash.com/photo-1601362840469-51e4d8d58785?auto=format&fit=crop&q=80&w=1200',
  'https://images.unsplash.com/photo-1552930294-6b595f4c2974?auto=format&fit=crop&q=80&w=800',
  'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&q=80&w=800',
]

export function CustomerGarageDetail() {
  const { id } = useParams<{ id: string }>()
  const [portal, setPortal] = useState<GaragePortal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    customerApi.garagePortal(id)
      .then(setPortal)
      .catch(() => setError('Không thể tải thông tin cửa hàng'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
    </div>
  )

  if (error || !portal) return (
    <div className="text-center py-16 text-slate-500">{error || 'Không tìm thấy cửa hàng'}</div>
  )

  const { info, amenities, services, capacity_load } = portal
  const maxLoad = Math.max(...capacity_load.map(c => c.load_percent), 1)

  return (
    <div className="flex-1 pb-24 max-w-7xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500 pt-2 text-slate-800 px-6">

      {/* Nav */}
      <div className="flex justify-between items-center w-full">
        <div className="flex items-center gap-6">
          <Link to="/app/map" className="p-3 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors shadow-sm">
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </Link>
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">{info.name}</h2>
            {info.is_verified && (
              <span className="bg-emerald-100 text-emerald-700 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full border border-emerald-200">Verified</span>
            )}
          </div>
        </div>
      </div>

      {/* Hero Photos */}
      <section className="flex flex-col md:flex-row gap-6 h-auto md:h-[520px]">
        <div className="w-full md:w-2/3 relative overflow-hidden rounded-[2rem] border border-slate-200 shadow-sm h-[320px] md:h-full group flex-shrink-0">
          <img className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" src={info.photos[0] ?? HERO_IMAGES[0]} alt={info.name} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
          <div className="absolute bottom-8 left-8 md:bottom-12 md:left-12">
            <span className="text-[10px] font-bold text-blue-300 uppercase tracking-widest mb-2 block">{info.address.district}</span>
            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight drop-shadow-md">{info.name}</h1>
            <p className="text-white/70 text-sm font-medium mt-2">{info.address.street}, {info.address.ward}</p>
          </div>
        </div>
        <div className="w-full md:w-1/3 flex flex-row md:flex-col gap-6 h-[160px] md:h-full">
          {[1, 2].map(i => (
            <div key={i} className="flex-1 w-full overflow-hidden rounded-[2rem] border border-slate-200 shadow-sm relative group">
              <img className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" src={info.photos[i] ?? HERO_IMAGES[i]} alt="Detail" />
            </div>
          ))}
        </div>
      </section>

      {/* Score & Metrics */}
      <section className="flex flex-col md:flex-row gap-8 items-start">
        <Card className="md:w-72 shrink-0 p-8 rounded-[2rem] border-none shadow-xl shadow-blue-500/5 bg-white relative overflow-hidden">
          <div className="absolute -right-16 -top-16 bg-blue-50 w-48 h-48 rounded-full blur-3xl" />
          <div className="relative z-10">
            <div className="flex items-baseline justify-between mb-8">
              <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Phân loại</h3>
              <span className={`text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full ${TIER_COLOR[info.tier] ?? 'bg-slate-100 text-slate-600'}`}>{info.tier}</span>
            </div>
            <div className="text-center my-6">
              <span className="text-[6rem] font-black tracking-tighter leading-none bg-clip-text text-transparent bg-gradient-to-b from-blue-600 to-indigo-600">
                {info.efficiency_score.toFixed(1)}
              </span>
              <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mt-2">Điểm hiệu quả</p>
            </div>
            <div className="pt-6 border-t border-slate-100 grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Đánh giá</p>
                <p className="text-lg font-black text-slate-900 flex items-center justify-center gap-1">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  {info.stats.avg_rating.toFixed(1)}
                </p>
              </div>
              <div>
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Đúng giờ</p>
                <p className="text-lg font-black text-slate-900">{Math.round(info.stats.on_time_rate * 100)}%</p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="flex-1 p-10 rounded-[2rem] border-slate-200 shadow-sm bg-white">
          <div className="flex items-center gap-3 mb-10">
            <Zap className="text-blue-500 w-5 h-5" />
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest">Chỉ số vận hành</h3>
          </div>
          <div className="space-y-7">
            {Object.entries(info.metrics).map(([key, val]) => {
              const labels: Record<string, string> = { equipment: 'Thiết bị', process: 'Quy trình', staff: 'Nhân viên', capacity: 'Sức chứa', reliability: 'Độ tin cậy' }
              const colors = ['bg-blue-600', 'bg-indigo-500', 'bg-violet-500', 'bg-emerald-500', 'bg-blue-500']
              const idx = Object.keys(info.metrics).indexOf(key)
              return (
                <div key={key} className="grid grid-cols-12 items-center gap-6 group">
                  <label className="col-span-3 text-sm font-bold text-slate-600 group-hover:text-slate-900 transition-colors">{labels[key] ?? key}</label>
                  <div className="col-span-8 h-3 bg-slate-100 rounded-full overflow-hidden shadow-inner">
                    <div className={`h-full ${colors[idx % colors.length]} rounded-full`} style={{ width: `${val * 10}%` }} />
                  </div>
                  <span className="col-span-1 text-sm font-black text-right text-slate-800">{val.toFixed(1)}</span>
                </div>
              )
            })}
          </div>
        </Card>
      </section>

      {/* Amenities & Services */}
      <section className="grid grid-cols-1 md:grid-cols-12 gap-8">
        <div className="md:col-span-4 space-y-6">
          <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest px-2">Tiện ích</h3>
          <div className="grid grid-cols-2 gap-4">
            {amenities.map(key => {
              const a = AMENITY_MAP[key] ?? { icon: Coffee, label: key, color: 'text-slate-500', bg: 'bg-slate-50' }
              return (
                <Card key={key} className="p-6 rounded-3xl border-slate-200 shadow-sm flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow group bg-white">
                  <div className={`w-14 h-14 rounded-2xl ${a.bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <a.icon className={`${a.color} w-7 h-7`} strokeWidth={2} />
                  </div>
                  <span className="text-xs font-bold text-slate-700">{a.label}</span>
                </Card>
              )
            })}
          </div>
        </div>

        <div className="md:col-span-8 flex flex-col space-y-6">
          <div className="flex justify-between items-end px-2">
            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Danh sách dịch vụ</h3>
            <span className="text-[10px] font-bold text-slate-400">VND</span>
          </div>
          <Card className="bg-white border border-slate-200 rounded-[2rem] overflow-hidden shadow-sm flex-1">
            <table className="w-full text-left">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Dịch vụ</th>
                  <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Thời gian</th>
                  <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest text-right">Giá</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {services.map(svc => (
                  <tr key={svc.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-8 py-6 flex items-start gap-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${svc.is_popular ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-50 text-slate-400'}`}>
                        <Droplets className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <p className="text-base font-bold text-slate-900">{svc.name}</p>
                          {svc.is_popular && <span className="text-[9px] font-bold uppercase tracking-widest bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">Phổ biến</span>}
                        </div>
                        <p className="text-xs font-semibold text-slate-500">{svc.desc}</p>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-sm font-bold text-slate-600 flex items-center gap-1.5 pt-9">
                      <Clock className="w-4 h-4" /> {svc.time_mins} phút
                    </td>
                    <td className="px-8 py-6 text-right text-xl font-black text-slate-900 group-hover:text-blue-600 transition-colors">
                      {svc.price_vnd.toLocaleString('vi-VN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </section>

      {/* Capacity Chart */}
      <section>
        <Card className="p-10 pb-12 rounded-[2.5rem] border border-blue-100 shadow-xl shadow-blue-500/5 bg-gradient-to-b from-white to-blue-50/30">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6 border-b border-blue-100/50 pb-8">
            <div>
              <h3 className="text-xl font-bold text-slate-900">Phân tích sức chứa</h3>
              <p className="text-sm font-medium text-slate-500 mt-1">Mức độ hoạt động theo giờ trong ngày</p>
            </div>
            <div className="flex gap-6 bg-white px-5 py-3 rounded-full shadow-sm border border-slate-100">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600">Tải thường</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600">Cao điểm</span>
              </div>
            </div>
          </div>
          <div className="flex items-end justify-between h-56 gap-2 pr-2 mb-10">
            {capacity_load.map(bar => {
              const pct = (bar.load_percent / maxLoad) * 100
              const isPeak = bar.load_percent >= 80
              return (
                <div key={bar.time} className="flex flex-col items-center flex-1 gap-4 group">
                  <div className="w-full relative h-full flex items-end justify-center px-1">
                    <div
                      className={`w-full rounded-t-xl group-hover:-translate-y-2 transition-transform duration-300 ${isPeak ? 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.3)]' : 'bg-blue-400'}`}
                      style={{ height: `${pct}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-bold text-slate-500">{bar.time}</span>
                </div>
              )
            })}
          </div>
          <div className="flex justify-center pt-4">
            <button className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/30 font-bold tracking-wide rounded-full px-12 py-5 group flex items-center transition-all hover:scale-105 active:scale-95">
              <Calendar className="w-5 h-5 mr-3 group-hover:rotate-12 transition-transform" />
              <span className="text-base uppercase tracking-widest">Đặt lịch ngay</span>
            </button>
          </div>
        </Card>
      </section>
    </div>
  )
}
