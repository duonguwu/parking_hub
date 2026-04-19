# WashMind — Đề Xuất Kinh Doanh

> **Tasco Foundry: Wash3000**
> Đội WashMind · Tháng 04/2026

---

## Tóm Tắt

WashMind là **Lớp Thông Minh (Intelligence Layer)** cho mạng lưới rửa xe toàn quốc của Tasco, là một nền tảng điều phối và ghép nối theo thời gian thực, kết nối chủ xe với đúng gara, đúng thời điểm, đúng tiêu chuẩn chất lượng.

Việt Nam có gần 7 triệu ô tô đăng ký, tăng trưởng 15-20%/năm. Thị trường rửa xe lớn nhưng cực kỳ phân mảnh, hàng chục ngàn tiệm độc lập, không có chuẩn chất lượng, không có hạ tầng số, và người tiêu dùng không có cách nào ra quyết định đúng. Tầm nhìn xây dựng mạng lưới 3.000 điểm của Tasco cần một bộ não — và WashMind chính là bộ não đó.

**WashMind khác biệt ở điểm nào:**

- **Ghép nối thông minh (Smart Matching)**: Chúng tôi không liệt kê gara. Chúng tôi tính toán gara tối ưu dựa trên tải vận hành real-time, thời gian di chuyển, loại xe, và dự đoán tình trạng gara *tại thời điểm user đến nơi*, không phải thời điểm tìm kiếm.
- **Phân cấp gara (Garage Tiering)**: Phân loại gara theo năng lực vận hành thực tế (Basic → Standard → Pro → Elite), đảm bảo xe sang vào đúng gara đủ tiêu chuẩn, xe phổ thông không phải trả giá premium.
- **Niềm tin bằng dữ liệu (Data-Driven Trust)**: Thay vì đánh giá 5 sao dễ bị thao túng, chúng tôi chấm điểm gara bằng dữ liệu vận hành: thời gian xử lý thực tế, tỷ lệ khách quay lại, mức độ ổn định theo thời gian.

---

## 1. Chiến Lược Ra Thị Trường (Go-to-Market)

### Bài toán: Con gà và Quả trứng

WashMind là marketplace hai chiều. Không có gara → user mở app thấy trống → bỏ đi. Không có user → gara không thấy giá trị → bỏ đi. Chúng tôi giải quyết bằng chiến lược **Cung Trước (Supply First)**.

### Giai đoạn 1 — Xây dựng nguồn cung (Tuần 1-6)

**Mục tiêu:** 5-10 gara tại 1 quận duy nhất (Quận 1 hoặc Quận 3, TP.HCM)

| Hành động | Chi tiết |
|---|---|
| **Chọn gara có sẵn khách** | Chọn gara đã kinh doanh ổn định. Họ không *cần* mình — nghĩa là họ sẽ không thất vọng. |
| **Miễn phí hoàn toàn** | "Chúng tôi mang thêm khách VETC cho anh. Anh không trả gì. Thử 3 tháng." Không gara nào từ chối khách miễn phí. |
| **Nhắm vào giờ vắng** | Tập trung fill dead hours (13h-15h các ngày trong tuần). Gara có thêm doanh thu, không mất gì. |
| **Onboard trực tiếp** | Team đến tận gara, chụp ảnh, đánh giá tier, thiết lập profile. Sự tiếp xúc trực tiếp tạo niềm tin. |

**Tại sao 1 quận, không phải cả thành phố?**
- 10 gara ở 1 quận = mật độ cao = user luôn thấy gara gần = trải nghiệm tốt
- 10 gara rải khắp thành phố = mật độ thấp = user thấy gara xa = trải nghiệm kém = bỏ đi

Grab ban đầu chỉ chạy ở 1 khu vực nhỏ tại Malaysia. Chiếm lĩnh nhỏ, rồi mở rộng.

### Giai đoạn 2 — Kích hoạt cầu (Tuần 5-8)

**Mục tiêu:** 100+ lượt đặt lịch qua nền tảng

| Kênh | Chiến lược | Chi phí |
|---|---|---|
| **Push notification VETC** | "Giảm 50% lần rửa xe đầu tiên qua WashMind" — gửi trực tiếp cho 4M+ user VETC trong khu vực pilot | Gần như 0 đồng (hạ tầng Tasco) |
| **Mã QR tại gara** | QR tại gara đã onboard: "Đặt lịch lần sau — không phải chờ" | ~$50 tổng cộng |
| **Chương trình giới thiệu** | User được 1 lần rửa miễn phí khi giới thiệu 3 người | $5-10/user mới |
| **Nhân viên gara giới thiệu** | Nhân viên nói với khách walk-in: "Lần sau đặt qua WashMind nhé, khỏi chờ" | $0 |

**Insight then chốt:** Với tích hợp VETC, chi phí thu hút khách hàng (CAC) tiến về 0. User VETC đã sở hữu ô tô, đã quen thanh toán số, và có thể tiếp cận qua push notification miễn phí. Đây là lợi thế không công bằng (unfair advantage) của chúng tôi.

