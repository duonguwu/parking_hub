// Cấu hình nhận diện ứng dụng. Đổi tên sản phẩm ở đúng một chỗ này.
export const APP_NAME = 'Parking HUB'
export const APP_TAGLINE = 'Mạng lưới bãi đỗ xe thông minh'

// Địa chỉ backend. Ưu tiên VITE_API_BASE.
// Dev: relative path ('') để Vite proxy chuyển tiếp tới backend local.
// Production (Vercel): mặc định https://api.parkinghub.asia.
export const API_BASE =
  import.meta.env.VITE_API_BASE ?? (import.meta.env.PROD ? 'https://api.parkinghub.asia' : '')

