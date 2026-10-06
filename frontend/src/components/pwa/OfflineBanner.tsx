import { useState, useEffect } from 'react'
import { WifiOff } from 'lucide-react'

export function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine)

  useEffect(() => {
    const handleOnline = () => setIsOffline(false)
    const handleOffline = () => setIsOffline(true)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (!isOffline) {
    return null
  }

  return (
    <div
      role="status"
      className="fixed top-0 inset-x-0 z-[200] bg-error text-white text-xs font-semibold px-4 py-2 flex items-center justify-center gap-2 shadow-md animate-in slide-in-from-top duration-300"
    >
      <WifiOff className="w-4 h-4 shrink-0 animate-pulse" />
      <span>
        Bạn đang ngoại tuyến. Bản đồ và dữ liệu đã lưu trong bộ nhớ đệm PWA vẫn sẵn sàng.
      </span>
    </div>
  )
}
