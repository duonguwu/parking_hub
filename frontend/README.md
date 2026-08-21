# Parking HUB Web

Frontend cho ba màn hình theo vai trò: khách hàng, chủ bãi, quản trị nền tảng.

Stack: React 18, TypeScript, Vite, Tailwind CSS 4, React Router 6, Leaflet, lucide-react.

## Chạy dự án

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # kiểm tra type và build production
npm run lint
```

Backend mặc định ở `http://localhost:8000`. Đổi bằng biến môi trường `VITE_API_BASE` hoặc sửa `src/config/app.ts`.

## Tài liệu

Hướng dẫn tái sử dụng mã nguồn, cấu trúc thư mục, luồng đăng nhập và phân quyền: `../docs/04_technical/08_Codebase_Guide.md`.
Nguyên tắc thiết kế giao diện và bộ token màu: `../docs/04_technical/09_Frontend_Design_System.md`.
