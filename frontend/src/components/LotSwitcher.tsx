import { useEffect, useState } from 'react'
import { MapPin } from 'lucide-react'
import { garageApi, activeGarage } from '@/services/api'

export interface LotOption { id: string; name: string; district: string; status: string; lot_type: string }

interface Props {
  lots: LotOption[]
  /** super_admin: có ô tìm kiếm vì danh sách là toàn mạng lưới */
  searchable?: boolean
}

/** Chọn bãi đang thao tác (chủ nhiều bãi, hoặc super_admin xem như chủ bãi). Đổi bãi sẽ tải lại trang. */
export function LotSwitcher({ lots, searchable }: Props) {
  const [options, setOptions] = useState<LotOption[]>(lots)
  const [q, setQ] = useState('')
  const currentId = activeGarage.get()

  useEffect(() => setOptions(lots), [lots])

  useEffect(() => {
    if (!searchable) return
    const t = setTimeout(() => {
      garageApi.accessibleGarages(q).then(setOptions).catch(() => {})
    }, 300)
    return () => clearTimeout(t)
  }, [q, searchable])

  const onChange = (id: string) => {
    const lot = options.find((l) => l.id === id)
    if (!lot || id === currentId) return
    activeGarage.set(id, lot.name)
    window.location.reload()
  }

  // Chủ chỉ có 1 bãi: không cần bộ chọn
  if (!searchable && lots.length <= 1) return null

  const hasCurrent = options.some((l) => l.id === currentId)
  return (
    <div className="flex items-center gap-2 min-w-0">
      <MapPin className="w-4 h-4 text-on-surface-variant shrink-0" />
      {searchable && (
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tìm bãi…" aria-label="Tìm bãi"
          className="hidden lg:block w-32 text-xs px-3 py-1.5 rounded-full border border-outline-variant bg-surface" />
      )}
      <select value={currentId} onChange={(e) => onChange(e.target.value)} aria-label="Chọn bãi"
        className="text-xs font-medium max-w-[11rem] sm:max-w-[16rem] truncate px-3 py-1.5 rounded-full border border-outline-variant bg-surface">
        {!hasCurrent && currentId && <option value={currentId}>{activeGarage.name() || 'Bãi đang chọn'}</option>}
        {options.map((l) => <option key={l.id} value={l.id}>{l.name} · {l.district}</option>)}
      </select>
    </div>
  )
}