### Giai đoạn 3 — Chứng minh & Mở rộng (Tuần 7-12)

**Mục tiêu:** Có traction đo lường được để trình bày tại Demo Day

| Chỉ số | Mục tiêu | Cách đạt |
|---|---|---|
| Gara hoạt động | 5+ | Tiếp cận trực tiếp |
| Lượt dịch vụ | 30+ | Kích hoạt user VETC |
| Tỷ lệ kích hoạt khách hàng | >20% | Khuyến mãi + matching chất lượng |
| Phản hồi thu thập | >80% | Feedback 1 chạm (👍/👎) sau dịch vụ |

Các chỉ số này khớp trực tiếp với tiêu chí thành công mà Tasco đã công bố cho Top 3.

---

## 2. Kế Hoạch Mở Rộng: Lộ Trình Đến 3.000 Điểm

Chúng tôi không giả vờ scale lên 3.000 là dễ. Nhưng chúng tôi có chiến lược cụ thể theo từng giai đoạn, hiệu quả tăng dần.

### Mô hình 4 giai đoạn

```
Giai đoạn 1: CHỨNG MINH (Tháng 1-3)        →      5 → 50 gara
Giai đoạn 2: TẠO KHUÔN MẪU (Tháng 4-6)     →     50 → 200 gara
Giai đoạn 3: NHÂN BẢN (Tháng 7-9)           →    200 → 800 gara
Giai đoạn 4: HIỆU ỨNG MẠNG LƯỚI (Tháng 10-12) → 800 → 3.000 gara
```

### Giai đoạn 1 — CHỨNG MINH (Tháng 1-3): 5 → 50 Gara

**Chiến lược:** Onboard trực tiếp, cầm tay chỉ việc tại TP.HCM

- Field team (2-3 người) đến gara trực tiếp
- Mô hình 0% commission: "Miễn phí 3 tháng"
- Năng suất: ~5 gara/tuần với field team 2 người
- **Mục tiêu: 50 gara tại 5 quận TP.HCM**

**Chúng tôi đang chứng minh:**
- Gara thấy giá trị (thêm khách hàng)
- User thích WashMind hơn Google Maps
- Unit economics hoạt động (ngay cả khi 0% commission, chi phí vận hành cực thấp)

**Sản phẩm:** Một **Playbook Onboard Gara** — quy trình từng bước, kịch bản tiếp cận, checklist đánh giá, hướng dẫn setup. Playbook này là cách chúng tôi scale vượt xa khả năng vật lý của team.

### Giai đoạn 2 — TẠO KHUÔN MẪU (Tháng 4-6): 50 → 200 Gara

**Chiến lược:** Nhân bản playbook + tuyển field staff + mở rộng thành phố

| Hành động | Chi tiết |
|---|---|
| **Tuyển 4-6 field staff** | Training bằng playbook từ Giai đoạn 1. Mỗi người onboard 5-8 gara/tuần. |
| **Mở rộng ra Hà Nội & Đà Nẵng** | 2 field staff mỗi thành phố, bắt đầu từ quận trung tâm. |
| **Cổng tự đăng ký (Self-Onboard Portal)** | Web portal để gara tự đăng ký. WashMind xác minh từ xa (upload ảnh, video call đánh giá). |
| **Áp dụng commission dần** | Đưa vào commission 5-8% sau khi hết giai đoạn miễn phí. Gara đã thấy ROI sẽ chấp nhận. |

**Tính toán:** 6 field staff × 5 gara/tuần × 12 tuần = 360 tiềm năng. Mục tiêu 200 (bảo thủ, tính cả từ chối và churn).

### Giai đoạn 3 — NHÂN BẢN (Tháng 7-9): 200 → 800 Gara

**Chiến lược:** Tự đăng ký + chuỗi gara + mạng lưới Tasco

| Kênh | Số gara dự kiến |
|---|---|
| **Cổng tự đăng ký** | Gara nghe về WashMind từ gara khác. Truyền miệng. Mục tiêu: 150 đăng ký organic. |
| **Hợp tác chuỗi gara** | Partner với chuỗi rửa xe hiện có (20-50 điểm). 1 deal = nhiều gara. Mục tiêu: 3-5 chuỗi = 100-200 gara. |
| **Mạng lưới operator Tasco** | Tasco có "quyền tiếp cận trực tiếp chủ gara, field team sẵn sàng." Kích hoạt mạng lưới này. Mục tiêu: 100-200 gara. |
| **Mở rộng field team** | 10-12 field staff tại 5 thành phố. Mục tiêu: 150+ gara. |

**Yếu tố then chốt:** Đến giai đoạn này, chúng tôi có **bằng chứng** — dashboard hiển thị doanh thu tăng của gara, dữ liệu khách hàng, tỷ lệ quay lại. Bằng chứng này khiến mỗi lần pitch tiếp theo dễ hơn. Gara đến với mình, không phải mình đi xin.

### Giai đoạn 4 — HIỆU ỨNG MẠNG LƯỚI (Tháng 10-12): 800 → 3.000 Gara

