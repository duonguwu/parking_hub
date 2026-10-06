import { useState, useEffect } from 'react'
import { CarFront, Plus, Star, Zap, Loader2, CheckCircle2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { customerApi, type Vehicle } from '@/services/api'
import { SmartBookingModal } from '@/components/SmartBookingModal'

const BODY_LABEL: Record<string, string> = { suv: 'SUV', sedan: 'Sedan', hatchback: 'Hatchback', truck: 'Bán tải', van: 'Xe van', coupe: 'Coupe', mpv: 'MPV' }
const SIZE_LABEL: Record<string, string> = { small: 'Cỡ nhỏ', medium: 'Cỡ vừa', large: 'Cỡ lớn' }
const BODY_ICONS: Record<string, string> = { suv: '🚙', sedan: '🚗', hatchback: '🚘', truck: '🛻', van: '🚐', coupe: '🏎️' }

export function CustomerVehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [settingDefault, setSettingDefault] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ license_plate: '', brand: '', model: '', color: '', body_type: 'sedan' })
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  const addVehicle = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const large = ['suv', 'truck', 'van'].includes(form.body_type)
      await customerApi.addVehicle({ ...form, license_plate: form.license_plate.trim().toUpperCase(),
        size_class: large ? 'large' : 'medium', is_default: vehicles.length === 0 })
      setForm({ license_plate: '', brand: '', model: '', color: '', body_type: 'sedan' })
      setAdding(false)
      await load()
    } catch (err) {
      setFormError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

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
        <button onClick={() => setAdding(!adding)} className="bg-primary hover:opacity-90 text-white font-bold px-4 py-2.5 rounded-full flex items-center gap-1.5 text-xs transition-all active:scale-95">
          <Plus className="w-4 h-4" />
          <span>Thêm xe</span>
        </button>
      </div>

      {adding && (
        <form onSubmit={addVehicle} className="bg-surface rounded-3xl p-5 border border-outline-variant grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {([['license_plate', 'Biển số *', '51A-12345'], ['brand', 'Hãng', 'Toyota'], ['model', 'Dòng xe', 'Vios'], ['color', 'Màu', 'Trắng']] as const).map(([k, label, ph]) => (
            <label key={k} className="flex flex-col gap-1 font-semibold text-on-surface-variant">
              {label}
              <input required={k === 'license_plate'} value={form[k]} placeholder={ph}
                onChange={e => setForm({ ...form, [k]: e.target.value })}
                className="bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2 text-on-surface outline-none focus:border-primary" />
            </label>
          ))}
          <label className="flex flex-col gap-1 font-semibold text-on-surface-variant">
            Kiểu thân xe
            <select value={form.body_type} onChange={e => setForm({ ...form, body_type: e.target.value })}
              className="bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2 text-on-surface">
              {Object.entries(BODY_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
          <div className="flex items-end gap-2">
            <button type="submit" disabled={saving} className="flex-1 bg-primary text-white font-bold py-2.5 rounded-full disabled:opacity-60">
              {saving ? 'Đang lưu…' : 'Lưu xe'}
            </button>
            <button type="button" onClick={() => setAdding(false)} className="px-4 py-2.5 rounded-full border border-outline-variant font-bold">Huỷ</button>
          </div>
          {formError && <p className="sm:col-span-2 text-error font-semibold">{formError}</p>}
        </form>
      )}

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
                      {SIZE_LABEL[vehicle.size_class] ?? vehicle.size_class}
                    </span>
                  </div>
                  <span className="text-3xl">{BODY_ICONS[vehicle.body_type] ?? '🚗'}</span>
                </div>

                {/* Main info */}
                <div className="mb-4">
                  <h3 className="text-lg font-black text-on-surface tracking-tight">{vehicle.brand} {vehicle.model}</h3>
                  <p className="text-xs font-bold text-primary mt-0.5">{vehicle.license_plate}{vehicle.year ? ` · Năm ${vehicle.year}` : ''}</p>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                  <div className="bg-surface-container-low rounded-2xl p-2.5 border border-outline-variant/60">
                    <p className="text-[9px] font-bold text-on-surface-variant uppercase mb-0.5">Màu sắc</p>
                    <p className="font-bold text-on-surface">{vehicle.color || '—'}</p>
                  </div>
                  <div className="bg-surface-container-low rounded-2xl p-2.5 border border-outline-variant/60">
                    <p className="text-[9px] font-bold text-on-surface-variant uppercase mb-0.5">Kiểu thân xe</p>
                    <p className="font-bold text-on-surface">{BODY_LABEL[vehicle.body_type] ?? (vehicle.body_type || '—')}</p>
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
                  <Zap className="w-3.5 h-3.5" /> <span>Gợi ý bãi</span>
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

