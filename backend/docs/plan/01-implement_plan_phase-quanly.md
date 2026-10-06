# Phase Quản lý: scope và plan

Mục tiêu: **app chạy đúng nghiệp vụ cho cả 3 vai trò** (tài xế, chủ bãi, admin), xem được bãi trên bản đồ HCM, dữ liệu giả đủ nhiều để demo đi thi. Không làm AI, thời tiết/traffic, hay matching nâng cao.

Đã commit: `9a5800a`, gồm infra, sửa login và nợ kỹ thuật FE. Bạn push để Vercel deploy là login chạy được.

---

## 1. Phân loại bãi: 4 trục và huy hiệu

Tài liệu có 3 trục (loại hình, cấp tích hợp, điểm chất lượng). Như bạn nói, 3 trục này vẫn **chưa phân biệt được bãi chuyên dụng xây hẳn để đỗ xe** (nhà xe cao tầng kiểu Vinhomes/VinFast) **với bãi tạm, bãi "dỏm"** (sân đất, không mái, không đèn). Điểm chất lượng chỉ đo cách bãi vận hành, không đo cơ sở vật chất. Đề xuất thêm **trục thứ 4: Hạng tiêu chuẩn**, giống cách khách sạn xếp sao.

| Trục | Field | Giá trị | Ai đặt | Thay đổi |
|---|---|---|---|---|
| 1. Loại hình | `lot_type` | Thêm **`parking_building` (nhà xe chuyên dụng nhiều tầng)** vào 7 loại cũ: hầm toà nhà, hầm chung cư, bãi ngoài trời, nhà xe có mái, lòng đường/công cộng, chỗ nhỏ hộ dân, đầu mối giao thông | Lúc onboard | Hiếm khi |
| 2. Cấp tích hợp | `integration_level` 1–4 | Danh mục / Có cập nhật / Kết nối cảm nhận / Kết nối đầy đủ | Admin | Khi bãi nâng cấp |
| **3. Hạng tiêu chuẩn** | `grade` 1–5 sao, kèm `grade_assessment` | Tính từ **checklist kiểm định thực địa** (thang 100 điểm) | Admin hoặc người kiểm định | 6 tháng một lần |
| 4. Điểm chất lượng | `quality_score` 0–100 | Tỷ lệ giữ đúng chỗ, tỷ lệ khách không đến, số tranh chấp, tỷ lệ khách quay lại | Tự tính | Liên tục |

**Checklist cho Hạng tiêu chuẩn** (lấy từ tài liệu 05 mục 4):

| Nhóm | Điểm | Tiêu chí |
|---|---|---|
| Kết cấu | 25 | Công trình chuyên dụng hay tận dụng; mặt sàn bê tông/nhựa hay sỏi/đất; kẻ vạch ô đỗ |
| An ninh | 25 | Bảo vệ (không / theo giờ / 24h), camera (không / một phần / toàn bãi), barrier kiểm soát ra vào |
| Che chắn và môi trường | 15 | Hầm, mái toàn phần, mái một phần, ngoài trời; tiền sử ngập; chiếu sáng ban đêm |
| Tiếp cận | 15 | Lối vào rộng, độ dốc, chiều cao thông thuỷ, cách tổ chức đỗ (tự đỗ / có người hướng dẫn / đỗ chồng) |
| An toàn PCCC | 10 | Bình chữa cháy, báo cháy, khu sạc xe điện riêng |
| Tiện ích | 10 | Trụ sạc, nhà vệ sinh, rửa xe, chỗ chờ |

Quy đổi điểm ra sao: **5★ ≥ 85**, 4★ ≥ 70, 3★ ≥ 55, 2★ ≥ 40, còn lại 1★.
- Nhà xe chuyên dụng cao tầng, có bảo vệ 24h và camera toàn bãi: thường **5★**.
- Sân đất ngoài trời, không đèn, đỗ chồng: thường **1–2★**.

**Huy hiệu** (tính tự động, hiện cạnh tên bãi): `Đã kiểm định` · `Bãi chuyên dụng` · `An toàn PCCC` (cấp 4 hoặc đạt mục PCCC) · `Thời gian thực` (cấp 3–4) · `Có sạc EV` · `Giữ đúng chỗ ≥ 98%`.

**Thẻ bãi hiển thị cho tài xế:** `★★★★ · Hầm toà nhà · Thời gian thực · Giữ đúng chỗ 98%`.
- Cấp 1: "Chưa có dữ liệu chỗ trống".
- Cấp 2: "Cập nhật lúc 14:05".
- Cấp 3–4: số liệu giả lập (`occupancy.source = simulated`).

