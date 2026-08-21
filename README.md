# Parking HUB

Mạng lưới bãi đỗ xe ô tô thông minh cho đô thị Việt Nam.

Trạng thái: đang tái cấu trúc từ một nền tảng điều phối mạng lưới điểm dịch vụ sẵn có sang nghiệp vụ bãi đỗ xe. Phần khung gồm xác thực, phân quyền theo vai trò, ba màn hình theo vai trò, và các module nghiệp vụ nền đã chạy được.

## Tài liệu

Bắt đầu từ [docs/README.md](docs/README.md).

| Nhóm | Tài liệu |
|---|---|
| Chiến lược và sản phẩm | `docs/01_strategy-product/` |
| Kinh doanh và vận hành | `docs/02_business-operations/` |
| Hồ sơ cuộc thi | `docs/03_submission/` |
| Hướng dẫn kỹ thuật | `docs/04_technical/` |
| Nguồn dữ liệu và giả định | `docs/99_reference/` |

## Cấu trúc repo

```
backend/     FastAPI, MongoDB, Redis, dịch vụ định tuyến và thời tiết
frontend/    React, TypeScript, Vite, Tailwind
docs/        Tài liệu dự án
```

## Chạy nhanh

```bash
# Backend
cd backend
cp .env.sample .env        # sửa lại thông tin kết nối
uv run uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Chi tiết yêu cầu môi trường, tài khoản seed và cách kiểm tra nằm trong `docs/04_technical/08_Codebase_Guide.md`.
