import { useRegisterSW } from 'virtual:pwa-register/react'
import { RefreshCw, CheckCircle, X } from 'lucide-react'

export function PWABadge() {
  // Check for updates periodically every 60 minutes
  const period = 60 * 60 * 1000

  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(swUrl, r) {
      if (period <= 0) return
      if (r?.active?.state === 'activated') {
        setInterval(async () => {
          if (!(!r.installing && navigator)) return
          if ('onLine' in navigator && !navigator.onLine) return

          const resp = await fetch(swUrl, {
            cache: 'no-store',
            headers: {
              'cache': 'no-store',
              'cache-control': 'no-cache',
            },
          })

          if (resp?.status === 200)
            await r.update()
        }, period)
      }
    },
  })

  const close = () => {
    setOfflineReady(false)
    setNeedRefresh(false)
  }

  if (!offlineReady && !needRefresh) {
    return null
  }

  return (
    <div
      className="fixed bottom-20 md:bottom-6 right-4 md:right-6 z-50 max-w-sm w-full bg-surface border border-outline-variant rounded-2xl p-4 shadow-xl backdrop-blur-md animate-in slide-in-from-bottom-4 duration-300"
      role="alert"
      aria-labelledby="pwa-toast-message"
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center shrink-0 mt-0.5">
          {needRefresh ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <CheckCircle className="w-4 h-4 text-success" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <p id="pwa-toast-message" className="text-xs font-bold text-on-surface">
            {needRefresh
              ? 'Bản cập nhật mới đã sẵn sàng!'
              : 'Sẵn sàng hoạt động ngoại tuyến!'}
          </p>
          <p className="text-[11px] text-on-surface-variant mt-0.5">
            {needRefresh
              ? 'Nhấp cập nhật để tải phiên bản Parking Hub mới nhất.'
              : 'Dữ liệu ứng dụng đã được lưu vào bộ nhớ đệm.'}
          </p>

          <div className="flex items-center gap-2 mt-3">
            {needRefresh && (
              <button
                type="button"
                onClick={() => updateServiceWorker(true)}
                className="bg-primary text-white text-xs font-bold px-3.5 py-1.5 rounded-full hover:opacity-90 transition-opacity"
              >
                Cập nhật ngay
              </button>
            )}
            <button
              type="button"
              onClick={close}
              className="bg-surface-container-low border border-outline-variant text-on-surface-variant text-xs font-bold px-3 py-1.5 rounded-full hover:bg-surface-container transition-colors"
            >
              Đóng
            </button>
          </div>
        </div>

        <button
          type="button"
          onClick={close}
          className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg transition-colors"
          aria-label="Đóng thông báo"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