**Chiến lược:** Sức hút nền tảng + mở rộng địa lý mạnh mẽ

Ở quy mô này, hiệu ứng mạng lưới bắt đầu hoạt động:

- **User đòi hỏi phủ sóng** → Gara ở khu vực chưa có thấy đối thủ hưởng lợi → Tự đăng ký
- **Thương hiệu Tasco** → "WashMind Certified" trở thành badge chất lượng → Gara muốn có
- **Hợp đồng B2B đội xe** → Công ty logistics (GHN, J&T, tài xế Grab) cần phủ sóng toàn quốc → Tạo áp lực cho gara ở khu vực chưa phủ
- **Mô hình "điểm kết nối"** — Không phải gara nào cũng cần tích hợp real-time đầy đủ ngay ngày 1. Gara có thể được "kết nối" (listed, xác minh, nhận booking qua điện thoại/app) trước khi nâng cấp lên tích hợp số hoàn toàn.

```
Chi tiết 3.000 "điểm kết nối":
├── Tích hợp đầy đủ (real-time capacity, booking số):     ~800
├── Tích hợp một phần (profile + booking thủ công):        ~1.200  
└── Listed & xác minh (tìm thấy được, booking qua ĐT):    ~1.000
```

**Điều này khả thi** vì "kết nối" ≠ "tự động hóa hoàn toàn." Chúng tôi xây mạng lưới trước, đào sâu tích hợp dần theo thời gian.

### Tại sao gara đồng ý tham gia

| Lo ngại | Câu trả lời |
|---|---|
| "Tui cần thêm app nữa làm gì?" | Chúng tôi mang đến khách anh chưa có hôm nay. Anh không trả gì 3 tháng đầu. |
| "Tui bận đủ rồi" | Chúng tôi fill giờ vắng (13h-15h các ngày thường). Đó là doanh thu anh đang bỏ lỡ. |
| "Tui không tin mấy công ty công nghệ" | Đây là dữ liệu — gara X quận bên cạnh nhận thêm 15 khách tuần vừa rồi qua chúng tôi. Anh gọi cho chủ hỏi. |
| "Lỡ tui muốn nghỉ?" | Anh nghỉ lúc nào cũng được. Không hợp đồng, không ràng buộc. (Nhưng anh sẽ không muốn, vì khách anh giờ đặt qua chúng tôi.) |

---

## 3. Tính Năng Cốt Lõi Của Sản Phẩm

### 3.1. Smart Matching Engine — Trái tim hệ thống

**Vấn đề:** Google Maps trả về danh sách gara gần nhất, user tự chọn. Đến nơi mới biết phải chờ 45 phút hoặc gara không rửa được xe mình.

**Giải pháp:** WashMind không trả danh sách — WashMind **ra quyết định hộ user** bằng cách tính toán đồng thời 8 yếu tố:

| Yếu tố | Ý nghĩa | Tại sao quan trọng |
|---|---|---|
| **Khoảng cách & ETA** | Thời gian di chuyển thực tế (tính cả kẹt xe) | User muốn gần |
| **Thời gian chờ dự đoán** | Đánh giá tải gara **khi user đến nơi** | Khác biệt cốt lõi vs Google Maps |
| **Chất lượng gara** | Score dựa trên dữ liệu vận hành | Đảm bảo chất lượng |
| **Phù hợp loại xe** | Tier gara khớp với loại xe (xe sang cần tier 3+) | Bảo vệ trải nghiệm |
| **Lịch sử cá nhân** | Gara quen, gara hay quay lại | Cá nhân hóa |
| **Giá dịch vụ** | So sánh với trung bình khu vực | Phù hợp túi tiền |
| **Độ tin cậy** | Tỷ lệ đúng giờ, tỷ lệ khiếu nại | Giảm rủi ro |
| **Thời tiết** | Ưu tiên gara có mái che khi mưa | Context-aware |

**Pipeline 5 bước (< 200ms):**

```
Bước 1: Lọc cứng        → 3.000 gara → ~20 candidates (geo + tier + dịch vụ)
Bước 2: Làm giàu dữ liệu → ETA matrix (OSRM), thời tiết, capacity dự đoán
Bước 3: Chấm điểm       → 8 scoring functions, trọng số động theo context
Bước 4: Cá nhân hóa      → Điều chỉnh theo lịch sử user
Bước 5: Xếp hạng đa dạng → Top 3 kèm giải thích "Tại sao gara này"
```

**Ví dụ kết quả:**

> 🏆 **AutoSpa Pro Q3** — 89 điểm
> - ✅ Chỉ 12 phút di chuyển — gần nhất
> - ✅ Chờ 5 phút khi đến nơi
> - ✅ Có mái che — phù hợp trời đang mưa
> - ⚠️ Giá cao hơn trung bình khu vực 15%

### 3.2. Hệ Thống Phân Cấp Gara (Garage Tiering)

4 cấp dựa trên năng lực vận hành **thực tế**, không phải tự khai báo:

| Tier | Tên | Phù hợp cho | Ví dụ |
|---|---|---|---|
| **Tier 1** | Basic | Xe phổ thông, xe máy | Tiệm rửa xe ven đường |
| **Tier 2** | Standard | Xe gia đình, sedan | Gara 2-3 bay, có khu chờ |
| **Tier 3** | Pro | Xe cao cấp, SUV sang | Trung tâm chăm sóc chuyên nghiệp |
| **Tier 4** | Elite | Xe sang, siêu xe | Studio detailing chuyên biệt |

**Điểm gara được tính từ 5 nhóm yếu tố:**
- Thiết bị & hóa chất (Equipment)
- Quy trình & SOP (Process)
- Nhân sự & đào tạo (Staff)
- Công suất & diện tích (Capacity)
- Độ tin cậy — tỷ lệ khách quay lại, complaint rate (Reliability)

**Mapping tự động:** Xe sang → chỉ gợi ý Tier 3-4. Xe phổ thông → Tier 1-3. Matching Engine tự lọc tier trước khi tính score.

### 3.3. Hệ Thống Đặt Lịch (Booking Engine)

**State machine đầy đủ:**

```
Tạo đặt lịch → [Chờ xác nhận] → Gara xác nhận → [Đã xác nhận]
    → User bấm "Đang đến" → [Đang di chuyển] → Check-in (QR/GPS)
    → [Đã đến] → Nhân viên bắt đầu → [Đang rửa] → Hoàn thành ✓
    
Hủy có thể xảy ra ở bất kỳ bước nào, với chính sách phí khác nhau:
- Hủy < 5 phút:    Miễn phí
- Hủy sau xác nhận: 10% phí dịch vụ
- Đang đi mà hủy:  20% phí
- Không đến (no-show): 50% phí
```

**Chống double-booking:** Redis distributed lock trên mỗi slot `(garage_id + thời gian)` — đảm bảo chỉ 1 user book thành công dù 50 người bấm cùng lúc.

**Theo dõi ETA live:** Khi user bấm "Đang đến", hệ thống cập nhật ETA mỗi 2 phút và thông báo cho gara nếu user đến trễ quá 10 phút.

### 3.4. Theo Dõi Công Suất Real-time (Capacity Monitoring)

- Nhân viên gara update qua app/tablet: nhận xe → bắt đầu rửa → hoàn thành
- Hệ thống snapshot tải mỗi 5 phút → lưu vào time-series
- **Capacity Predictor** — dự đoán tình trạng gara tại thời điểm tương lai:

```
Dự đoán = 
    50% × Pipeline (bookings đã xác nhận sắp đến)
  + 30% × Historical baseline (trung bình cùng giờ/ngày 4 tuần qua)
  + 20% × Current state decay (trạng thái hiện tại)

Nếu dự đoán < 15 phút trước → dựa mạnh vào pipeline
Nếu dự đoán > 60 phút trước → dựa mạnh vào historical
```

### 3.5. Calibration & Data Moat

Hệ thống tự cải thiện theo thời gian nhờ dữ liệu vận hành thực:

- **ETA Calibration**: Gara nói "25 phút/xe" nhưng thực tế 35 phút → hệ thống tự điều chỉnh hàng tuần
- **Search Logs**: Mỗi lần user search → log đầy đủ context (vị trí, xe, thời gian, thời tiết, kết quả, quyết định user)
- **Implicit Feedback**: User chọn gara rank 2 thay vì rank 1 → tín hiệu cần cải thiện ranking
- **Weekly Training**: Sau 1.000+ bookings, sử dụng LambdaMART (LightGBM) để tự học trọng số tối ưu từ hành vi thực

---

## 4. Dashboard & Công Cụ Quản Lý

### 4.1. Dashboard Quản Trị Platform (WashMind Admin)

Dành cho team WashMind vận hành toàn bộ mạng lưới:

#### Tổng quan mạng lưới (Network Overview)

| Chỉ số | Hiển thị | Mục đích |
|---|---|---|
| **Bản đồ live** | Tất cả gara trên bản đồ, màu theo tải (xanh/vàng/đỏ) | Giám sát real-time toàn mạng |
| **Tổng lượt dịch vụ hôm nay** | Số lượt + so sánh cùng ngày tuần trước | Tracking tăng trưởng |
| **GMV (Gross Merchandise Value)** | Tổng doanh thu chảy qua platform hôm nay/tuần/tháng | KPI kinh doanh |
| **Tỷ lệ hoàn thành** | % booking → completed (mục tiêu >90%) | Chất lượng hệ thống |
| **Matching accuracy** | % user hài lòng top-1 (thumbs up) | Chất lượng engine |
| **Gara mới onboard tuần này** | Số gara + trend | Tracking scale |

#### Quản lý gara (Garage Management)

