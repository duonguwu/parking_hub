import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { X } from 'lucide-react'
import { adminApi, GARAGE_STATUS_LABEL, INTEGRATION_LABEL, type GarageCard } from '@/services/api'
import { ParkingMap, MapLegend } from '@/components/parking/ParkingMap'
import { AvailabilityPill, BadgeList, Stars } from '@/components/parking/ParkingBits'

const sel = 'text-xs border border-outline-variant rounded-full px-3 py-1.5 bg-surface'

export function AdminMap() {
  const [status, setStatus] = useState('')
  const [level, setLevel] = useState('')
  const [items, setItems] = useState<GarageCard[]>([])
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<GarageCard | null>(null)

  useEffect(() => {
    setError('')
    adminApi.map({ status: status || undefined, level: level ? Number(level) : undefined })
      .then(setItems).catch((e) => setError(e.message))
  }, [status, level])

  return (
    <div className="relative h-[calc(100vh-4rem-4.5rem)] md:h-[calc(100vh-4rem)]">
      <ParkingMap garages={items} selectedId={selected?.id} onSelect={setSelected} fitToGarages className="h-full w-full" />
      <div className="absolute top-3 left-3 right-3 z-[500] flex flex-wrap gap-2 items-center">
        <select className={sel} value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Mọi trạng thái</option>
          {Object.entries(GARAGE_STATUS_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select className={sel} value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">Mọi cấp kết nối</option>
          {Object.entries(INTEGRATION_LABEL).map(([k, v]) => <option key={k} value={k}>Cấp {k} · {v}</option>)}
        </select>
        <span className="text-xs bg-surface px-3 py-1.5 rounded-full border border-outline-variant">{items.length} bãi</span>
        {error && <span className="text-xs bg-error/10 text-error px-3 py-1.5 rounded-full">{error}</span>}
      </div>
      <MapLegend className="absolute bottom-3 left-3 z-[500]" />
      {selected && (
        <div className="absolute z-[500] bottom-3 right-3 left-3 sm:left-auto sm:w-80 bg-surface border border-outline-variant rounded-xl p-4 shadow-lg space-y-2">
          <div className="flex justify-between gap-2">
            <div className="min-w-0">
              <p className="font-semibold truncate">{selected.name}</p>
              <p className="text-xs text-on-surface-variant">{selected.address}</p>
            </div>
            <button onClick={() => setSelected(null)} className="text-on-surface-variant shrink-0"><X className="w-4 h-4" /></button>
          </div>
          <div className="flex flex-wrap gap-2 items-center text-xs">
            <Stars value={selected.grade} />
            <span>{selected.lot_type_label}</span>
            <span>· Cấp {selected.integration_level}</span>
            <span>· {GARAGE_STATUS_LABEL[selected.status] ?? selected.status}</span>
          </div>
          <AvailabilityPill a={selected.availability} level={selected.integration_level} showTime />
          <BadgeList badges={selected.badges} max={4} />
          <Link to={`/admin/garages/${selected.id}`} className="block text-center text-sm font-semibold bg-primary text-white rounded-full py-2">Xem chi tiết</Link>
        </div>
      )}
    </div>
  )
}
