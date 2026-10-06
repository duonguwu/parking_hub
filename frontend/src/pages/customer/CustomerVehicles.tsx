import { useState, useEffect } from 'react'
import { CarFront, Plus, Star, Zap, Loader2, CheckCircle2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type Vehicle } from '@/services/api'
import { SmartBookingModal } from '@/components/SmartBookingModal'

const BODY_ICONS: Record<string, string> = { suv: '🚙', sedan: '🚗', hatchback: '🚘', truck: '🛻', van: '🚐', coupe: '🏎️' }

export function CustomerVehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [settingDefault, setSettingDefault] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const load = () => customerApi.vehicles().then(setVehicles).catch(console.error).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const setDefault = async (id: string) => {
    setSettingDefault(id)
    try {
      await customerApi.setDefaultVehicle(id)
      await load()
    } catch (e) {
      console.error(e)
    } finally {
      setSettingDefault(null)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">

      {/* Header */}
      <div className="bg-surface rounded-3xl p-5 sm:p-6 border border-outline-variant flex justify-between items-center">
        <div>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-surface-container-low text-on-surface-variant rounded-full text-[10px] font-bold uppercase tracking-wider mb-2 border border-outline-variant">
            <CarFront className="w-3 h-3" /> Danh sách xe
          </span>
          <h1 className="text-xl sm:text-2xl font-black text-on-surface tracking-tight">Phương tiện đã lưu</h1>
        </div>
        <button className="bg-primary hover:opacity-90 text-white font-bold px-4 py-2.5 rounded-full flex items-center gap-1.5 text-xs transition-all active:scale-95">
          <Plus className="w-4 h-4" />
          <span>Thêm xe</span>
        </button>
      </div>

      {/* Vehicles */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
        </div>
      ) : vehicles.length === 0 ? (
        <div className="text-center py-12 text-on-surface-variant text-xs font-medium bg-surface rounded-3xl border border-outline-variant">
          Chưa có xe nào. Hãy thêm phương tiện đầu tiên của bạn!
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {vehicles.map(vehicle => (
            <Card
              key={vehicle.id}
              className={`p-5 rounded-3xl border transition-all bg-surface flex flex-col justify-between ${
                vehicle.is_default ? 'border-primary bg-primary-container/5' : 'border-outline-variant'
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex justify-between items-start mb-3">
                  <div className="flex flex-col gap-1">
                    {vehicle.is_default && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-success-soft text-success rounded-full text-[10px] font-bold uppercase tracking-wider self-start">
                        <CheckCircle2 className="w-3 h-3" /> Mặc định
                      </span>
                    )}
                    <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
                      {vehicle.vehicle_type} · {vehicle.size_class}
                    </span>
                  </div>
                  <span className="text-3xl">{BODY_ICONS[vehicle.body_type] ?? '🚗'}</span>
                </div>

                {/* Main info */}
                <div className="mb-4">
                  <h3 className="text-lg font-black text-on-surface tracking-tight">{vehicle.brand} {vehicle.model}</h3>
                  <p className="text-xs font-bold text-primary mt-0.5">{vehicle.license_plate} · Năm {vehicle.year}</p>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                  <div className="bg-surface-container-low rounded-2xl p-2.5 border border-outline-variant/60">
                    <p className="text-[9px] font-bold text-on-surface-variant uppercase mb-0.5">Màu sắc</p>
                    <p className="font-bold text-on-surface">{vehicle.color}</p>
                  </div>
                  <div className="bg-surface-container-low rounded-2xl p-2.5 border border-outline-variant/60">
                    <p className="text-[9px] font-bold text-on-surface-variant uppercase mb-0.5">Cấp tối thiểu</p>
                    <p className="font-bold text-on-surface">Tier {vehicle.minimum_garage_tier ?? 1}+</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2 border-t border-outline-variant/60">
                {!vehicle.is_default && (
                  <button
                    onClick={() => setDefault(vehicle.id)}
                    disabled={settingDefault === vehicle.id}
                    className="flex-1 bg-surface border border-outline-variant hover:border-primary text-on-surface-variant font-bold text-xs py-2.5 rounded-full transition-all flex items-center justify-center gap-1"
                  >
                    {settingDefault === vehicle.id
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : <><Star className="w-3.5 h-3.5" /> <span>Đặt mặc định</span></>
                    }
                  </button>
                )}
                <button 
                  onClick={() => setModalOpen(true)}
                  className={`${vehicle.is_default ? 'flex-1' : ''} bg-primary hover:opacity-90 text-white font-bold text-xs py-2.5 px-4 rounded-full transition-all flex items-center justify-center gap-1.5`}
                >
                  <Zap className="w-3.5 h-3.5" /> <span>Đặt chỗ xe này</span>
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <SmartBookingModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}

