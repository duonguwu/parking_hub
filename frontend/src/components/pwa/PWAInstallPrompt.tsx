import { useState, useEffect } from 'react'
import { Download, Smartphone, X } from 'lucide-react'

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[]
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed'
    platform: string
  }>
  prompt(): Promise<void>
}

export function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const [isDismissed, setIsDismissed] = useState(() => {
    return localStorage.getItem('parking_hub_pwa_dismissed') === 'true'
  })

  useEffect(() => {
    // Check if already in standalone mode (already installed)
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone
    if (isStandalone) {
      return
    }

    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
      if (!isDismissed) {
        setIsVisible(true)
      }
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [isDismissed])

  const handleInstallClick = async () => {
    if (!deferredPrompt) return

    await deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice

    if (outcome === 'accepted') {
      setIsVisible(false)
      setDeferredPrompt(null)
    }
  }

  const handleDismiss = () => {
    setIsVisible(false)
    setIsDismissed(true)
    localStorage.setItem('parking_hub_pwa_dismissed', 'true')
  }

  if (!isVisible || !deferredPrompt) {
    return null
  }

  return (
    <aside
      aria-label="Cài đặt ứng dụng Parking Hub"
      className="fixed bottom-20 md:bottom-6 left-4 md:left-6 z-50 max-w-sm w-[calc(100%-2rem)] md:w-auto bg-surface border border-primary/30 rounded-2xl p-4 shadow-xl backdrop-blur-md animate-in slide-in-from-bottom-4 duration-300"
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-2xl bg-primary text-white flex items-center justify-center shrink-0 shadow-md">
          <Smartphone className="w-5 h-5" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-xs font-bold text-on-surface flex items-center gap-1.5">
            Cài đặt Parking Hub
            <span className="text-[9px] bg-primary-container text-on-primary-container font-extrabold px-1.5 py-0.2 rounded uppercase">
              App
            </span>
          </h4>
          <p className="text-[11px] text-on-surface-variant mt-0.5 leading-tight">
            Thêm vào màn hình chính để truy cập nhanh chóng & nhận thông báo trạng thái chỗ đỗ.
          </p>

          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={handleInstallClick}
              className="bg-primary text-white text-xs font-bold px-3.5 py-1.5 rounded-full hover:opacity-90 transition-opacity flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Cài đặt ngay</span>
            </button>
            <button
              onClick={handleDismiss}
              className="text-on-surface-variant hover:text-on-surface text-xs font-bold px-2 py-1.5 transition-colors"
            >
              Để sau
            </button>
          </div>
        </div>

        <button
          onClick={handleDismiss}
          className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg transition-colors"
          aria-label="Đóng"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </aside>
  )
}
