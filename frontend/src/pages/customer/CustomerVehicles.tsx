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
    <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500 pt-6 px-6 pb-24">

      {/* Header */}
      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200 flex justify-between items-center">
        <div>
          <span className="inline-flex items-center gap-2 px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-bold uppercase tracking-widest mb-3 border border-slate-200">
            <CarFront className="w-3.5 h-3.5" /> Garage cá nhân
          </span>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Phương tiện của tôi</h1>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-3.5 rounded-2xl flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all hover:scale-105 active:scale-95">
          <Plus className="w-5 h-5" />
          <span className="hidden sm:inline">Thêm xe</span>
        </button>
      </div>

      {/* Vehicles */}
      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : vehicles.length === 0 ? (
        <div className="text-center py-16 text-slate-400 font-medium">Chưa có xe nào. Hãy thêm xe đầu tiên của bạn!</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {vehicles.map(vehicle => (
            <Card
              key={vehicle.id}
              className={`p-7 rounded-3xl border-2 shadow-sm hover:shadow-lg transition-all duration-300 bg-white group relative overflow-hidden ${vehicle.is_default ? 'border-blue-300 shadow-blue-500/10' : 'border-slate-200 hover:border-blue-200'}`}
            >
              {/* Background decoration */}
              <div className={`absolute -right-8 -top-8 w-32 h-32 rounded-full opacity-10 ${vehicle.is_default ? 'bg-blue-500' : 'bg-slate-200'}`} />

              {/* Header */}
              <div className="flex justify-between items-start mb-6 relative z-10">
                <div className="flex flex-col gap-1.5">
                  {vehicle.is_default && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-100 text-blue-700 rounded-full text-[9px] font-bold uppercase tracking-widest border border-blue-200 self-start">
                      <CheckCircle2 className="w-3 h-3" /> Mặc định
                    </span>
                  )}
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    {vehicle.vehicle_type} · {vehicle.size_class}
                  </span>
                </div>
                <span className="text-4xl">{BODY_ICONS[vehicle.body_type] ?? '🚗'}</span>
              </div>

              {/* Main info */}
              <div className="relative z-10 mb-6">
                <h3 className="text-2xl font-black text-slate-900 tracking-tight">{vehicle.brand} {vehicle.model}</h3>
                <p className="text-sm font-bold text-slate-500 mt-1">{vehicle.license_plate} · {vehicle.year}</p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6 relative z-10">
                <div className="bg-slate-50 rounded-2xl p-3">
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Màu sắc</p>
                  <p className="text-sm font-bold text-slate-900">{vehicle.color}</p>
                </div>
                <div className="bg-slate-50 rounded-2xl p-3">
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Tier tối thiểu</p>
                  <p className="text-sm font-bold text-slate-900">Tier {vehicle.minimum_garage_tier ?? 1}+</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 relative z-10">
                {!vehicle.is_default && (
                  <button
                    onClick={() => setDefault(vehicle.id)}
                    disabled={settingDefault === vehicle.id}
                    className="flex-1 bg-slate-50 hover:bg-blue-50 hover:text-blue-700 text-slate-600 border border-slate-200 hover:border-blue-200 font-bold text-xs py-3 rounded-2xl transition-all flex items-center justify-center gap-2"
                  >
                    {settingDefault === vehicle.id
                      ? <Loader2 className="w-4 h-4 animate-spin" />
                      : <><Star className="w-4 h-4" /> Đặt mặc định</>
                    }
                  </button>
                )}
                <button 
                  onClick={() => setModalOpen(true)}
                  className={`${vehicle.is_default ? 'flex-1' : ''} bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-3 px-4 rounded-2xl transition-all flex items-center justify-center gap-2 shadow-sm shadow-blue-600/20`}
                >
                  <Zap className="w-4 h-4" /> Đặt lịch thông minh
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