**Cách các trục được dùng:**
- **Cấp tích hợp**: quyết định cam kết. Cấp 1 chỉ xem · cấp 2 đặt chỗ, bãi xác nhận · cấp 3–4 giữ chỗ tự xác nhận · cấp 4 được ưu tiên xếp hạng.
- **Hạng sao và điểm chất lượng**: dùng cho bộ lọc ("từ 3★") và xếp hạng.
- **Chủ bãi không tự sửa** cấp và hạng. Chủ bãi khai thuộc tính, admin kiểm định rồi chấm.

---

## 1b. Kết quả review FE

| Phát hiện | Ở đâu | Xử lý |
|---|---|---|
| **Còn sót nghiệp vụ garage/rửa xe** | `CustomerHome` (`vehicle_diagnostics.finish_degradation`, `wait_time`) · `GarageScore` ("Roadmap to Elite Tier", "ISO Certified", throughput, bays) · `GarageQueue` (trạng thái `in_service`, `completed`, "Appointment Time", "Service Details") · `GarageDetail` (chỉ số equipment/process/staff, ảnh Unsplash) | Viết lại theo nghiệp vụ bãi đỗ |
| **Cổng chủ bãi gần như toàn tiếng Anh** | `GarageDashboard`, `GarageQueue`, `GarageServices`, `GarageAnalytics` (còn có "Server Status", "Version"), `GarageScore` | Việt hoá toàn bộ và bỏ các khối không có thật |
| **Hai design system** | Phía khách dùng token kiểu Material (`surface`, `on-surface`, `primary`); phía chủ bãi dùng thẳng `slate`/`blue` | Giữ token của khách cho app tài xế. Cổng chủ bãi và admin dùng chung một bố cục dashboard |
| **Bản đồ chỉ có ở phía khách** | `CustomerMap` (Leaflet, OSM) | Tách thành component `ParkingMap` dùng chung cho tài xế, admin (toàn mạng lưới) và chủ bãi (bãi của mình) |
| **Đặt chỗ phụ thuộc matching** | `SmartBookingModal` gọi `/match/search` rồi `createBooking(requested_time)` | Thêm luồng **đặt trực tiếp từ trang chi tiết bãi** (chọn dịch vụ, giờ bắt đầu, thời lượng, xem giá). `SmartBookingModal` giữ làm "gợi ý thông minh", chỉ sửa field |
| **Lượt đặt dùng field cũ** | `CustomerBookings` (`requested_time`, `price`, `ACTIVE_STATUSES` cũ), `BookingTracker`, `BOOKING_STATUS_MAP` | Đổi sang `start_time`/`end_time`, `quoted_price`/`final_price` và trạng thái mới |
| **Admin trống, không có menu** | `AdminLayout` chỉ là `Outlet`; `AdminDashboard` 1 dòng | Dựng mới: layout có sidebar, 5 trang (Tổng quan, Bản đồ, Bãi đỗ, Người dùng, Dịch vụ) |
| **Hồ sơ khách trống** | `CustomerProfile` 1 dòng | Làm trang hồ sơ đơn giản: thông tin, đổi mật khẩu, đăng xuất |
| Type-check | `tsc -b` | **Đang pass** (chạy bằng Docker `node:20`) |


## 2. Scope theo vai trò

### Tài xế (`/app`)
| Tính năng | Ghi chú |
|---|---|
| Đăng ký, đăng nhập, quản lý xe | Giữ nguyên code hiện có |
| **Bản đồ HCM** | Marker màu theo tình trạng còn chỗ (xanh/vàng/đỏ/xám nếu cấp 1), bấm vào xem thẻ tóm tắt |
| Bộ lọc | Loại bãi, có mái che/hầm, trụ sạc, chiều cao xe, có bảo vệ, không ngập, khoảng giá |
| Tìm quanh một điểm | Bấm lên bản đồ hoặc chọn vị trí hiện tại, lấy bán kính quanh điểm đó (tạm thay "tìm theo điểm đến" đầy đủ) |
| **Chi tiết bãi** | Thông tin, cấp, thuộc tính, bảng giá, chỗ trống kèm mốc cập nhật, biểu đồ lấp đầy theo giờ, điểm tin cậy |
| **Đặt chỗ** | Chọn dịch vụ (giờ, đêm, ngày), giờ bắt đầu và thời lượng, thấy giá dự kiến, xác nhận. Huỷ được |
| Lượt đặt của tôi | Danh sách và dòng thời gian trạng thái |

### Chủ bãi (`/garage`)
| Tính năng | Ghi chú |
|---|---|
| **Tổng quan** | Chỗ trống hiện tại, xe đang trong bãi, lượt giữ chỗ sắp tới trong 2 giờ, doanh thu hôm nay, tỷ lệ lấp đầy 24 giờ |
| **Cập nhật chỗ trống** | Nút +/− hoặc nhập số (đây là cách cập nhật của bãi cấp 2) |
| **Lượt đặt và vào/ra** | Xác nhận/từ chối (cấp 2), check-in theo biển số, check-out (tự tính tiền bằng `quote_price`), đánh dấu không đến |
| **Hồ sơ bãi** | Sửa thuộc tính, sức chứa, tỷ lệ cho giữ trước, giờ mở cửa, người liên hệ |
| **Dịch vụ và bảng giá** | Bật/tắt dịch vụ, giá theo block, giá cố định, trần theo ngày, giá cao điểm |
| Phân tích | Lấp đầy theo giờ/thứ, doanh thu 30 ngày, nguồn lượt (nền tảng hay vãng lai) |
| Điểm chất lượng | Các chỉ số vận hành và gợi ý cải thiện |

