// Cấu hình nhận diện ứng dụng. Đổi tên sản phẩm ở đúng một chỗ này.
export const APP_NAME = 'Parking HUB'
export const APP_TAGLINE = 'Mạng lưới bãi đỗ xe thông minh'

// Địa chỉ backend. Đặt VITE_API_BASE trong file .env của frontend để override.
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
