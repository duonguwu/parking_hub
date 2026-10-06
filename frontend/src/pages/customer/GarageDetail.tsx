import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Calendar, Wifi, Coffee, BatteryCharging, Snowflake, ChevronLeft, Zap, Shield, Loader2, Star, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type GaragePortal, TIER_COLOR } from '@/services/api'
import { SmartBookingModal } from '@/components/SmartBookingModal'

const AMENITY_MAP: Record<string, { icon: React.ElementType; label: string }> = {
  wifi:         { icon: Wifi,           label: 'WiFi miễn phí' },
  coffee:       { icon: Coffee,         label: 'Cà phê / Đồ uống' },
  ev_charging:  { icon: BatteryCharging,label: 'Trạm sạc xe điện EV' },
  climate:      { icon: Snowflake,      label: 'Có mái che / Điều hòa' },
  waiting_area: { icon: Coffee,         label: 'Phòng chờ' },
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
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    if (!id) return
    customerApi.garagePortal(id)
      .then(setPortal)
      .catch(() => setError('Không thể tải thông tin bãi đỗ'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
    </div>
  )

  if (error || !portal) return (
    <div className="text-center py-16 text-on-surface-variant">{error || 'Không tìm thấy bãi đỗ'}</div>
  )

  const { info, amenities, services, capacity_load } = portal
  const maxLoad = Math.max(...capacity_load.map(c => c.load_percent), 1)
  const lowestPrice = services.length > 0 ? Math.min(...services.map(s => s.price_vnd)) : 10000

  return (
    <div className="flex-1 pb-24 md:pb-8 max-w-5xl mx-auto space-y-6 md:space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-300">

      {/* Navigation & Header */}
      <div className="flex justify-between items-center w-full">
        <div className="flex items-center gap-3 md:gap-4">
          <Link to="/app/map" className="p-2.5 rounded-full border border-outline-variant bg-surface hover:bg-surface-container-low transition-colors">
            <ChevronLeft className="w-5 h-5 text-on-surface" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl md:text-3xl font-black text-on-surface">{info.name}</h1>
              {info.is_verified && (
                <span className="bg-success-soft text-success text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Xác thực
                </span>
              )}
            </div>
            <p className="text-xs text-on-surface-variant mt-0.5">{info.address.street}, {info.address.district}</p>
          </div>
        </div>
      </div>

      {/* Hero Photos Gallery */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
        <div className="md:col-span-2 relative overflow-hidden rounded-3xl border border-outline-variant h-56 sm:h-72 md:h-96 group">
          <img className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src={info.photos[0] ?? HERO_IMAGES[0]} alt={info.name} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
          <div className="absolute bottom-4 left-4 md:bottom-6 md:left-6 text-white">
            <span className="text-[10px] font-bold uppercase tracking-wider bg-black/40 backdrop-blur-md px-2.5 py-1 rounded-full mb-1.5 inline-block">
              {info.address.district}
            </span>
            <p className="text-lg md:text-2xl font-bold">{info.name}</p>
          </div>
        </div>
        <div className="hidden md:flex flex-col gap-4">
          {[1, 2].map(i => (
            <div key={i} className="flex-1 overflow-hidden rounded-3xl border border-outline-variant relative group">
              <img className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src={info.photos[i] ?? HERO_IMAGES[i]} alt="Detail" />
            </div>
          ))}
        </div>
      </section>

      {/* Score & Operation Metrics */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <Card className="p-6 rounded-3xl border border-outline-variant bg-surface flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Cấp phân hạng</span>
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded ${TIER_COLOR[info.tier] ?? 'bg-surface-container'}`}>{info.tier}</span>
            </div>
            <div className="text-center my-4">
              <span className="text-5xl md:text-6xl font-black text-primary">
                {info.efficiency_score.toFixed(1)}
              </span>
              <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mt-1">Điểm đánh giá chất lượng</p>
            </div>
          </div>
          <div className="pt-4 border-t border-outline-variant grid grid-cols-2 gap-2 text-center text-xs">
            <div>
              <p className="text-[10px] font-bold text-on-surface-variant uppercase mb-0.5">Xếp hạng</p>
              <p className="font-bold text-on-surface flex items-center justify-center gap-1">
                <Star className="w-3.5 h-3.5 fill-warning text-warning" />
                {info.stats.avg_rating.toFixed(1)}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold text-on-surface-variant uppercase mb-0.5">Độ tin cậy</p>
              <p className="font-bold text-on-surface">{Math.round(info.stats.on_time_rate * 100)}%</p>
            </div>
          </div>
        </Card>

        <Card className="md:col-span-2 p-6 rounded-3xl border border-outline-variant bg-surface">
          <div className="flex items-center gap-2 mb-6">
            <Zap className="text-primary w-5 h-5" />
            <h2 className="text-sm font-bold text-on-surface uppercase tracking-wider">Chỉ số vận hành bãi</h2>
          </div>
          <div className="space-y-4">
            {Object.entries(info.metrics).map(([key, val]) => {
              const labels: Record<string, string> = { equipment: 'Cơ sở hạ tầng & Camera', process: 'Quy trình kiểm soát', staff: 'Nhân sự hỗ trợ', capacity: 'Quy mô sức chứa', reliability: 'Độ chuẩn xác chỗ trống' }
              return (
                <div key={key} className="grid grid-cols-12 items-center gap-2 sm:gap-4 text-xs">
                  <label className="col-span-5 sm:col-span-4 font-semibold text-on-surface-variant truncate">{labels[key] ?? key}</label>
                  <div className="col-span-5 sm:col-span-7 h-2.5 bg-surface-container-low border border-outline-variant/50 rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full" style={{ width: `${val * 10}%` }} />
                  </div>
                  <span className="col-span-2 sm:col-span-1 font-bold text-right text-on-surface">{val.toFixed(1)}</span>
                </div>
              )
            })}
          </div>
        </Card>
      </section>

      {/* Services & Amenities */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider px-1">Tiện ích bãi đỗ</h3>
          <div className="grid grid-cols-2 sm:grid-cols-1 gap-2.5">
            {amenities.map(key => {
              const a = AMENITY_MAP[key] ?? { icon: Coffee, label: key }
              return (
                <Card key={key} className="p-3.5 rounded-2xl border border-outline-variant bg-surface flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center shrink-0">
                    <a.icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-semibold text-on-surface">{a.label}</span>
                </Card>
              )
            })}
          </div>
        </div>

        <div className="md:col-span-2 space-y-3">
          <div className="flex justify-between items-center px-1">
            <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Bảng giá dịch vụ</h3>
            <span className="text-[10px] font-bold text-on-surface-variant">VNĐ</span>
          </div>

          <div className="space-y-2.5">
            {services.map(svc => (
              <Card key={svc.id} className="p-4 rounded-2xl border border-outline-variant bg-surface flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-on-surface">{svc.name}</h4>
                    {svc.is_popular && (
                      <span className="text-[9px] font-bold uppercase bg-primary-container text-on-primary-container px-2 py-0.5 rounded-full">Phổ biến</span>
                    )}
                  </div>
                  <p className="text-xs text-on-surface-variant mt-0.5">{svc.desc}</p>
                </div>
                <div className="flex items-center justify-between sm:justify-end gap-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-outline-variant/50">
                  <span className="text-xs text-on-surface-variant flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-outline" /> {svc.time_mins}p
                  </span>
                  <span className="text-base font-black text-primary">
                    {svc.price_vnd.toLocaleString('vi-VN')} đ
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Capacity Chart */}
      <section>
        <Card className="p-6 md:p-8 rounded-3xl border border-outline-variant bg-surface">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3 border-b border-outline-variant pb-4">
            <div>
              <h3 className="text-base font-bold text-on-surface">Dự báo tải công suất</h3>
              <p className="text-xs text-on-surface-variant">Tình trạng chỗ trống theo giờ trong ngày</p>
            </div>
            <div className="flex gap-4 text-xs font-semibold">
              <div className="flex items-center gap-1.5 text-on-surface-variant">
                <span className="w-2.5 h-2.5 rounded-full bg-primary" />
                <span>Bình thường</span>
              </div>
              <div className="flex items-center gap-1.5 text-on-surface-variant">
                <span className="w-2.5 h-2.5 rounded-full bg-error" />
                <span>Cao điểm</span>
              </div>
            </div>
          </div>

          <div className="flex items-end justify-between h-40 gap-1 sm:gap-2 mb-6">
            {capacity_load.map(bar => {
              const pct = (bar.load_percent / maxLoad) * 100
              const isPeak = bar.load_percent >= 80
              return (
                <div key={bar.time} className="flex flex-col items-center flex-1 gap-2 group">
                  <div className="w-full relative h-full flex items-end justify-center">
                    <div
                      className={`w-full max-w-[28px] rounded-t-md transition-all ${isPeak ? 'bg-error' : 'bg-primary'}`}
                      style={{ height: `${pct}%` }}
                    />
                  </div>
                  <span className="text-[9px] font-bold text-on-surface-variant">{bar.time}</span>
                </div>
              )
            })}
          </div>

          <div className="hidden md:flex justify-center pt-2">
            <button
              onClick={() => setModalOpen(true)}
              className="bg-primary hover:opacity-90 text-white font-bold text-sm tracking-wide rounded-full px-10 py-3.5 flex items-center transition-all active:scale-95 border border-primary/20"
            >
              <Calendar className="w-4 h-4 mr-2" />
              <span>ĐẶT CHỖ TẠI BÃI NÀY</span>
            </button>
          </div>
        </Card>
      </section>

      {/* ── Sticky Bottom Action Bar trên Mobile ── */}
      <div className="md:hidden fixed bottom-14 left-0 right-0 z-30 bg-surface/95 backdrop-blur-md border-t border-outline-variant px-4 py-3 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-bold text-on-surface-variant">Giá chỉ từ</span>
          <p className="text-base font-black text-primary">{lowestPrice.toLocaleString('vi-VN')} đ</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-full hover:opacity-90 transition-opacity flex items-center gap-1.5"
        >
          <Calendar className="w-4 h-4" />
          <span>Đặt chỗ ngay</span>
        </button>
      </div>

      <SmartBookingModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}