### Admin (`/admin`): hiện là trang trống, phải dựng mới
| Tính năng | Ghi chú |
|---|---|
| **Tổng quan mạng lưới** | Số bãi, số chỗ, tỷ lệ lấp đầy toàn mạng, lượt đặt và doanh thu, phân bố theo quận và theo cấp |
| **Bản đồ mạng lưới** | Toàn bộ bãi, lọc theo cấp và trạng thái |
| **Quản lý bãi** | Danh sách, duyệt bãi chờ (`pending_review`), đổi cấp tích hợp, tạm ngưng |
| Chủ thể và người dùng | Danh sách chủ bãi và khách (API đã có) |
| Danh mục dịch vụ | Thêm, sửa, ẩn dịch vụ cấp nền tảng |

### Ngoài phạm vi phase này (làm sau)
- AI và camera.
- Thời tiết, traffic, camera giao thông.
- Matching theo điểm đến đầy đủ và cá nhân hoá.
- Thanh toán online: MVP chỉ đánh dấu "đã thanh toán", ghi phương thức tiền mặt hoặc chuyển khoản.
- **Luồng mua** gói tháng/gói ngày làm việc: MVP chỉ hiện trong bảng giá, chủ bãi chỉnh giá được.
- Hộ dân tự đăng ký chỗ nhỏ, thông báo/push, dữ liệu tự thay đổi theo thời gian, đổi tên `garage` thành `parking_lot`.

Endpoint `/match/search` cũ được giữ, chỉ sửa cho chạy được với model mới. Không cải tiến trong phase này.

---

## 3. Thay đổi kỹ thuật chính
- **`service_type`**: 8 dịch vụ (`park_hourly`, `park_overnight`, `park_daily`, `park_workday`, `park_monthly`, `ev_charging`, `car_wash`, `valet`), mỗi dịch vụ có `icon`, `unit`, `is_popular`, `sort_order`. Bỏ 3 chỗ đang ghi cứng.
- **`garage_service.pricing`**: block/flat, `daily_cap`, `peak_rules`, kèm hàm `quote_price()` dùng chung.
- **`GarageModel`**: `lot_type`, `integration_level`, `quality_score`, `entrance_location`, `capacity{total_spots, walk_in_spots, monthly_spots, reservable_ratio, grace_minutes}`, `attributes{...}`, `occupancy{occupied, reserved, available, source, updated_at}`, `stats` vận hành, `contacts`. Bỏ `current_load`, `amenities`, các trường thời gian xử lý.
- **`booking`**: `start_time`, `end_time`, `grace_until`, `license_plate`, `quoted_price`, `final_price`, `payment_status`, `source`.
  - Trạng thái: `pending` (cấp 2 chờ bãi) → `reserved` → `checked_in` → `checked_out`, cùng `cancelled`, `rejected`, `no_show`, `expired`.
  - Giữ khoá Redis. Kiểm tra số chỗ đang giữ không vượt `total_spots × reservable_ratio`.
- **`capacity`**: snapshot theo giờ lưu `occupied`/`available`. Dự đoán dựa trên trung bình cùng giờ, cùng thứ trong lịch sử.
- **Endpoint admin mới** `/admin/*`, theo kiểu REST.

---

## 4. Thứ tự làm, mỗi bước 1 commit, bạn push
| Commit | Nội dung | Kiểm tra |
|---|---|---|
| C2 | Danh mục dịch vụ, bảng giá, `quote_price`, màn chủ bãi sửa giá | Test và build |
| C3 | Model bãi mới, API garage, bộ lọc, màn hồ sơ bãi của chủ bãi | Test |
| C4 | Occupancy, booking theo khoảng thời gian, màn lượt đặt và vào/ra của chủ bãi | Test luồng đặt chỗ |
| C5 | FE tài xế: bản đồ, bộ lọc, chi tiết bãi, đặt chỗ | Build FE |
| C6 | Admin: API và màn hình | Build và test |
| C7 | Seed khoảng 150 bãi HCM, 40 khách, khoảng 3.000 lượt trong 90 ngày, snapshot 8 tuần; deploy và seed lên prod | Kiểm tra trên `app.parkinghub.asia` |

Tài khoản demo sau khi seed: `superadmin` (đã có), các chủ bãi `owner_*` và khách `customer_*`. Mật khẩu demo mình sẽ ghi vào README.
