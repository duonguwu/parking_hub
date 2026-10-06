# Tài khoản test

Mật khẩu chung: **`test123@`**. Đăng nhập tại https://app.parkinghub.asia

## Tài khoản có tên cố định

| Username | Vai trò | Vào trang | Ghi chú |
|---|---|---|---|
| `admin` | super_admin | `/admin` | Toàn quyền, ngang `superadmin` trong env. Chuyển được sang giao diện tài xế và chủ bãi (menu bên trái, mục "Chuyển giao diện") |
| `ops` | platform_ops | `/admin` | Vận hành nền tảng |
| `owner` | garage_owner | `/garage` | Chủ "Bãi Xe Test Q1" (tenant `bai-xe-test-q1`) |
| `manager` | garage_manager | `/garage` | Quản lý ca, cùng bãi với `owner` |
| `staff` | garage_staff | `/garage` | Bảo vệ, cùng bãi với `owner` |
| `driver` | customer | `/app` | Tài xế trống dữ liệu, để thử đăng ký xe và đặt mới |
| `fleet` | fleet_manager | `/app` | Quản lý đội xe (dùng app tài xế) |
| `minh.12` | customer | `/app` | Tài xế có 2 xe: Mercedes-Benz S 450 4MATIC (xe sang) và Toyota Vios 2013 (xe cũ). Có lịch sử khoảng 80 lượt, 1 xe đang trong bãi, 1 lượt sắp tới |
| `duong.12` | customer | `/app` | Tài xế có 2 xe: VinFast VF 9 (xe cao cấp) và Kia Morning 2011 (xe cũ). Có lịch sử khoảng 55 lượt, 1 xe đang trong bãi, vài lượt sắp tới |
| `vin.q1` | garage_owner | `/garage` | Chủ **2 bãi**: Vin Parking Đồng Khởi (nhà xe cao tầng, cấp 4, 5 sao) và Vin Parking Nguyễn Huệ (hầm toà nhà, cấp 3) |
| `vin.landmark` | garage_owner | `/garage` | Chủ 1 bãi: Vin Parking Landmark, Bình Thạnh (900 chỗ, cấp 4, 5 sao) |
| `vin.q3` | garage_owner | `/garage` | Chủ **2 bãi** chất lượng khác nhau: Vin Parking Võ Văn Tần (hầm toà nhà, cấp 3) và Vin Parking Nam Kỳ Khởi Nghĩa (sân ngoài, cấp 2, hạng thấp) |

Chủ có nhiều bãi sẽ thấy ô chọn bãi trên thanh trên cùng của cổng chủ bãi. Admin thì có thêm ô tìm bãi để xem như chủ bất kỳ bãi nào.

## Dữ liệu demo hàng loạt (seed)

Mật khẩu khác với nhóm trên:

| Username | Mật khẩu | Ghi chú |
|---|---|---|
| `owner_<quận>_<số>` ví dụ `owner_q1_01` | `Owner@2026` | Chủ bãi demo, khoảng 15% chủ có 2 đến 3 bãi trong cùng quận |
| `customer_01` đến `customer_40` | `Customer@2026` | Tài xế demo, mỗi người 1 đến 2 xe, hạng xe và năm sản xuất khác nhau |

Quy mô seed hiện tại: 262 bãi trải khắp TP.HCM (Quận 1, 3, 4, 5, 6, 7, 8, 10, 11, 12, Bình Thạnh, Phú Nhuận, Tân Bình, Tân Phú, Gò Vấp, Bình Tân, Nhà Bè, TP. Thủ Đức), khoảng 4.700 lượt đặt trong 90 ngày, snapshot lấp đầy theo giờ 8 tuần.

## Lệnh hay dùng

```bash
# Tạo lại tài khoản test cơ bản (idempotent)
docker exec -i -w /app parkinghub-backend-app python - < backend/scripts/create_test_accounts.py

# Seed lại toàn bộ dữ liệu demo (xoá dữ liệu demo cũ, đổi id nên cần đăng nhập lại)
docker cp backend/scripts/seed_data.py parkinghub-backend-app:/app/scripts/seed_data.py
docker exec -w /app parkinghub-backend-app python scripts/seed_data.py --reset

# Kiểm tra nhanh toàn bộ vai trò và luồng đặt chỗ trên domain thật
bash backend/scripts/test_roles_smoke.sh
bash backend/scripts/test_booking_e2e.sh
python3 backend/scripts/check_fe_shapes.py
```
