# WashMind — UI/UX Design Brief

> Tài liệu này dành cho Designer. Đọc từ đầu đến cuối trước khi vẽ bất kỳ frame nào.
> Mục tiêu: hiểu sản phẩm ở tầng sâu, không chỉ biết "cần vẽ gì" mà còn hiểu "tại sao".

---

## 1. Sản phẩm là gì?

**WashMind** là hệ thống điều phối thông minh cho dịch vụ rửa xe — không phải app đặt dịch vụ thông thường. Điểm khác biệt cốt lõi:

> *Google Maps cho bạn danh sách. WashMind ra quyết định hộ bạn.*

Hệ thống tính toán đồng thời 8 yếu tố (khoảng cách, thời gian chờ, chất lượng gara, loại xe, giá, thời tiết, lịch sử cá nhân...) và trả về **top 3 gợi ý tối ưu** — mỗi gợi ý đi kèm **lý do cụ thể bằng tiếng Việt**.

Ví dụ thực tế ra quyết định của WashMind:
- Gara A gần nhất — nhưng đang kẹt, khi bạn đến sẽ chờ 40 phút
- Gara B xa hơn 3km — nhưng đến nơi chỉ chờ 5 phút vì WashMind biết 2 xe sắp xong
- Gara C có mái che — phù hợp vì trời đang mưa

→ WashMind gợi ý **B trước, C dự phòng**, giải thích rõ ràng. Đây là trải nghiệm mà không nền tảng nào khác có.

---

## 2. Ba nhóm người dùng — Ba thế giới khác nhau

### 👤 Persona 1: Khách hàng (Customer)

**Họ là ai:** Chủ xe ô tô, 25-45 tuổi, sống ở đô thị lớn (HCM, HN, Đà Nẵng). Bận rộn. Coi thời gian là tài sản. Đã quen app như Grab, Shopee.

**Pain point họ đang chịu:**
- Đến gara rồi mới biết phải chờ 45 phút
- Không biết gara nào phù hợp với xe mình (xe Mercedes đâu thể vào tiệm rửa xe vỉa hè)
- Google Maps chỉ cho thấy gara gần, không biết gara đang đông hay vắng

**Họ muốn gì từ WashMind:**
- Mở app → thấy ngay gợi ý tốt → đặt lịch trong 30 giây → đến nơi đúng giờ, không chờ
- Không muốn phải điền form phức tạp. Chỉ cần chọn xe + dịch vụ là đủ

**Cảm xúc khi dùng app:** Cảm giác được chăm sóc. App hiểu mình. Không cần phải suy nghĩ.

---

### 🔧 Persona 2: Chủ gara (Garage Owner)

**Họ là ai:** Chủ tiệm rửa xe, 30-55 tuổi. Có thể không giỏi công nghệ. Đang quản lý bằng kinh nghiệm và sổ tay. Lo lắng khi giờ vắng không có khách.

**Pain point họ đang chịu:**
- Không biết giờ nào đông, giờ nào vắng để chuẩn bị nhân lực
- Không có số liệu — không biết mình đang làm tốt hay kém so với gara khác
- Thu tiền mặt, không tracking doanh thu bài bản

**Họ muốn gì từ WashMind:**
- Nhìn vào 1 màn hình biết ngay hôm nay bao nhiêu xe, bao nhiêu tiền
- Biết xe nào sắp đến để chuẩn bị bay rửa
- Con số cụ thể chứng minh WashMind mang giá trị — "tuần này có thêm 15 khách từ WashMind"

**Cảm xúc khi dùng app:** Tự tin. Nắm quyền kiểm soát. Thấy gara của mình đang tăng trưởng.

---

### ⚙️ Persona 3: Admin Platform (WashMind Team)

**Họ là ai:** Team vận hành WashMind — startup founder, ops manager. Cần nhìn toàn cảnh mạng lưới, phát hiện vấn đề sớm, đưa ra quyết định mở rộng.

