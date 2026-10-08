import { useEffect, useState } from 'react'
import { Camera } from 'lucide-react'
import { trafficCameraApi, type MatchResult, type TrafficCamera } from '@/services/api'
import { CameraViewer } from './CameraViewer'

export function RouteCameraList({ match }: { match: MatchResult }) {
  const [cameras, setCameras] = useState<TrafficCamera[]>([])
  const [status, setStatus] = useState('')
  const [available, setAvailable] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const route = match.route
  useEffect(() => {
    const controller = new AbortController()
    trafficCameraApi.availability(controller.signal)
      .then((data) => { if (!controller.signal.aborted) setAvailable(data.enabled) })
      .catch(() => { if (!controller.signal.aborted) setAvailable(false) })
    return () => controller.abort()
  }, [])
  useEffect(() => {
    setCameras([])
    setSelectedId(null)
    if (!available || match.route_source !== 'osrm' || !route?.length) return
    setStatus('Đang tìm camera gần tuyến...')
    const controller = new AbortController()
    trafficCameraApi.alongRoute(route, controller.signal)
      .then((items) => { setCameras(items); setStatus(items.length ? '' : 'Không có camera gần tuyến này.') })
      .catch((error) => { if (!controller.signal.aborted) setStatus(error.message) })
    return () => controller.abort()
  }, [available, match.route_source, route])

  if (!available || match.route_source !== 'osrm') return null
  return <section className='border-t border-outline-variant pt-3 mt-3'>
    <h3 className='flex items-center gap-2 text-sm font-semibold text-on-surface'><Camera size={16} />Camera gần tuyến</h3>
    {status && <p className='text-xs text-on-surface-variant mt-2'>{status}</p>}
    {cameras.length > 0 && <div className='mt-2 max-h-48 overflow-y-auto divide-y divide-outline-variant'>
      {cameras.map((camera) => <div key={camera.id} className='py-2 text-xs'>
        <button type='button' onClick={() => setSelectedId((id) => id === camera.id ? null : camera.id)}
          aria-expanded={selectedId === camera.id} className='text-left font-medium text-primary'>
          {camera.name}
        </button>
        <p className='text-on-surface-variant'>{Math.round((camera.distance_from_start_m ?? 0) / 100) / 10} km từ điểm đi</p>
        {selectedId === camera.id && <CameraViewer camera={camera} />}
      </div>)}
    </div>}
  </section>
}