| Chức năng | Chi tiết |
|---|---|
| **Danh sách gara** | Lọc theo thành phố, quận, tier, trạng thái. Search theo tên/địa chỉ. |
| **Profile gara** | Thông tin, ảnh, dịch vụ, giá, operating hours, tier assessment chi tiết |
| **Score & Tier tracking** | Biểu đồ score theo thời gian, so sánh với trung bình thành phố |
| **Capacity heatmap** | Biểu đồ nhiệt: giờ nào đông/vắng, ngày nào bận nhất — theo từng gara hoặc khu vực |
| **Cảnh báo** | Auto-alert: gara không update tải >2h, processing time tăng đột biến, complaint rate cao |
| **Onboard pipeline** | Kanban: Lead → Contacted → Visited → Assessment → Active. Tracking conversion |

#### Phân tích người dùng (User Analytics)

| Chức năng | Chi tiết |
|---|---|
| **Retention funnel** | D1 / D7 / D30 retention rates, cohort analysis |
| **Search → Book conversion** | % search dẫn đến booking, breakdown theo khu vực/giờ |
| **Demand heatmap** | Khu vực nào có nhiều search nhưng ít gara → cơ hội mở rộng |
| **Unmet demand** | Search mà không book — tại sao? Giá cao? Xa? Chất lượng? |
| **Top users** | Users có LTV cao nhất, frequency cao nhất |

#### Tài chính (Finance)

| Chức năng | Chi tiết |
|---|---|
| **Commission tracking** | Doanh thu commission theo gara/khu vực/tháng |
| **Payout report** | Số tiền cần trả cho từng gara |
| **Unit economics** | CAC, LTV, LTV/CAC real-time theo cohort |
| **Subscription revenue** | MRR (Monthly Recurring Revenue) từ gói thành viên |

### 4.2. Dashboard Chủ Gara (Garage Owner Portal)

Dành cho chủ gara quản lý kinh doanh thông qua WashMind. Đây là công cụ giúp gara "dính" với platform.

#### Tổng quan kinh doanh (Business Overview)

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 AUTOSPA QUẬN 3 — Dashboard                     Hôm nay: T5    │
├────────────────┬────────────────┬──────────────┬───────────────────┤
│ 🚗 Xe hôm nay  │ 💰 Doanh thu   │ ⭐ Score      │ 📈 So với tuần   │
│    12 lượt     │   2.160.000đ   │   72/100     │   trước: +18%    │
├────────────────┴────────────────┴──────────────┴───────────────────┤
│                                                                     │
│  📋 Booking tiếp theo:                                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 14:30  |  Mercedes S-Class  |  Rửa Premium  |  Đang đến     │  │
│  │ 15:00  |  Toyota Camry      |  Rửa Basic    |  Đã xác nhận  │  │
│  │ 15:45  |  BMW X5            |  Detailing     |  Chờ xác nhận │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  📊 Biểu đồ công suất hôm nay:                                     │
│  7h ████░░░░░░ 40%                                                  │
│  8h ██████████ 100% ← cao điểm                                     │
│  9h ████████░░ 80%                                                  │
│ 10h ██████░░░░ 60%                                                  │
│ 11h ████░░░░░░ 40%                                                  │
│ 12h ██░░░░░░░░ 20%                                                  │
│ 13h █░░░░░░░░░ 10% ← giờ vắng (WashMind fill)                     │
│ 14h ████░░░░░░ 40% ← đang tăng (có 3 booking)                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Các chức năng chi tiết

| Module | Chức năng | Giá trị cho gara |
|---|---|---|
| **Quản lý booking** | Xem/xác nhận/từ chối booking, check-in, hoàn thành dịch vụ | Luồng vận hành số hóa |
| **Quản lý dịch vụ** | Thêm/sửa dịch vụ cung cấp, thiết lập giá, thời gian ước tính | Tự chủ kinh doanh |
| **Quản lý nhân viên** | Thêm tài khoản staff, phân ca, theo dõi hiệu suất từng nhân viên | Quản lý nhân sự |
| **Báo cáo doanh thu** | Doanh thu theo ngày/tuần/tháng, so sánh với giai đoạn trước | Thấy rõ giá trị WashMind mang lại |
| **Thống kê khách hàng** | Khách mới vs khách quay lại, loại xe phổ biến, giờ đông nhất | Insight kinh doanh |
| **Score & Tier** | Xem điểm hiện tại, lịch sử, gợi ý cải thiện để lên tier | Động lực nâng chất lượng |
| **Insights** | "Giờ vắng nhất: T3 13h-15h", "SUV chiếm 40% khách", "Khách quay lại: 65%" | Data mà trước đây gara không bao giờ có |
| **Thông báo** | Booking mới, khách đang đến, khách trễ, cảnh báo score giảm | Realtime |

#### Giao diện nhân viên gara (Garage Staff App — Mobile)

Giao diện đơn giản cho nhân viên tại bay rửa xe:

```
┌──────────────────────────┐
│  🚗 XE ĐANG CHỜ (2)      │
│                          │
│  ▶ Mercedes S-Class      │
│    Rửa Premium | 14:30   │
│    [BẮT ĐẦU RỬA]        │
│                          │
│  ▶ Toyota Camry          │
│    Rửa Basic | 15:00     │
│    Đến lúc: 14:55        │
│                          │
│  ───────────────────     │
│  🔧 ĐANG RỬA (1)        │
│                          │
│  ▶ Honda CRV             │
│    Rửa Premium | 14:00   │
│    Bắt đầu: 14:05        │
│    [HOÀN THÀNH] ← 1 nút │
│                          │
└──────────────────────────┘
```