**Họ muốn gì:**
- Nhìn bản đồ thấy ngay gara nào đang vấn đề (không update trạng thái, score giảm)
- Dashboard số liệu tổng hợp: GMV, matching accuracy, retention
- Phát hiện khu vực có demand cao nhưng thiếu gara — để ưu tiên onboard

**Cảm xúc khi dùng app:** Tổng chỉ huy. Nhìn một màn hình biết toàn bộ mạng lưới đang hoạt động thế nào.

---

## 3. Ngôn ngữ cảm xúc & Mood

WashMind không phải app rửa xe bình thường. Định vị là **Intelligence Layer** — lớp thông minh bên dưới mạng lưới 3,000 điểm. UI phải truyền đạt điều đó.

### Từ khóa cảm xúc:
`Precision` · `Fluid` · `Confident` · `Premium` · `Intelligent` · `Calm`

### Không muốn:
`Generic` · `Crowded` · `Flashy` · `Childish` · `Corporate-boring`

### Tham chiếu mood:
- **Tesla Mobile App** — dark mode, clean, data-driven, premium feel
- **Linear.app** — precision, minimalist, professional
- **Revolut** — modern finance dashboard, glassmorphism subtly
- **Grab for Business** — data-heavy but digestible

### Ghi chú đặc biệt:
- App hướng đến người Việt — cần balance giữa premium và thân thiện. Đừng quá lạnh lùng.
- Có tiếng Việt trong UI — font cần hiển thị tốt với dấu tiếng Việt
- B2C app (customer) cần warm hơn. B2B portal (garage, admin) cần professional hơn.

---

## 4. Design System — Đọc kỹ

### Màu chủ đạo
- **Primary**: `#003646` — Deep Teal. Màu nền sidebar, button CTA, header accent
- **Primary Container**: `#1e4d5e` — dùng cho gradient trên button primary
- Không dùng màu phẳng cho button primary — **bắt buộc dùng gradient** từ `#003646` → `#1e4d5e` (135deg)

### Surface system (nền)
Không dùng border 1px để phân chia section. Dùng độ chênh màu nền:
- Nền tổng: `#f7f9fb`
- Card: `#ffffff`
- Card nhấn (inner): `#f2f4f6`
- Sidebar: `#d8dadc`

### Status Colors (quan trọng cho real-time data)
| Trạng thái | Background | Text | Dùng cho |
|---|---|---|---|
| Rảnh / Tốt | `#8cf5e4` | `#00201c` | Gara rảnh, score cao, success |
| Đang bận / Cảnh báo | `#fef08a` | `#854d0e` | Gara bận vừa, cần chú ý |
| Đầy / Lỗi | `#ffdad6` | `#93000a` | Gara đầy, không nhận booking |

### Typography — Inter font
- KPI số lớn (doanh thu, số xe): `3.5rem`, weight 700, letter-spacing -0.02em
- Section header: `1.5rem`, weight 600
- Body text: `0.875rem`, weight 400
- Label/metadata: `0.75rem`, weight 500, ALL CAPS, tracking 0.05em

### Glassmorphism — dùng có chọn lọc
Chỉ dùng cho:
- Sidebar trên màn hình có bản đồ phía sau
- Bottom nav bar của Customer App
- Tooltip/popup floating trên map

Công thức: `background: rgba(247,249,251,0.85)` + `backdrop-blur: 12-20px`

### Shadow
Không dùng shadow đen thuần. Shadow tinted:
```
0px 12px 32px rgba(0, 31, 41, 0.08)
```

---

## 5. Các màn hình cần thiết kế — Chi tiết từng màn

### 5.1. CUSTOMER APP

#### Màn 1: Home / Smart Search
**Đây là màn hình quan trọng nhất. Đây là ấn tượng đầu tiên.**

Layout gợi ý:
- Header: "Xin chào, [Tên]" + xe mặc định đang chọn (badge tier xe)
- Search bar nổi bật: "Bạn muốn rửa xe ở đâu?" — tap vào mở quick filter
- Bên dưới: Top 3 gợi ý thông minh (đây là output của Matching Engine)
  - Mỗi card: tên gara + tier badge + khoảng cách + thời gian chờ + **lý do** ("Gần nhất", "Đang trống", "Có mái che")
  - Score dạng số hoặc bar — không phải sao (sao là generic)
  - Nút "Đặt ngay" — 1 tap

