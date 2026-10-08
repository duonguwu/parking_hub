import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { trafficCameraApi, type TrafficCamera } from '@/services/api'

export function CameraViewer({ camera }: { camera: TrafficCamera }) {
  const [imageUrl, setImageUrl] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [version, setVersion] = useState(0)

  useEffect(() => {
    return () => { if (imageUrl) URL.revokeObjectURL(imageUrl) }
  }, [imageUrl])

  useEffect(() => {
    if (!camera.snapshot_available) return
    const controller = new AbortController()
    setError('')
    setLoading(true)
    trafficCameraApi.snapshot(camera.id, controller.signal)
      .then((blob) => {
        if (controller.signal.aborted) return
        setImageUrl(URL.createObjectURL(blob))
      })
      .catch((reason) => { if (!controller.signal.aborted) setError(reason.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [camera.id, camera.snapshot_available, version])

  if (!camera.snapshot_available) return <p className='text-xs text-on-surface-variant'>Camera này chưa có nguồn ảnh.</p>
  return <div className='mt-2 w-60 max-w-full text-on-surface'>
    {loading && <p role='status' className='text-xs'>Đang tải ảnh camera...</p>}
    {error && <p role='alert' className='text-xs text-error'>{error}</p>}
    {imageUrl && <img src={imageUrl} alt={`Ảnh mới nhất từ ${camera.name}`} className='w-full h-auto' />}
    <button type='button' onClick={() => setVersion((value) => value + 1)} disabled={loading}
      title='Tải lại ảnh' aria-label='Tải lại ảnh camera'
      className='mt-2 inline-flex items-center gap-1 text-xs text-primary disabled:opacity-50'>
      <RefreshCw size={14} /> Tải lại ảnh
    </button>
    <p className='mt-1 text-xs text-on-surface-variant'>Ảnh chụp tại thời điểm tải, không phải video trực tiếp.</p>
  </div>
}
