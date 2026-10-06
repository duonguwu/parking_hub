import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MapPin, Sparkles, CarFront, ChevronRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, formatVnd, formatDateTime, type DashboardSummary } from '@/services/api'
import { HCM_CENTER } from '@/components/parking/ParkingMap'
import { BookingStatusBadge, EmptyState, Spinner } from '@/components/parking/ParkingBits'
import { SmartBookingModal } from '@/components/SmartBookingModal'
import { useAuth } from '@/services/auth-context'
import { GarageCardView } from './CustomerMap'

function greeting() {
  const h = new Date().getHours()
  return h < 11 ? 'Chào buổi sáng' : h < 14 ? 'Chào buổi trưa' : h < 18 ? 'Chào buổi chiều' : 'Chào buổi tối'
}

export function CustomerHome() {
  const { user } = useAuth()
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    const load = (lat: number, lng: number) =>
      customerApi.dashboardSummary(lat, lng).then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false))
    if (!navigator.geolocation) return void load(HCM_CENTER.lat, HCM_CENTER.lng)
    navigator.geolocation.getCurrentPosition(
      (p) => load(p.coords.latitude, p.coords.longitude),
      () => load(HCM_CENTER.lat, HCM_CENTER.lng),
      { timeout: 5000 },
    )
  }, [])

  return (
    <div className="max-w-4xl mx-auto w-full space-y-5">
      <div>
        <p className="text-sm text-on-surface-variant">{greeting()},</p>
        <h1 className="text-2xl font-black text-on-surface">{user?.name || user?.username || 'bạn'}</h1>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Link to="/app/map" className="rounded-2xl bg-primary text-white p-4 flex flex-col gap-2">
          <MapPin className="w-5 h-5" /><span className="font-bold text-sm">Tìm bãi trên bản đồ</span>
        </Link>
        <button onClick={() => setModalOpen(true)} className="rounded-2xl bg-surface border border-outline-variant p-4 flex flex-col gap-2 text-left">
          <Sparkles className="w-5 h-5 text-primary" /><span className="font-bold text-sm text-on-surface">Gợi ý thông minh</span>
        </button>
      </div>

      {loading ? <Spinner /> : error || !data ? <EmptyState title="Không tải được trang chủ" desc={error} /> : <>
        <Card className="p-4 rounded-2xl flex items-center gap-3">
          <CarFront className="w-6 h-6 text-primary shrink-0" />
          {data.default_vehicle ? (
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-on-surface-variant">Xe mặc định</p>
              <p className="font-bold text-on-surface">{data.default_vehicle.license_plate} · {data.default_vehicle.brand} {data.default_vehicle.model}</p>
            </div>
          ) : <p className="flex-1 text-sm text-on-surface-variant">Bạn chưa có xe mặc định.</p>}
          <Link to="/app/vehicles" className="text-xs font-bold text-primary whitespace-nowrap">Quản lý xe</Link>
        </Card>

        <section>
          <div className="flex justify-between items-center mb-2">
            <h2 className="font-bold text-on-surface">Lượt đặt đang hoạt động</h2>
            <Link to="/app/bookings" className="text-xs font-bold text-primary">Tất cả</Link>
          </div>
          {data.active_bookings.length === 0 ? (
            <Card className="p-0 rounded-2xl"><EmptyState title="Không có lượt đặt nào" desc="Tìm bãi trên bản đồ để giữ chỗ." className="py-6" /></Card>
          ) : (
            <div className="space-y-2">
              {data.active_bookings.map((b) => (
                <Link key={b.id} to={`/app/bookings/${b.id}`} className="flex items-center gap-3 p-3 rounded-2xl bg-surface border border-outline-variant hover:border-primary/50">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-on-surface truncate">{b.garage_name || 'Bãi đỗ'}</p>
                    <p className="text-[11px] text-on-surface-variant">{b.license_plate} · {formatDateTime(b.start_time)} – {formatDateTime(b.end_time)}</p>
                  </div>
                  <BookingStatusBadge status={b.status} />
                  <ChevronRight className="w-4 h-4 text-outline" />
                </Link>
              ))}
            </div>
          )}
        </section>

        <div className="grid grid-cols-3 gap-2">
          {[
            ['Lượt gửi', String(data.stats.total_sessions)],
            ['Tổng chi', formatVnd(data.stats.total_spent)],
            ['Số bãi đã gửi', String(data.stats.lots_visited)],
          ].map(([l, v]) => (
            <Card key={l} className="p-3 rounded-2xl text-center">
              <p className="text-base font-black text-on-surface">{v}</p>
              <p className="text-[10px] text-on-surface-variant">{l}</p>
            </Card>
          ))}
        </div>

        <section>
          <div className="flex justify-between items-center mb-2">
            <h2 className="font-bold text-on-surface">Bãi đỗ gần bạn</h2>
            <Link to="/app/map" className="text-xs font-bold text-primary">Xem bản đồ</Link>
          </div>
          {data.nearby.length === 0 ? <EmptyState title="Chưa tìm thấy bãi nào quanh đây" /> : (
            <div className="grid sm:grid-cols-2 gap-2">{data.nearby.map((g) => <GarageCardView key={g.id} g={g} />)}</div>
          )}
        </section>
      </>}

      <SmartBookingModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}
