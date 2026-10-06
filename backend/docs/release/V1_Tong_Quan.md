# Parking HUB V1: tổng quan nhanh cho team

Cập nhật: 06/10/2026. Đọc khoảng 5 phút là nắm được hệ thống đang ở đâu.

Trạng thái: ứng dụng đã dùng được cho cả 3 vai trò (API đã test, giao diện chưa test trên trình duyệt thật). Hướng dẫn tính năng: [huong_dan_tinh_nang.md](../huong_dan_tinh_nang.md). Kế hoạch tiếp theo: [Ke_Hoach_Tiep_Theo.md](../plan/Ke_Hoach_Tiep_Theo.md).

Parking HUB là nền tảng kết nối tài xế với mạng lưới bãi đỗ xe tại TP.HCM. Bản V1 phục vụ demo cuộc thi: dữ liệu là dữ liệu giả, không có AI, thời tiết hay giao thông.

---

## 1. Trạng thái hệ thống

| Thành phần | Địa chỉ | Chạy ở đâu | Tình trạng |
|---|---|---|---|
| Landing page | https://parkinghub.asia | Vercel | Đang chạy |
| Ứng dụng (tài xế, chủ bãi, admin) | https://app.parkinghub.asia | Vercel, tự deploy khi push lên GitHub `main` | Đang chạy |
| API backend | https://api.parkinghub.asia | VPS riêng, Nginx (HTTPS) chuyển vào cổng 8000 | Đang chạy, kiểm tra tại `/health` |
| Cơ sở dữ liệu | MongoDB | Docker trên VPS | Đang chạy |
| Cache và khoá đặt chỗ | Redis | Docker trên VPS | Đang chạy, rất nhẹ (khoảng 5 MB) |

Tài nguyên VPS: 2 CPU, 4 GB RAM, ổ 50 GB (đã dùng 21%). Backend dùng khoảng 80 MB RAM, Mongo khoảng 280 MB, nên còn dư nhiều chỗ.

Quy trình cập nhật:
- **Frontend:** push code lên `main`, Vercel tự build và deploy.
- **Backend:** vào thư mục `backend/` trên VPS, chạy `docker compose -f docker-compose.prod.yml up -d --build`.

Công nghệ: FE React + TypeScript + Vite + Tailwind, bản đồ Leaflet. BE FastAPI (Python), MongoDB, Redis. Đăng nhập bằng cookie bảo mật, tự làm mới token.

Chất lượng hiện tại: 152 test backend đạt, FE qua kiểm tra kiểu, có 3 script kiểm tra nhanh trên domain thật (xem mục 6).

---

## 2. Ba màn hình và tính năng

Mọi người dùng chung một trang đăng nhập, hệ thống tự đưa về đúng khu vực theo vai trò.

### Tài xế (`/app`)

| Màn hình | Làm được gì |
|---|---|
| Trang chủ | Xe mặc định, lượt đặt đang diễn ra, gợi ý bãi gần bạn |
| Bản đồ | Bãi đỗ trên bản đồ HCM, màu theo tình trạng còn chỗ. Lọc theo loại bãi, mái che, trụ sạc EV, bảo vệ, không ngập, chiều cao xe, giá. Tìm quanh một điểm bấm trên bản đồ |
| Chi tiết bãi | Hạng sao, cấp tích hợp, thuộc tính, bảng giá từng dịch vụ, chỗ trống kèm giờ cập nhật, dự báo lấp đầy theo giờ, đánh giá |
| Đặt chỗ | Chọn dịch vụ (giờ, đêm, ngày...), giờ vào và giờ ra, xem giá dự kiến rồi xác nhận. Gợi ý thông minh có sẵn nếu chưa chọn bãi |
| Lượt đặt | Danh sách, theo dõi trạng thái, huỷ lượt, đánh giá sau khi dùng |
| Xe | Thêm và quản lý xe, đặt xe mặc định |
| Hồ sơ | Thông tin cá nhân, đăng xuất |

### Chủ bãi, quản lý, nhân viên (`/garage`)

| Màn hình | Làm được gì |
|---|---|
| Tổng quan | Chỗ trống hiện tại (nút cộng trừ để cập nhật), xe đang trong bãi, lượt sắp tới trong 2 giờ, doanh thu hôm nay, biểu đồ lấp đầy 24 giờ |
| Lượt đặt và vào/ra | Bốn tab: sắp tới, chờ xác nhận, đang trong bãi, lịch sử. Xác nhận hoặc từ chối, check-in theo biển số (sai biển bị chặn), check-out tự tính tiền, ghi nhận không đến, đánh dấu đã thanh toán, thêm xe vãng lai |
| Hồ sơ bãi | Sửa sức chứa, tỷ lệ cho giữ trước, thuộc tính, giờ mở cửa, liên hệ |
| Dịch vụ và giá | Bật tắt dịch vụ, giá theo block hoặc giá cố định, trần theo ngày, giá giờ cao điểm |
| Phân tích | Doanh thu, số lượt, thời lượng trung bình, lấp đầy theo giờ, nguồn lượt (app hay vãng lai) |
| Chất lượng | Điểm chất lượng tính từ số liệu vận hành, hạng sao kiểm định, gợi ý cải thiện |

Chủ có nhiều bãi sẽ có ô chọn bãi ở thanh trên cùng.

### Quản trị viên (`/admin`)

| Màn hình | Làm được gì |
|---|---|
| Tổng quan | Số bãi, số chỗ, lấp đầy toàn mạng, lượt đặt và doanh thu 30 ngày, phân bố theo quận, cấp, loại bãi |
| Bản đồ | Toàn bộ bãi, lọc theo cấp và trạng thái |
| Bãi đỗ | Danh sách, duyệt bãi chờ, tạm ngưng, đổi cấp tích hợp, chấm checklist kiểm định (100 điểm) để ra hạng sao |
| Người dùng | Tìm, khoá và mở tài khoản |
| Dịch vụ | Danh mục dịch vụ của nền tảng (thêm, sửa, ẩn) |
| Chuyển giao diện | Chỉ super admin: xem như tài xế, hoặc xem như chủ của bất kỳ bãi nào |