- 2 nút chính: **BẮT ĐẦU** và **HOÀN THÀNH** — cực kỳ đơn giản
- Mỗi lần bấm = 1 data point cho Data Moat (thời gian xử lý thực tế)
- Scan QR check-in khi khách đến

### 4.3. Giao Diện Người Dùng (User App)

| Tính năng | Mô tả |
|---|---|
| **Tìm gara thông minh** | Nhập vị trí/loại xe/dịch vụ → Top 3 gara tối ưu với giải thích, trên bản đồ |
| **Chat tự nhiên** | "7 giờ tối nay tìm gara rửa xe gần Q1" → hệ thống hiểu và gợi ý |
| **Đặt lịch 1 chạm** | Chọn gara → xác nhận → nhận hướng dẫn đường đi |
| **Theo dõi trạng thái** | Timeline: đang đi → đã đến → đang rửa → hoàn thành |
| **Feedback nhanh** | 👍/👎 + bình luận tùy chọn sau dịch vụ |
| **Lịch sử** | Tất cả lần rửa xe, gara quen, chi tiêu |
| **Gợi ý chủ động** | Push notification: "Sáng mai rảnh, gara quen của bạn đang vắng — đặt lịch?" |
| **Quản lý xe** | Thêm nhiều xe, mỗi xe tự động mapping tier |

---

## 5. Tận Dụng Tài Nguyên Hiện Có

### Tasco cung cấp gì (sau khi vào Top 3)

| Tài nguyên Tasco | WashMind tận dụng | Giá trị |
|---|---|---|
| **VETC — 4M+ users** | Kênh demand trực tiếp. Push notification tới chủ xe khu vực pilot. Nhận diện xe tự động. | CAC gần 0. Onboard không ma sát. |
| **GoongIO Maps API** | Routing & ETA chính xác — input cốt lõi cho Matching Engine. Dự đoán tình trạng gara khi đến cần ETA chính xác. | Matching chính xác vượt trội so với đối thủ dùng map chung. |
| **Tasco Payment APIs** | Thanh toán qua ví VETC. Billing subscription. Chia doanh thu cho gara. | Ma sát thanh toán = 0 → conversion cao. |
| **Operator Network** | Tiếp cận trực tiếp chủ gara + field team sẵn sàng để onboard quy mô lớn. | Tăng tốc mở rộng Giai đoạn 3-4. |
| **AI Infrastructure** | Computer vision (tương lai: đánh giá xe tự động, xác minh chất lượng). | Tăng tốc roadmap. |

### Chúng tôi đã build gì mà không cần chờ

**Chúng tôi không ngồi chờ tài nguyên Tasco để bắt đầu.** Stack hiện tại:

| Thành phần | Trạng thái | Tích hợp Tasco |
|---|---|---|
| **Backend** | FastAPI + MongoDB, deployed, tested | Sẵn sàng — adapter pattern |
| **Maps & Routing** | OpenStreetMap (OSRM self-hosted) | Swap sang GoongIO = 1-2 ngày |
| **Multi-Tenant** | Đã build và test — support unlimited gara | Mỗi gara = 1 tenant, platform query cross-tenant |
| **Matching Engine** | Core algorithm implemented, 8 scoring functions | GoongIO ETA cắm thẳng vào formula có sẵn |
| **Auth & RBAC** | JWT + 7 vai trò (super_admin → customer) | VETC SSO = thêm 1 auth provider |
| **Garage Tiering** | Hệ thống 4 tier với scoring algorithm | Sẵn sàng nhận data gara thực |
| **Data Collection** | Service logs, search logs, capacity snapshots thiết kế xong | Thu thập từ Ngày 1 pilot |
| **Booking Engine** | State machine + distributed lock | Production-ready |

**Thông điệp then chốt:** Kiến trúc được build với **adapter pattern** — chuyển từ OpenStreetMap sang GoongIO, hay từ auth thủ công sang VETC SSO, chỉ là thay cấu hình, không cần rebuild. Chúng tôi đã chứng minh có thể thực thi độc lập, và sẽ đi nhanh hơn nữa với hạ tầng Tasco.

---

## 6. Giá Trị Đầu Tư: Tại Sao $500.000 Cho WashMind

### Unit Economics — Mỗi giao dịch tạo giá trị

```
1 lượt rửa xe qua WashMind:
├── Khách trả:                         150.000 VNĐ
├── Gara nhận (sau commission 12%):    132.000 VNĐ
├── WashMind/Tasco giữ:                 18.000 VNĐ
│   ├── Chi phí hạ tầng:               ~1.000 VNĐ
│   └── Lợi nhuận gộp:                 17.000 VNĐ mỗi lượt
└── Biên lợi nhuận:                    ~11,3%
```

### Thu Hút Khách Hàng — Gần Bằng 0

