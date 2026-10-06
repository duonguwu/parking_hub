// Cấu hình nhận diện ứng dụng. Đổi tên sản phẩm ở đúng một chỗ này.
export const APP_NAME = 'Parking HUB'
export const APP_TAGLINE = 'Mạng lưới bãi đỗ xe thông minh'

// Địa chỉ backend. Mặc định dùng relative path ('') để Vite proxy tự động chuyển tiếp tới backend, giúp chạy mượt qua Cloudflare Tunnel/LAN mà không bị lỗi CORS/Mixed Content.
export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

