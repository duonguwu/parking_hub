# WashMind Frontend — Feature List

> Stack: React + TypeScript + Vite + TailwindCSS + shadcn/ui
> 3 portals: Customer App (`/app`), Garage Portal (`/garage`), Admin Platform (`/admin`)

---

## 1. Customer App — `/app`

Mục tiêu: User tìm gara, đặt lịch, theo dõi trạng thái rửa xe.

### Trang chính
- **Home / Search**: Tìm gara thông minh — nhập vị trí, chọn xe, chọn dịch vụ → hiển thị top 3 kết quả có score, lý do gợi ý, thời gian di chuyển, thời gian chờ dự đoán
- **Map View**: Bản đồ OSM + Leaflet, hiển thị gara xung quanh theo màu trạng thái (xanh=rảnh, vàng=bận, đỏ=đầy)
- **Garage Detail**: Thông tin gara, tier badge, dịch vụ + giá, ảnh, amenities, giờ mở cửa, biểu đồ giờ đông/vắng
- **Booking Flow**: Chọn dịch vụ → chọn thời gian → xác nhận → màn hình booking detail
- **Booking Tracker**: Timeline real-time: Đang đến → Check-in → Đang rửa → Hoàn thành
- **Booking History**: Danh sách các lần rửa xe, lọc theo trạng thái
- **Feedback**: Thumbs up/down sau khi hoàn thành, comment tùy chọn
- **My Vehicles**: Quản lý danh sách xe, xe mặc định
- **Profile**: Thông tin tài khoản, cài đặt thông báo

---

## 2. Garage Owner Portal — `/garage`

Mục tiêu: Chủ gara quản lý vận hành, xem doanh thu, theo dõi booking.

### Dashboard
- **KPI Cards**: Xe hôm nay, Doanh thu hôm nay, Score hiện tại, So sánh tuần trước
- **Capacity Bar Chart**: Biểu đồ cột theo giờ trong ngày — giờ nào đông/vắng
- **Booking Queue**: Danh sách booking sắp tới, trạng thái real-time, xe đang đến

### Booking Management
- **Booking List**: Tất cả booking — lọc theo ngày, trạng thái
- **Booking Actions**: Xác nhận / Từ chối / Check-in / Bắt đầu / Hoàn thành (state machine)
- **Staff View (Mobile)**: Giao diện đơn giản cho nhân viên bay — 2 nút BẮT ĐẦU / HOÀN THÀNH

### Analytics
- **Revenue Chart**: Line chart doanh thu theo ngày/tuần/tháng
- **Customer Stats**: Tỷ lệ khách mới vs quay lại, loại xe phổ biến
- **Peak Hours Heatmap**: Chart nhiệt giờ/ngày

### Garage Settings
- **Service Management**: Thêm/sửa dịch vụ cung cấp, giá, thời gian ước tính
- **Operating Hours**: Cài đặt giờ mở cửa theo ngày
- **Staff Management**: Thêm nhân viên, phân ca

### Score & Tier
- **Score Dashboard**: Điểm hiện tại 5 nhóm (Equipment, Process, Staff, Capacity, Reliability)
- **Score History**: Line chart score theo thời gian
- **Tier Badge + Upgrade Tips**: Gợi ý cải thiện để lên tier

---

## 3. Admin Platform — `/admin`

Mục tiêu: WashMind team (bạn) quản lý toàn bộ mạng lưới gara, user, analytics.

### Network Overview
- **Live Map**: Bản đồ toàn bộ gara, màu theo tải, click vào xem detail
- **KPI Strip**: Tổng lượt hôm nay, GMV tuần, Matching accuracy, Completion rate, Gara active

### Garage Management
- **Garage List**: Bảng gara — lọc theo tier, thành phố, trạng thái, search tên
- **Garage Detail**: Profile đầy đủ, score breakdown, capacity history, booking stats
- **Onboard Pipeline**: Kanban Lead → Contacted → Assessed → Active
- **Alerts**: Gara không update >2h, score giảm đột biến, complaint rate cao

### User & Demand Analytics
- **Retention Funnel**: D1/D7/D30 retention rates
- **Demand Heatmap**: Khu vực nào nhiều search — cơ hội mở rộng
- **Unmet Demand**: Search không dẫn đến booking — lý do phân tích

### Finance
- **Commission Report**: Doanh thu commission theo gara/khu vực/thời gian
- **Payout Tracking**: Tiền cần trả cho gara
- **Subscription MRR**: Monthly Recurring Revenue từ gói thành viên

### Certification & Tier
- **Assessment Requests**: Gara xin nâng tier — duyệt/từ chối
- **Tier Adjustment**: Chỉnh tier thủ công với lý do

---

## Pages / Routes Summary

| Path | Portal | Trang |
|---|---|---|
| `/app` | Customer | Home / Search |
| `/app/map` | Customer | Map View |
| `/app/garages/:id` | Customer | Garage Detail |
| `/app/bookings` | Customer | Booking History |
| `/app/bookings/:id` | Customer | Booking Tracker |
| `/app/vehicles` | Customer | My Vehicles |
| `/app/profile` | Customer | Profile |
| `/garage` | Garage Owner | Dashboard |
| `/garage/bookings` | Garage Owner | Booking Management |
| `/garage/analytics` | Garage Owner | Analytics |
| `/garage/services` | Garage Owner | Service Management |
| `/garage/staff` | Garage Owner | Staff Management |
| `/garage/score` | Garage Owner | Score & Tier |
| `/garage/settings` | Garage Owner | Settings |
| `/admin` | Admin | Network Overview |
| `/admin/garages` | Admin | Garage Management |
| `/admin/analytics` | Admin | Demand Analytics |
| `/admin/finance` | Admin | Finance |
| `/admin/certifications` | Admin | Tier Certifications |
| `/login` | All | Auth |