```
CAC  = ~30.000 VNĐ (push notification cho VETC users có sẵn, gần miễn phí)
LTV  = 18.000 × 3 lần/tháng × 24 tháng = 1.296.000 VNĐ
LTV/CAC = 43x  ← Xuất sắc cho bất kỳ marketplace nào
Hoàn vốn: < 2 lần rửa (< 1 tháng)
```

### 8 Nguồn Doanh Thu — Không Chỉ Commission

| # | Nguồn doanh thu | Năm 1 (500 gara) | Năm 2 (3.000 gara) |
|---|---|---|---|
| 1 | **Hoa hồng giao dịch** (10-12%) | ~5 tỷ VNĐ | ~30 tỷ VNĐ |
| 2 | **Gói subscription** (gói tháng cho user) | ~3 tỷ VNĐ | ~18 tỷ VNĐ |
| 3 | **Quản lý đội xe B2B** (hợp đồng doanh nghiệp) | ~4 tỷ VNĐ | ~24 tỷ VNĐ |
| 4 | **Phí chứng nhận gara** (đánh giá tier, badge) | ~0,5 tỷ VNĐ | ~3 tỷ VNĐ |
| 5 | **Hiển thị ưu tiên** (premium listing cho gara) | ~0,3 tỷ VNĐ | ~2 tỷ VNĐ |
| 6 | **Mua sỉ vật tư** (margin từ procurement) | ~1 tỷ VNĐ | ~5 tỷ VNĐ |
| 7 | **Phân tích dữ liệu** (insight ẩn danh, tổng hợp) | — | ~2 tỷ VNĐ |
| 8 | **Loyalty VETC** (cross-pollination với hệ sinh thái) | — | Chia sẻ doanh thu |
| | **Tổng** | **~13,8 tỷ VNĐ (~$550K)** | **~84 tỷ VNĐ (~$3,4M)** |

### Lợi Nhuận Đầu Tư

```
Đầu tư:           $500.000 USD (~12,5 tỷ VNĐ)
Doanh thu Năm 1:   ~13,8 tỷ VNĐ (~$550K)  → ROI: ~108%
Doanh thu Năm 2:   ~84 tỷ VNĐ (~$3,4M)    → ROI tích lũy: ~680%

Thời gian hoàn vốn: ~12 tháng
```

### Phân Bổ Ngân Sách

| Hạng mục | Số tiền | % | Mục đích |
|---|---|---|---|
| **Team & Tuyển dụng** | $300.000 | 60% | Business lead, ops manager, 4-6 field staff, 1-2 kỹ sư bổ sung |
| **Marketing & Acquisition** | $80.000 | 16% | Khuyến mãi user, incentive onboard gara, brand materials |
| **Vận hành** | $60.000 | 12% | Trợ giá pilot (miễn phí cho gara), chương trình fleet pilot |
| **Hạ tầng** | $30.000 | 6% | Cloud hosting, API costs, monitoring, security |
| **Dự phòng** | $30.000 | 6% | Contingency |
| **Tổng** | **$500.000** | **100%** | |

### Lợi Thế Cạnh Tranh — Tại Sao WashMind Thắng

Các đội khác trong Wash3000 rất có thể sẽ build "tech cho gara" — dashboard SaaS, cảm biến IoT, camera tại từng tiệm. Các giải pháp này giải quyết bài toán của chủ gara. **Nhưng Tasco không cần cải tiến 1 gara — Tasco cần xây MẠNG LƯỚI 3.000 điểm.**

WashMind vận hành ở **tầng mạng lưới**:

| Yếu tố | Tiếp cận "Tech tại Gara" | WashMind |
|---|---|---|
| **Phạm vi** | 1 gara mỗi lần | Toàn mạng lưới đồng thời |
| **Phụ thuộc** | Gara có thể ngừng dùng bất cứ lúc nào | Gara phụ thuộc WashMind về khách hàng |
| **Doanh thu** | Phí SaaS nhỏ mỗi gara | 8 nguồn doanh thu quy mô mạng lưới |
| **Giá trị dữ liệu** | Dữ liệu từ 1 gara (hẹp) | Trí tuệ cross-network (sâu) |
| **Lock-in** | Không — gara chuyển tự do | Lock-in hai chiều (gara + user) |
| **Synergy VETC** | Tối thiểu | Tích hợp sâu (identity, payment, loyalty) |
| **Giá trị cho Tasco** | Cải thiện 1 tiệm | Xây đế chế dịch vụ ô tô |

### Hào Nước Dữ Liệu (Data Moat)

Sau 3-6 tháng vận hành thực, WashMind tích lũy **5 lớp dữ liệu độc quyền** mà không đối thủ nào có thể sao chép:

1. **Sự thật hành vi** — thời gian xử lý thực vs quảng cáo (cần hàng ngàn giao dịch thực)
2. **Trí tuệ di chuyển** — ETA hiệu chỉnh vượt trội map chung (cần user đi thực tế)
3. **Cá nhân hóa** — biết user muốn gì trước khi họ nói (cần nhiều tháng lịch sử)
4. **DNA vận hành gara** — pattern hiệu suất theo giờ, ngày, thời tiết (cần giám sát liên tục)
5. **Trí tuệ mạng lưới** — pattern thay thế, hiệu ứng domino (cần multi-gara + multi-user data)