---

## 3. Cách phân loại một bãi (gặp ở mọi màn hình)

| Trục | Ý nghĩa |
|---|---|
| Loại hình | 8 loại: nhà xe chuyên dụng, hầm toà nhà, hầm chung cư, nhà xe có mái, bãi ngoài trời, đầu mối giao thông, lòng đường, chỗ hộ dân |
| Cấp tích hợp (1 đến 4) | Cấp 1 chỉ để xem. Cấp 2 nhận đặt, bãi phải xác nhận. Cấp 3 và 4 giữ chỗ tự xác nhận. Cấp càng cao thì dữ liệu chỗ trống càng đáng tin |
| Hạng sao (1 đến 5) | Admin kiểm định thực địa theo checklist 100 điểm: kết cấu, an ninh, che chắn, tiếp cận, PCCC, tiện ích. Chủ bãi không tự sửa |
| Điểm chất lượng | Tự tính từ vận hành: giữ đúng chỗ, tỷ lệ khách không đến, khiếu nại, khách quay lại |

---

## 4. Dữ liệu đang có

Toàn bộ là dữ liệu giả để demo, đã nạp thẳng vào hệ thống thật.

| Hạng mục | Số lượng |
|---|---|
| Bãi đỗ | 262 bãi, tổng 36.798 chỗ, trải 18 quận huyện HCM |
| Trạng thái bãi | 244 hoạt động, 13 chờ duyệt, 5 tạm ngưng |
| Loại hình | Hầm chung cư 68, ngoài trời 46, hầm văn phòng 44, nhà xe có mái 32, hộ dân 24, nhà xe chuyên dụng 18, lòng đường 17, đầu mối giao thông 13 |
| Cấp tích hợp | Cấp 1: 49, cấp 2: 103, cấp 3: 79, cấp 4: 31 |
| Hạng sao | 1 sao: 100, 2 sao: 41, 3 sao: 43, 4 sao: 53, 5 sao: 25 |
| Chủ bãi | 220 tài khoản, 36 chủ có từ 2 đến 3 bãi |
| Tài xế | 43 tài khoản, 53 xe thuộc các hạng phổ thông, cao cấp, xe sang |
| Lượt đặt | khoảng 4.700 trong 90 ngày (đã xong, đang trong bãi, huỷ, không đến, sắp tới, chờ xác nhận) |
| Bảng giá | 943 dịch vụ gắn với các bãi, giá khác nhau theo quận và loại bãi |
| Lịch sử lấp đầy | khoảng 267.000 mốc theo giờ trong 8 tuần, dùng cho biểu đồ và dự báo |

Dữ liệu chỗ trống ở bãi cấp 3 và 4 là số liệu giả lập (nhãn "Thời gian thực"), bãi cấp 2 do chủ bãi tự cập nhật.

### Tài khoản để dùng thử

Mật khẩu `test123@` cho các tài khoản có tên cố định:

| Muốn xem | Đăng nhập bằng |
|---|---|
| Tài xế đầy đủ dữ liệu, 2 xe (xe sang và xe cũ) | `minh.12`, `duong.12` |
| Chủ nhiều bãi | `vin.q1` (2 bãi), `vin.q3` (2 bãi, chất lượng khác nhau) |
| Chủ một bãi lớn | `vin.landmark` (900 chỗ) |
| Chủ, quản lý, nhân viên cùng một bãi | `owner`, `manager`, `staff` |
| Quản trị, chuyển được sang giao diện khác | `admin` |
| Tài xế trống để thử đăng ký xe và đặt mới | `driver` |

Danh sách đầy đủ, kể cả 220 chủ bãi và 40 tài xế demo, nằm ở [TEST_ACCOUNTS.md](../TEST_ACCOUNTS.md).

---

## 5. Chưa làm trong V1

- AI nhận diện biển số, đếm chỗ trống bằng camera, phát hiện khói lửa.
- Thời tiết, giao thông, camera giao thông.
- Thanh toán online (hiện chỉ đánh dấu đã thu tiền mặt hoặc chuyển khoản).
- Luồng mua gói tháng và gói ngày làm việc (hiện chỉ hiển thị trong bảng giá).
- Thông báo đẩy, hộ dân tự đăng ký chỗ nhỏ, dữ liệu tự biến động theo kịch bản.
- Tìm bãi theo điểm đến đầy đủ và cá nhân hoá gợi ý (đã có bản cơ bản).

---

## 6. Cho người vận hành

Ba script kiểm tra trên domain thật, chạy từ thư mục gốc dự án:

```bash
bash backend/scripts/test_roles_smoke.sh      # đăng nhập mọi vai trò, gọi các endpoint chính, kiểm tra phân quyền
bash backend/scripts/test_booking_e2e.sh      # đặt chỗ, vào, ra, thanh toán, huỷ, các ca lỗi
python3 backend/scripts/check_fe_shapes.py    # kiểm tra dữ liệu BE khớp với kiểu FE đang đọc
```

Nạp lại dữ liệu demo (xoá dữ liệu demo cũ rồi tạo mới, sau đó mọi người cần đăng nhập lại):

```bash
docker cp backend/scripts/seed_data.py parkinghub-backend-app:/app/scripts/seed_data.py
docker exec -w /app parkinghub-backend-app python scripts/seed_data.py --reset
```

Chạy test backend: `bash backend/scripts/run_tests.sh -q`.
