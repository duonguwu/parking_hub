import { useEffect, useState } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { Marker, Popup, useMapEvents } from 'react-leaflet'
import { Camera } from 'lucide-react'
import L from 'leaflet'
import { trafficCameraApi, type TrafficCamera } from '@/services/api'
import { CameraViewer } from './CameraViewer'

const cameraIcon = L.divIcon({
  className: 'traffic-camera-marker',
  html: renderToStaticMarkup(<span className='traffic-camera-marker__symbol'><Camera size={15} strokeWidth={2} /></span>),
  iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -16],
})

function viewport(map: L.Map) {
  const bounds = map.getBounds()
  return {
    west: bounds.getWest(), south: bounds.getSouth(),
    east: bounds.getEast(), north: bounds.getNorth(),
  }
}

export function CameraLayer({ onStatus }: { onStatus: (message: string) => void }) {
  const [cameras, setCameras] = useState<TrafficCamera[]>([])
  const map = useMapEvents({ moveend: () => setBounds(viewport(map)) })
  const [bounds, setBounds] = useState(() => viewport(map))

  useEffect(() => {
    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      if (bounds.east - bounds.west > 0.5 || bounds.north - bounds.south > 0.5) {
        setCameras([])
        onStatus('Phóng to bản đồ để xem camera trong khu vực.')
        return
      }
      onStatus('Đang tải camera...')
      trafficCameraApi.inViewport(bounds, controller.signal)
        .then((items) => { setCameras(items); onStatus(items.length ? '' : 'Không có camera trong khu vực này.') })
        .catch((error) => { if (controller.signal.aborted) return; setCameras([]); onStatus(error.message) })
    }, 250)
    return () => { window.clearTimeout(timer); controller.abort() }
  }, [bounds, onStatus])

  return cameras.map((camera) => <Marker key={camera.id} position={[camera.lat, camera.lng]} icon={cameraIcon}>
    <Popup>
      <div className='min-w-40 text-on-surface'>
        <p className='font-semibold'>{camera.name}</p>
        <p className='text-xs text-on-surface-variant'>{camera.district}</p>
        <CameraViewer camera={camera} />
      </div>
    </Popup>
  </Marker>)
}
