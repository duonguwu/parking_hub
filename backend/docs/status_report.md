# Báo cáo tình hình triển khai Phase Quản lý

Cập nhật: 06/10/2026.

## 1. Đã xong

| Commit | Nội dung | Kiểm tra |
|---|---|---|
| `c8ab7b0` | Backend: model bãi mới (loại hình, cấp tích hợp, hạng sao, điểm chất lượng), đặt chỗ theo khoảng thời gian, bảng giá block/flat, chỗ trống và dự đoán, cổng chủ bãi viết lại, API admin `/admin/*` | 152 test pass (`bash scripts/run_tests.sh`) |
| `ab8245a` | Seed demo: khoảng 150 bãi ở 10 quận HCM, 40 tài xế, khoảng 3.700 lượt đặt, snapshot 8 tuần | Đã chạy thử trên DB riêng, kiểm tra mọi màn hình có số liệu |
| `c19bbe4` | Frontend cho cả 3 vai trò: `api.ts` mới, `ParkingMap` dùng chung, app tài xế, cổng chủ bãi, cổng admin | `npm run build` pass |

Các endpoint public mới: `/service-types`, `/garage-services/quote`, `/garage-services/list_by_garage`, `/capacity/current_and_predicted`, `/match/feedback`, `/garage/taxonomy`.

Bãi mới đăng ký có trạng thái `pending_review`. Admin duyệt và đặt cấp tích hợp ở `/admin/garages/:id`.

## 2. Việc còn lại

1. Deploy, rồi seed lên prod: `docker exec -it parkinghub-backend-app uv run python scripts/seed_data.py --reset`. Lệnh này chỉ xoá các bản ghi có `created_by=seed_demo`.
2. Kiểm tra giao diện trên trình duyệt. Hiện mới type-check và build, chưa click thử từng màn hình.
3. Ghi tài khoản demo vào README: chủ bãi `owner_<quận>_<nn>` / `Owner@2026`, tài xế `customer_01..40` / `Customer@2026`.
4. Đổi tên `garage` thành `parking_lot` (bước 8 trong tài liệu 08), làm trên một nhánh riêng.

## 3. Ghi chú kỹ thuật

- Thời lượng mặc định của gói flat ở trang đặt chỗ (đêm 12 giờ, gói ngày làm việc 10 giờ, lượt 4 giờ, tháng 30 ngày) đang khai ở frontend `GarageDetail.tsx`. Giá cuối vẫn do backend tính.
- `backend/docs/portal_head.md` và `portal_services.md` là bản nháp đã gộp vào `garage_portal_utils.py`, có thể xoá.
