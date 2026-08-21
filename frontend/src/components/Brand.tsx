import { APP_NAME } from '@/config/app'
import { cn } from '@/services/utils'

/**
 * Wordmark của sản phẩm. Hiện tại là chữ, chưa dùng file ảnh logo.
 * Khi có logo chính thức, thay phần bên trong bằng thẻ img và giữ nguyên interface.
 */
export function Brand({ className }: { className?: string }) {
  return (
    <span className={cn('text-xl font-extrabold tracking-tight text-primary', className)}>
      {APP_NAME}
    </span>
  )
}
