# Tài khoản test

Mật khẩu chung: **`test123@`**. Đăng nhập tại https://app.parkinghub.asia

| Username | Vai trò | Vào trang | Ghi chú |
|---|---|---|---|
| `admin` | super_admin | `/admin` | Toàn quyền |
| `ops` | platform_ops | `/admin` | Vận hành nền tảng |
| `owner` | garage_owner | `/garage` | Chủ bãi "Bai Xe Test Q1" (tenant `bai-xe-test-q1`) |
| `manager` | garage_manager | `/garage` | Quản lý ca, cùng bãi với `owner` |
| `staff` | garage_staff | `/garage` | Bảo vệ, cùng bãi với `owner` |
| `driver` | customer | `/app` | Tài xế |
| `fleet` | fleet_manager | `/app` | Quản lý đội xe (dùng app tài xế) |

Tạo lại (idempotent): `docker exec -i -w /app parkinghub-backend-app python - < backend/scripts/create_test_accounts.py`