UX insight:
- Không hiển thị list dài. Chỉ 3. Chọn ít = chọn được.
- "Lý do" là điểm khác biệt cốt lõi, design phải làm nổi bật phần này
- Weather context badge nếu đang mưa: "🌧 Đang mưa — ưu tiên gara có mái che"

#### Màn 2: Garage Detail
- Hero: ảnh gara (carousel)
- Tier badge nổi bật + score bar 5 thành phần
- Thông tin nhanh: địa chỉ, giờ mở cửa, số bay, amenities (icon grid)
- Dịch vụ + giá (list đơn giản)
- Biểu đồ giờ đông vắng: Bar chart theo giờ trong ngày — giờ thấp màu xanh, giờ cao màu đỏ
- Button CTA: "Đặt lịch tại đây" — sticky bottom

#### Màn 3: Map View
- Full screen map (OSM/Leaflet)
- Sidebar trái glassmorphism: filter (tier, dịch vụ, khoảng cách)
- Marker trên map: màu theo trạng thái (xanh/vàng/đỏ), tap vào hiện mini-card
- Mini-card khi tap marker: tên + tier + thời gian chờ + nút xem chi tiết

#### Màn 4: Booking Tracker
**Màn hình này phải "sống" — cảm giác real-time**

Timeline dọc với 5 bước:
1. ✅ Đặt lịch
2. ✅ Gara xác nhận
3. 🔵 Đang đến → hiện ETA countdown
4. ⬜ Đang rửa
5. ⬜ Hoàn thành

Khi ở bước "Đang đến": hiển thị bản đồ nhỏ + ETA realtime
Khi hoàn thành: confetti nhẹ + prompt feedback 👍/👎

---

### 5.2. GARAGE OWNER PORTAL

#### Màn 1: Dashboard (Trang chính)
**Chủ gara mở ra phải thấy ngay: hôm nay thế nào**

Layout gợi ý (desktop-first):
- Top row: 4 KPI cards
  - 🚗 Xe hôm nay: `12 lượt` (so với hôm qua: `+3`)
  - 💰 Doanh thu: `2.160.000đ`
  - ⭐ Score: `72/100` (trend arrow)
  - 📊 WashMind fill rate: `34%` (% xe đến qua app)
- Capacity bar chart: 24h trong ngày, mỗi giờ 1 bar — màu xanh=vắng, đỏ=đông
- Booking queue (bên phải): danh sách xe sắp đến, đang rửa — cập nhật realtime

#### Màn 2: Booking Management
- Tabs: Hôm nay / Sắp tới / Lịch sử
- Mỗi booking row: thời gian | loại xe | dịch vụ | trạng thái badge | action buttons
- Action theo trạng thái: [Xác nhận] [Từ chối] / [Check-in] / [Bắt đầu] / [Hoàn thành]

#### Màn 3: Staff Mobile View
**Giao diện đặc biệt cho nhân viên tại bay rửa xe — cực kỳ đơn giản**
- Chỉ có 2 section: "Xe đang chờ" và "Đang rửa"
- Mỗi xe: loại xe + dịch vụ + giờ hẹn
- 1 button lớn: [BẮT ĐẦU RỬA] hoặc [HOÀN THÀNH]
- Font lớn, contrast cao — nhìn được dưới nắng

#### Màn 4: Analytics
- Revenue line chart: theo ngày/tuần/tháng (toggle)
- Customer donut chart: Mới vs Quay lại
- Peak hours heatmap: grid 7ngày x 24h — cell màu theo tải

#### Màn 5: Score & Tier
- Score meter lớn (gauge chart hoặc radial): `72/100`
- 5 component bars: Equipment | Process | Staff | Capacity | Reliability
- Tier badge: Standard → để lên Pro cần thêm bao nhiêu điểm
- Tips section: "Cải thiện Process score bằng cách..."

---

### 5.3. ADMIN PLATFORM