> **Code copy được trong vài tuần. Dữ liệu cần nhiều tháng xây dựng và không bao giờ sao chép được.**

---

## 7. Đội Ngũ

| Thành viên | Vai trò | Đóng góp |
|---|---|---|
| **Nguyễn Dương** | AI Engineer · Co-Founder | Chiến lược sản phẩm, Matching Engine, Intelligence Layer, kiến trúc dữ liệu |
| **Đào Trung Tín** | Software Engineer · Co-Founder | Full-stack development, hạ tầng backend, deployment |
| **Dương Hiển Kiệt** | UI/UX Designer · Co-Founder | Thiết kế sản phẩm, brand identity, trải nghiệm người dùng |

### Chúng tôi mang đến gì

- **Prototype đang chạy** — không phải slides. Backend deployed, multi-tenant architecture tested, core APIs hoạt động.
- **Năng lực kỹ thuật sâu** — AI/ML cho matching algorithms, thiết kế hạ tầng scalable, engineering production-grade.
- **Tốc độ** — Building plan phủ 4 phase phát triển với deliverables cụ thể. Phase 1 (Foundation) đã hoàn thành.

### Đang bổ sung

Team hiện tại mạnh về tech. Với đầu tư, **tuyển dụng đầu tiên là Business/Operations Lead** — người có kinh nghiệm vận hành ngành dịch vụ, ưu tiên hiểu biết mạng lưới automotive hoặc logistics. Chúng tôi cũng đang tích cực tìm kiếm qua **Founder Matching sessions** của Wash3000.

---

## 8. Đánh Giá Rủi Ro

| Rủi ro | Mức độ | Giải pháp |
|---|---|---|
| **Gara từ chối tham gia** | Cao | Onboard miễn phí, 0% commission 3 tháng, focus fill dead hours (hoàn toàn upside cho gara) |
| **User bypass platform sau khi biết gara** | Cao | Gói subscription (trả trước), loyalty points (chỉ tích qua app), giá ưu đãi app-only, gợi ý đa dạng gara |
| **Đối thủ build giải pháp tương tự** | Trung bình | Data Moat — 3-6 tháng dữ liệu vận hành tạo khoảng cách không bắt kịp. First-mover trong tích hợp VETC. |
| **Team thiếu kinh nghiệm kinh doanh** | Trung bình | Ưu tiên tuyển biz/ops lead. Tận dụng chương trình mentorship Tasco. Tham gia Founder Matching. |
| **Tasco thay đổi chiến lược** | Thấp | Matching engine platform-agnostic — áp dụng được cho bảo dưỡng, detailing, đỗ xe, bất kỳ vertical dịch vụ xe nào. |

---

## 9. Timeline & Mốc Quan Trọng

| Thời gian | Mốc | Kết quả |
|---|---|---|
| **Nay - 23/04** | Nộp hồ sơ | Proposal này + demo prototype |
| **30/04** | Immersion & Team Pitch | Hiểu sâu ngành, pitch cải thiện |
| **Tháng 5/2026** | Vào Top 3 | MVP live, 5+ gara, booking thực đầu tiên |
| **Tháng 5-6** | Proof of Concept | 30+ dịch vụ, 20% activation, 80% feedback |
| **Tháng 7-9** | Scale pilot | 50-200 gara, multi-city, subscription launch |
| **Tháng 10-12** | Triển khai toàn quốc | 800-3.000 điểm kết nối |

---

## 10. Tầm Nhìn Dài Hạn

Rửa xe là **điểm bắt đầu**, không phải đích đến.

```
Năm 1:  Ghép nối & đặt lịch rửa xe (3.000 điểm)
Năm 2:  Bảo dưỡng, detailing, chăm sóc nội thất (mở rộng dịch vụ)
Năm 3:  Bảo hiểm, phụ kiện, marketplace phụ tùng
Năm 4+: Vehicle Intelligence Platform — hệ điều hành cho
         mọi dịch vụ ô tô tại Việt Nam
```

WashMind + Tasco = **Grab của ngành chăm sóc xe.** Một nền tảng bắt đầu từ giao dịch đơn giản, thường xuyên (rửa xe) và mở rộng ra toàn bộ vòng đời sở hữu phương tiện.

Mỗi lần rửa xe tạo ra dữ liệu. Mỗi dữ liệu làm matching thông minh hơn. Mỗi matching thông minh hơn mang lại thêm user. Mỗi user mang thêm gara. **Bánh đà mà đối thủ không thể đảo ngược.**

---

<div align="center">

**WashMind — Đúng nơi. Đúng lúc. Đúng chuẩn.**

*Lớp Thông Minh cho mạng lưới 3.000 điểm chăm sóc xe Việt Nam.*

Liên hệ: duongnguyen4823@gmail.com · tindao2310@gmail.com

© 2026 WashMind Team

</div>