#### Màn 1: Network Overview (Command Center)
**Màn hình "tổng chỉ huy" — nhìn vào biết toàn bộ mạng lưới**

- Full-width map bên phải: tất cả gara, màu theo tải
- Left panel: KPI strip dọc
  - Gara active: `47/52`
  - Lượt hôm nay: `312`
  - GMV hôm nay: `46.8M đ`
  - Matching accuracy: `83%`
  - Alert count: `3 ⚠️`
- Alert panel: Gara không update >2h, score drop >10 điểm

#### Màn 2: Garage Management
- Table: ID | Tên gara | Quận | Tier | Score | Trạng thái | Lượt hôm nay | Action
- Filter bar: Thành phố / Tier / Trạng thái / Search
- Click vào gara: slide-over panel với full detail, score chart, booking stats

#### Màn 3: Demand Analytics
- Heatmap bản đồ: khu vực tô màu theo search density
- "Khu trắng" = nhiều search, ít gara → cơ hội onboard
- Bar chart: Top quận theo số search
- Funnel: Search → View Detail → Book → Complete

#### Màn 4: Finance
- Revenue waterfall chart: Commission + Subscription + B2B Fleet
- Payout table: gara nào cần trả tiền, bao nhiêu, kỳ nào
- MRR trend: subscription growing over time

---

## 6. Luồng UX quan trọng (Flows)

### Flow 1: Customer tìm và đặt gara (Main Flow)
```
Mở app → Home (thấy ngay top 3) → Tap vào gara → Xem detail
→ Chọn dịch vụ → Chọn giờ → Xác nhận → Booking created
→ Nhận notification khi gara confirm → Bấm "Đang đến"
→ Tracker realtime → Check-in QR → Đang rửa → Hoàn thành → Feedback
```

### Flow 2: Chủ gara xử lý booking
```
Nhận push notification "Có booking mới" → Mở app
→ Xem booking detail (xe gì, dịch vụ gì, giờ nào)
→ Tap [Xác nhận] → User nhận thông báo
→ Khi xe đến: staff tap [Check-in] → [Bắt đầu] → [Hoàn thành]
→ Data tự động vào analytics và scoring
```

### Flow 3: Admin phát hiện vấn đề
```
Mở admin → Network map → Thấy gara màu đỏ (alert)
→ Click vào → Score đang giảm, processing time tăng
→ Gửi notification cho chủ gara qua portal
→ Track improvement qua score chart tuần sau
```

---

## 7. Responsive Strategy

| Portal | Primary Device | Secondary |
|---|---|---|
| Customer App | Mobile (360-430px) | Tablet |
| Garage Dashboard | Desktop (1280px+) | Tablet |
| Garage Staff View | Mobile (360px) | — |
| Admin Platform | Desktop (1440px+) | — |

Customer app **thiết kế mobile-first**. Garage portal và Admin thiết kế desktop trước.

---

## 8. Tài liệu kèm theo cho Designer

| Tài liệu | Nội dung |
|---|---|
| `design.md` | Design system: màu sắc, typography, component rules, do/don't |
| `features.md` | Danh sách đầy đủ tính năng và routes của 3 portal |
| `WashMind_Project_Document_v1.md` | Tổng quan sản phẩm, vấn đề giải quyết, user stories |
| `WashMind_Business_Perspective.md` | KPIs cần thể hiện trên dashboard (D7/D30 retention, GMV, LTV...) |

---

## 9. Checklist cho Designer

Trước khi deliver frame:
- [ ] Mỗi role có layout riêng, không share layout giữa customer và garage
- [ ] Status badge dùng đúng màu hệ thống (Signal System)
- [ ] Button primary dùng gradient, không phải màu phẳng
- [ ] Không dùng border 1px để phân section — dùng tonal shift
- [ ] KPI numbers đủ lớn và nổi bật — đây là thứ user nhìn đầu tiên
- [ ] "Lý do gợi ý" trên Search result phải được design nổi bật
- [ ] Responsive: Customer app xem trên mobile trước
- [ ] Tiếng Việt hiển thị đẹp với Inter font
