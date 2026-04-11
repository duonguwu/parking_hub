# WashMind — Tài Liệu Tổng Thể Dự Án

> **Hệ thống điều phối thông minh cho mạng lưới dịch vụ chăm sóc xe**
> *Đề xuất tham gia chương trình Tasco Foundry: Wash3000*

---

**Phiên bản:** 1.0 — Chuẩn hóa  
**Ngày tạo:** 11/04/2026  
**Tác giả:** WashMind Team

---

## Mục lục

1. [Bối cảnh & Lý do chọn đề tài](#1-bối-cảnh--lý-do-chọn-đề-tài)
2. [Giới thiệu dự án](#2-giới-thiệu-dự-án)
3. [Phân tích bài toán](#3-phân-tích-bài-toán)
4. [Giải pháp WashMind](#4-giải-pháp-washmind)
5. [Kiến trúc hệ thống](#5-kiến-trúc-hệ-thống)
6. [Tính năng chính](#6-tính-năng-chính)
7. [Hệ thống phân cấp gara (Garage Tiering)](#7-hệ-thống-phân-cấp-gara-garage-tiering)
8. [Thuật toán chấm điểm & Matching](#8-thuật-toán-chấm-điểm--matching)
9. [Tích hợp hạ tầng Tasco & VETC](#9-tích-hợp-hạ-tầng-tasco--vetc)
10. [Khác biệt & Giá trị cốt lõi](#10-khác-biệt--giá-trị-cốt-lõi)
11. [Phạm vi MVP](#11-phạm-vi-mvp)
12. [Lộ trình phát triển](#12-lộ-trình-phát-triển)
13. [Rủi ro & Giải pháp](#13-rủi-ro--giải-pháp)
14. [Tầm nhìn dài hạn](#14-tầm-nhìn-dài-hạn)

---

## 1. Bối cảnh & Lý do chọn đề tài

### 1.1. Bối cảnh cuộc thi Wash3000

Tasco — đơn vị vận hành hệ thống thu phí tự động VETC với hơn 4 triệu người dùng — đang khởi động chương trình **Tasco Foundry: Wash3000**, một sáng kiến Venture Building quy mô lớn với mục tiêu xây dựng và kết nối **3.000 điểm rửa xe trên toàn quốc Việt Nam** vào cuối năm 2026. Chương trình được hậu thuẫn bởi **GenAI Fund** với tổng mức đầu tư lên đến **$500,000 USD** cho đội chiến thắng.

Tasco không tìm kiếm nhân viên — họ tìm kiếm **những nhà đồng sáng lập (co-founders)** có khả năng thực thi, tư duy chiến lược và tầm nhìn số hóa ngành dịch vụ ô tô Việt Nam.

### 1.2. Tại sao chọn đề tài này?

**Thị trường rửa xe Việt Nam** là một thị trường lớn nhưng cực kỳ phân mảnh:

- **Quy mô:** Với hơn 6 triệu ô tô đang lưu hành (tính đến 2025), nhu cầu chăm sóc xe là thường xuyên và liên tục. Mỗi xe trung bình rửa 2-4 lần/tháng, tạo ra hàng chục triệu lượt giao dịch mỗi tháng trên cả nước.
- **Phân mảnh:** Phần lớn các điểm rửa xe là hộ kinh doanh nhỏ lẻ, không có chuẩn chất lượng chung, không kết nối với nhau, và không có công cụ quản lý vận hành số hóa.
- **Thiếu niềm tin:** Người dùng không có cách nào đánh giá chính xác chất lượng gara trước khi sử dụng. Review trên Google Maps hay mạng xã hội mang tính chủ quan, dễ bị thao túng và không phản ánh năng lực vận hành thực tế.
- **Thiếu tối ưu:** Không có hệ thống nào giúp người dùng ra quyết định "nên rửa xe ở đâu, lúc nào" một cách khoa học — dựa trên khoảng cách, thời gian chờ, năng lực gara và loại xe.

**Cơ hội:** Nếu 3.000 điểm rửa xe được kết nối vào một mạng lưới thống nhất, được tiêu chuẩn hóa và điều phối thông minh, thì đây không chỉ là một dịch vụ rửa xe — mà là **nền tảng chăm sóc xe quốc gia**, tương tự như cách Grab đã thay đổi ngành vận tải.

### 1.3. Ý nghĩa & Mục đích

| Khía cạnh | Nội dung |
|---|---|
| **Với người dùng** | Không còn phải "mò mẫm" tìm gara. Hệ thống đề xuất chính xác nơi phù hợp nhất, giảm thời gian chờ, đảm bảo xe được chăm sóc đúng tiêu chuẩn. |
| **Với gara** | Được số hóa vận hành, tiếp cận nguồn khách hàng lớn từ VETC, tăng hiệu suất sử dụng công suất, minh bạch đánh giá. |
| **Với Tasco/VETC** | Mở rộng hệ sinh thái dịch vụ cho 4M+ người dùng VETC, tăng stickiness, tạo nguồn doanh thu mới từ vertical chăm sóc xe. |
| **Với thị trường** | Tiêu chuẩn hóa ngành rửa xe, nâng cao chất lượng dịch vụ tổng thể, thúc đẩy chuyển đổi số cho SME ngành automotive services. |

---

## 2. Giới thiệu dự án

### 2.1. Tên dự án

**WashMind**

### 2.2. Định vị

> WashMind là **hệ thống điều phối và ra quyết định theo thời gian thực** cho dịch vụ chăm sóc xe, giúp mỗi phương tiện được phục vụ tại **đúng địa điểm**, **đúng thời điểm** và **đúng tiêu chuẩn**.

WashMind không đơn thuần là một ứng dụng "tìm gara rửa xe". WashMind là một **hệ thống thông minh (intelligent system)** kết hợp ba năng lực cốt lõi:

1. **Matching** — Ghép nối người dùng với gara phù hợp nhất dựa trên nhiều yếu tố đồng thời.
2. **Trust** — Xây dựng hệ thống tin cậy bằng dữ liệu vận hành thực tế, không phải rating chủ quan.
3. **Optimization** — Tối ưu hóa toàn bộ trải nghiệm: giảm chờ đợi, giảm di chuyển, tăng chất lượng phục vụ.

### 2.3. Tầm nhìn

Trở thành **lớp thông minh (Intelligence Layer)** cho toàn bộ mạng lưới 3.000 điểm chăm sóc xe của Tasco, nơi mọi quyết định — từ phía người dùng lẫn phía gara — đều được hỗ trợ bởi dữ liệu và thuật toán.

---

## 3. Phân tích bài toán

### 3.1. Hiện trạng thị trường

Ngành rửa xe tại Việt Nam hiện nay vận hành theo mô hình truyền thống, gần như hoàn toàn offline:

- **Phân mảnh quy mô lớn:** Hàng chục ngàn điểm rửa xe trải rộng cả nước, phần lớn là hộ kinh doanh cá thể hoặc tiệm nhỏ, hoạt động độc lập, không có kết nối hay chuẩn chung.
- **Tìm kiếm thủ công:** Người dùng tìm gara bằng cách hỏi người quen, tra Google Maps, hoặc đơn giản là "thấy tiệm nào gần thì ghé". Không có công cụ nào giúp so sánh, đánh giá hay gợi ý có hệ thống.
- **Chất lượng không đồng đều:** Một gara nhỏ ven đường và một trung tâm detailing chuyên nghiệp cùng hiển thị như nhau trên bản đồ, không có cách phân biệt năng lực thực sự.
- **Không dự đoán được:** Người dùng không biết gara có đang đông hay không, phải chờ bao lâu, có đủ thiết bị phù hợp loại xe mình hay không — cho đến khi đã đến nơi.

### 3.2. Ba vấn đề cốt lõi

#### 🔹 Thiếu Trust (Niềm tin)

Đánh giá trên các nền tảng hiện tại (Google Reviews, Facebook...) là chủ quan, dễ thao túng, và không phản ánh năng lực vận hành thực tế. Một gara có 4.9 sao trên Google chưa chắc đã có thiết bị phù hợp để rửa siêu xe. Rating hiện tại đo "cảm xúc khách hàng", không đo "năng lực phục vụ".

#### 🔹 Thiếu Predictability (Khả năng dự đoán)

Người dùng không có cách biết trước:
- Gara có đang quá tải hay không?
- Khi tôi đến nơi, phải chờ bao lâu?
- Gara có đủ năng lực phục vụ loại xe của tôi không?

Hệ quả: người dùng mất thời gian đi đến gara rồi mới biết phải chờ, hoặc gara không đủ khả năng phục vụ.

#### 🔹 Thiếu Optimization (Tối ưu hóa)

Hiện không có hệ thống nào tính toán tổng hợp nhiều yếu tố (khoảng cách, thời gian chờ, năng lực gara, loại xe, thời điểm) để đưa ra gợi ý tối ưu. Người dùng tự quyết định dựa trên thông tin không đầy đủ.

### 3.3. Ví dụ minh họa bài toán

> **Tình huống:** Anh Minh lái chiếc Mercedes S-Class. Lúc 18:30, anh muốn rửa xe gần khu vực quận 1, TP.HCM. Anh mở Google Maps, thấy 5 gara gần đó. Anh chọn gara gần nhất (cách 2km), đến nơi thì phát hiện:
>
> - Gara đang phục vụ 4 xe, phải chờ ít nhất 45 phút.
> - Gara chỉ là tiệm rửa xe bình thường, không có thiết bị phù hợp để rửa xe cao cấp.
> - Anh quay lại tìm gara khác, mất thêm 30 phút di chuyển.
>
> **Với WashMind:** Hệ thống biết:
> - Xe của anh Minh là Mercedes S-Class → cần gara Tier 3 (Pro) hoặc Tier 4 (Elite).
> - Gara A gần nhất nhưng chỉ Tier 1, loại bỏ.
> - Gara B cách 5km, đang phục vụ 4 xe, nhưng thời gian di chuyển là 20 phút, trong 20 phút đó gara sẽ xử lý xong 2 xe → khi anh đến, chỉ còn chờ ~10 phút.
> - Gara C cách 3km, Tier 4 (Elite), hiện đang rảnh.
>
> → WashMind gợi ý: **Gara C** (ưu tiên) và **Gara B** (lựa chọn thay thế), kèm thời gian dự kiến và tuyến đường.

---

## 4. Giải pháp WashMind

WashMind giải quyết bài toán bằng **ba trụ cột chiến lược:**

### 4.1. Smart Matching Engine — Động cơ ghép nối thông minh

Đây là trái tim của hệ thống. Không đơn giản là "trả về danh sách gara gần nhất" — Matching Engine đồng thời tính toán **nhiều biến số** để đưa ra gợi ý tối ưu:

- **Khoảng cách thực tế** (không phải đường chim bay) — sử dụng GoongIO Maps API để tính thời gian di chuyển chính xác theo giao thông thực.
- **Trạng thái vận hành real-time** của gara — đang phục vụ bao nhiêu xe, công suất tối đa, thời gian xử lý trung bình.
- **Dự đoán trạng thái tương lai** — tại thời điểm người dùng đến nơi (không phải thời điểm tìm kiếm), gara có sẵn sàng hay không.
- **Mức độ phù hợp** — gara có đủ tier, thiết bị và kinh nghiệm để phục vụ loại xe của người dùng hay không.

**Điểm khác biệt then chốt:** Các hệ thống hiện tại (Google Maps, các app booking) đánh giá trạng thái gara tại thời điểm tìm kiếm. WashMind đánh giá trạng thái gara tại **thời điểm người dùng đến nơi**, tính cả thời gian di chuyển. Một gara đang "quá tải" lúc 18:30 nhưng sẽ "rảnh" lúc 18:50 (khi bạn đến) vẫn là lựa chọn tốt — và WashMind biết điều đó.

### 4.2. Garage Tiering System — Hệ thống phân cấp gara

Không phải gara nào cũng giống nhau. WashMind xây dựng hệ thống phân cấp dựa trên **năng lực vận hành thực tế**, không phải tự khai báo hay rating khách hàng:

- Đánh giá thiết bị, quy trình, nhân sự, diện tích, dịch vụ.
- Phân loại thành 4 cấp: Basic → Standard → Pro → Elite.
- Mapping tự động: đúng loại xe vào đúng cấp gara.

→ **Bảo vệ trải nghiệm người dùng** (xe sang không bị đưa vào gara không đủ năng lực) và **bảo vệ gara** (không bị quá tải với loại xe vượt quá khả năng).

### 4.3. Trust Layer — Lớp tin cậy dựa trên dữ liệu

Thay thế hệ thống rating 5 sao truyền thống bằng **scoring dựa trên dữ liệu vận hành**:

- Thời gian xử lý thực tế so với cam kết.
- Tỷ lệ khách hàng quay lại.
- Tỷ lệ khiếu nại / complaint.
- Mức độ ổn định qua thời gian.

→ Score được cập nhật liên tục, gara có thể được nâng hoặc hạ cấp dựa trên hiệu suất thực tế. Đây là hệ thống **tự điều chỉnh (self-correcting)**.

---

## 5. Kiến trúc hệ thống

WashMind được thiết kế theo kiến trúc **3 lớp (3-Layer Architecture)**, mỗi lớp có vai trò rõ ràng và có thể phát triển độc lập:

| Layer | Tên gọi | Vai trò | Thành phần chính |
|---|---|---|---|
| **Layer 1** | **Supply Layer** | Quản lý phía cung (gara) | Onboarding gara, đánh giá chất lượng, phân cấp tier, theo dõi hiệu suất vận hành, cập nhật trạng thái real-time |
| **Layer 2** | **Demand Layer** | Tiếp nhận phía cầu (người dùng) | Nhận yêu cầu tìm kiếm, thu thập context (vị trí, thời gian, loại xe), trình bày kết quả, xử lý đặt lịch |
| **Layer 3** | **Intelligence Layer** | Tính toán & ra quyết định | Matching engine, scoring engine, routing logic, capacity prediction, demand forecasting (mở rộng) |

### Luồng hoạt động tổng quát

```
Người dùng gửi yêu cầu (vị trí, thời gian, loại xe)
        ↓
  [Demand Layer] Thu thập context, validate input
        ↓
  [Intelligence Layer] 
     → Lọc gara theo tier phù hợp
     → Tính khoảng cách & thời gian di chuyển (GoongIO Maps)
     → Dự đoán trạng thái gara tại thời điểm đến
     → Tính match score tổng hợp
     → Xếp hạng & chọn top 1-3 gara
        ↓
  [Demand Layer] Trình bày kết quả + gợi ý
        ↓
  Người dùng chọn → Đặt lịch / Điều hướng
        ↓
  [Supply Layer] Cập nhật trạng thái gara
```

### Hạ tầng & Tích hợp

Hệ thống được xây dựng trên nền tảng hạ tầng mà Tasco đã cung cấp sẵn:

- **Backend:** Python (FastAPI / Django)
- **Frontend:** React
- **Bản đồ & Định tuyến:** GoongIO Maps API (do Tasco cung cấp)
- **Thanh toán:** Tasco Payment APIs (tích hợp VETC)
- **Nguồn người dùng:** 4M+ tài khoản VETC

*(Chi tiết về stack kỹ thuật sẽ được mô tả trong tài liệu Technical Architecture riêng)*

---

## 6. Tính năng chính

### 6.1. Smart Matching Engine

**Mục tiêu:** Chọn gara tối ưu nhất cho người dùng, không phải trả về một danh sách để họ tự chọn.

**Input:**
- Vị trí hiện tại (hoặc vị trí dự kiến) của người dùng
- Thời gian mong muốn rửa xe
- Loại xe (phổ thông, cao cấp, sang, siêu xe)
- Lịch sử và preference (nếu có)

**Output:**
- Top 1-3 gara phù hợp nhất
- Kèm theo: thời gian di chuyển, thời gian chờ dự kiến, tier gara, match score

**Ví dụ thực tế:**

> Tại 18:30, gara X đang phục vụ 4 xe (tối đa công suất), trung bình mỗi xe mất 15 phút. Người dùng cách gara X 25 phút đi xe. Khi người dùng đến (18:55), gara đã hoàn thành ~1-2 xe tùy tiến trình → có slot sẵn sàng.
>
> → **Gara X vẫn là gợi ý hợp lệ**, dù tại thời điểm tìm kiếm nó đang "full". Đây là tối ưu hóa mà không có hệ thống nào trên thị trường hiện tại làm được.

### 6.2. Real-time Capacity Monitoring

Theo dõi tình trạng vận hành gara theo thời gian thực:

- Số xe đang được phục vụ / đang chờ.
- Ước tính thời gian chờ cho xe tiếp theo.
- Năng lực xử lý (xe/giờ) dựa trên dữ liệu lịch sử.
- Cảnh báo "cao điểm" để người dùng chủ động tránh.

### 6.3. Context-aware Recommendation (Gợi ý theo ngữ cảnh)

Thay vì chỉ gợi ý khi người dùng chủ động tìm kiếm, WashMind có khả năng **gợi ý chủ động** dựa trên ngữ cảnh:

- Đề xuất gara trên đường về nhà / trên lộ trình di chuyển.
- Nhắc nhở dựa trên lịch rửa xe gần nhất ("Bạn đã 2 tuần chưa rửa xe").
- Gợi ý thời điểm vắng khách ("Thứ 3 trưa thường rảnh nhất tại gara yêu thích của bạn").

### 6.4. Giao diện hội thoại (Conversational Interface)

Người dùng có thể tương tác với WashMind bằng ngôn ngữ tự nhiên, thay vì phải điền form:

- **Input mẫu:** *"7h tối nay tôi muốn rửa xe gần Quận 1"*
- **Hệ thống hỏi lại:** *"Xe của bạn là loại gì? Bạn muốn rửa ngoại thất hay full detailing?"*
- **Output:** Gợi ý gara kèm thời gian, tuyến đường, thời gian chờ.

Giao diện hội thoại giúp:
- Thu thập context một cách tự nhiên (vị trí dự kiến, thời gian, yêu cầu đặc biệt).
- Giảm ma sát UX — người dùng không cần biết cách dùng app, chỉ cần "nói" nhu cầu.
- Hỗ trợ lên lịch tương lai: *"Tối mai 8h tôi sẽ ở Thủ Đức, tìm gara giúp tôi"*.

### 6.5. Hệ thống đặt lịch (Scheduling & Booking)

- Đặt lịch trước tại gara mong muốn.
- Hệ thống tự động khớp slot còn trống.
- Nhắc nhở trước giờ hẹn.
- Hủy / dời lịch linh hoạt.

---

## 7. Hệ thống phân cấp gara (Garage Tiering)

### 7.1. Mục đích

Bảo vệ trải nghiệm người dùng bằng cách đảm bảo **đúng loại xe được phục vụ tại đúng loại gara**, và ngược lại, bảo vệ gara không bị nhận xe vượt quá năng lực.

### 7.2. Bốn cấp độ gara

| Tier | Tên | Định nghĩa | Phù hợp cho | Ví dụ |
|---|---|---|---|---|
| **Tier 1** | **Basic** | Thiết bị cơ bản, rửa xe tay hoặc máy đơn giản | Xe phổ thông, xe máy | Tiệm rửa xe ven đường |
| **Tier 2** | **Standard** | Quy trình ổn định, thiết bị trung bình, có khu chờ | Xe gia đình, sedan | Gara có diện tích vừa, 2-3 bay |
| **Tier 3** | **Pro** | Thiết bị chuyên nghiệp, có detailing cơ bản, nhân viên được đào tạo | Xe cao cấp, SUV hạng sang | Trung tâm chăm sóc xe chuyên nghiệp |
| **Tier 4** | **Elite** | Thiết bị cao cấp, quy trình detailing chuẩn, SOP nghiêm ngặt | Xe sang, siêu xe, xe cổ | Studio detailing chuyên biệt |

### 7.3. Matching xe ↔ gara

| Loại xe | Tier được phép |
|---|---|
| Xe phổ thông | Tier 1, 2, 3 |
| Xe cao cấp | Tier 2, 3, 4 |
| Xe sang | Tier 3, 4 |
| Siêu xe / Xe đặc biệt | Chỉ Tier 4 |

→ Matching engine tự động lọc gara không đủ tier trước khi tính score, đảm bảo mọi gợi ý đều đáp ứng yêu cầu tối thiểu.

---

## 8. Thuật toán chấm điểm & Matching

### 8.1. Garage Score (Điểm gara)

Mỗi gara được chấm điểm dựa trên **5 nhóm tiêu chí:**

| Nhóm | Yếu tố đánh giá | Trọng số (tham khảo) |
|---|---|---|
| **Equipment** | Thiết bị, dụng cụ, hóa chất | w1 |
| **Process** | Quy trình, SOP, thời gian xử lý | w2 |
| **Staff** | Kinh nghiệm, đào tạo, thái độ | w3 |
| **Capacity** | Công suất, diện tích, số bay | w4 |
| **Reliability** | Tỷ lệ khách quay lại, complaint rate, ổn định | w5 |

**Công thức:**

```
Garage Score = w1 × Equipment + w2 × Process + w3 × Staff + w4 × Capacity + w5 × Reliability
```

**Phân cấp theo score:**

| Khoảng điểm | Tier |
|---|---|
| 0 – 40 | Basic |
| 40 – 70 | Standard |
| 70 – 85 | Pro |
| 85+ | Elite |

### 8.2. Match Score (Điểm ghép nối)

Khi người dùng tìm kiếm, mỗi gara đủ điều kiện (đã qua bước lọc tier) được tính **Match Score** tổng hợp:

```
Match Score = a × DistanceScore + b × WaitTimeScore + c × GarageQualityScore + d × VehicleFitScore
```

Trong đó:
- **DistanceScore:** Tính dựa trên khoảng cách thực tế và thời gian di chuyển (GoongIO Maps API).
- **WaitTimeScore:** Ước tính thời gian chờ tại thời điểm người dùng đến (không phải thời điểm tìm kiếm).
- **GarageQualityScore:** Garage Score tổng hợp.
- **VehicleFitScore:** Mức độ phù hợp giữa tier gara và loại xe.

→ Gara có Match Score cao nhất được xếp hạng đầu trong danh sách gợi ý.

### 8.3. Hệ thống cập nhật liên tục (Continuous Scoring)

Score không tĩnh — nó được cập nhật liên tục dựa trên:

- Thời gian xử lý thực tế so với ước tính.
- Feedback khách hàng (có trọng số thấp hơn dữ liệu vận hành).
- Tỷ lệ khách quay lại (retention rate).
- Complaint rate.

→ Gara cải thiện chất lượng → score tăng → tự động được nâng tier.  
→ Gara giảm chất lượng → score giảm → cảnh báo hoặc hạ tier.

---

## 9. Tích hợp hạ tầng Tasco & VETC

Đây là **lợi thế cạnh tranh không thể thay thế (unfair advantage)** mà Tasco cung cấp cho các đội tham gia Wash3000:

### 9.1. VETC Integration (4M+ Users)

- **Nguồn người dùng sẵn có:** Hơn 4 triệu tài khoản VETC đang hoạt động — đây là người dùng đã sở hữu ô tô, có nhu cầu chăm sóc xe thực sự, và đã quen với thanh toán điện tử.
- **Thanh toán liền mạch:** Tích hợp thanh toán qua tài khoản VETC, không cần nhập thêm phương thức thanh toán.
- **Chương trình loyalty:** Tích điểm, ưu đãi cho người dùng VETC khi sử dụng WashMind — tạo thói quen sử dụng.
- **Nhận diện xe tự động:** Thông tin phương tiện từ VETC giúp WashMind biết loại xe mà không cần người dùng nhập thủ công → giảm ma sát, tăng tốc matching.

### 9.2. GoongIO Maps API

- **Bản đồ & Định vị chính xác:** Hiển thị gara trên bản đồ, xác định vị trí người dùng.
- **Routing & ETA:** Tính toán tuyến đường tối ưu, thời gian di chuyển chính xác theo giao thông thời gian thực. **Đây là input quan trọng cho Matching Engine** — WashMind cần biết chính xác "khi user đến gara thì mất bao lâu" để dự đoán trạng thái gara tại thời điểm đến.
- **Tìm kiếm theo khu vực:** Lọc gara theo vùng, quận/huyện, hoặc trên tuyến đường di chuyển.

### 9.3. Tasco Payment APIs

- **Thanh toán điện tử:** Cho phép thanh toán dịch vụ rửa xe trực tiếp qua app.
- **Tách bạch tài chính:** Phân phối doanh thu cho gara minh bạch, tự động.
- **Nền tảng cho mô hình kinh doanh:** Đặt cọc, thanh toán trả trước, gói dịch vụ, subscription — tất cả dựa trên payment infrastructure sẵn có.

---

## 10. Khác biệt & Giá trị cốt lõi

### WashMind KHÔNG phải:

| ❌ Không phải | Lý do |
|---|---|
| App tìm gara (như Google Maps) | Google Maps hiển thị, WashMind **quyết định** |
| Marketplace đơn thuần (như Shopee) | Marketplace liệt kê, WashMind **tối ưu** |
| Hệ thống đánh giá/review | Review đo cảm xúc, WashMind đo **hiệu suất** |

### WashMind LÀ:

| ✅ WashMind là | Giải thích |
|---|---|
| **Hệ thống điều phối** | Kết nối supply (gara) và demand (người dùng) một cách thông minh |
| **Hệ thống phân cấp** | Đúng xe, đúng gara, đúng tiêu chuẩn |
| **Hệ thống trust** | Tin cậy dựa trên dữ liệu, không phải ý kiến chủ quan |
| **Lớp thông minh** | Tối ưu hóa quyết định cho cả hai phía |

---

## 11. Phạm vi MVP

### 11.1. Nguyên tắc MVP

MVP không phải "sản phẩm hoàn chỉnh thu nhỏ" — mà là **phiên bản tối thiểu để chứng minh giải pháp hoạt động**. Trọng tâm MVP là chứng minh:

1. **Matching Engine hoạt động chính xác hơn Google Maps** trong việc tìm gara phù hợp.
2. **Hệ thống phân cấp gara có ý nghĩa thực tế** — xe cao cấp thực sự được gợi ý gara đủ năng lực.
3. **Real-time capacity tracking khả thi** — có thể theo dõi và dự đoán tình trạng gara.

### 11.2. MVP bao gồm

| Tính năng | Mô tả | Ưu tiên |
|---|---|---|
| Matching Engine (core) | Tìm gara dựa trên vị trí, loại xe, thời gian, tải vận hành | ⭐ Bắt buộc |
| Garage Tiering (cơ bản) | Phân cấp 3-5 gara pilot theo 4 tier | ⭐ Bắt buộc |
| Real-time status | Hiển thị trạng thái đang phục vụ / chờ | ⭐ Bắt buộc |
| Giao diện tìm kiếm | UI đơn giản để nhập yêu cầu, xem kết quả trên bản đồ | ⭐ Bắt buộc |
| GoongIO Maps integration | Bản đồ, routing, ETA | ⭐ Bắt buộc |
| Đặt lịch cơ bản | Chọn gara → xác nhận → nhận thông báo | 🔷 Cần thiết |
| Conversational interface | Chatbot đơn giản để nhận yêu cầu bằng ngôn ngữ tự nhiên | 🔷 Cần thiết |

### 11.3. MVP KHÔNG bao gồm (tại giai đoạn này)

- UI phức tạp / nhiều trang.
- Thanh toán tích hợp (pilot dùng thanh toán trực tiếp tại gara).
- AI/ML nâng cao (demand prediction, personalization).
- Hệ thống loyalty / gamification.

---

## 12. Lộ trình phát triển

Lộ trình được thiết kế **khớp với timeline 12 tuần** của chương trình Wash3000:

### Phase 1 — Tuần 1-2: Program Understanding & Preparation

| Hoạt động | Kết quả |
|---|---|
| Tham gia Kickoff & Meetup của Tasco | Hiểu rõ thesis, ecosystem, kỳ vọng |
| Nghiên cứu sâu thị trường rửa xe | Dữ liệu thị trường, pain points thực tế |
| Finalize đề xuất & team chemistry | Tài liệu dự án chuẩn hóa, phân công vai trò |
| Tiếp cận GoongIO & VETC APIs | Hiểu capabilities, giới hạn, tài liệu kỹ thuật |

### Phase 2 — Tuần 3-4: Team Formation & Selection Pitch

| Hoạt động | Kết quả |
|---|---|
| Hoàn thiện prototype / wireframe | UI mockup, demo flow |
| Xây dựng pitch deck | Trình bày chiến lược, kiến trúc, roadmap |
| Selection Pitch | Vào Top 10 để tiến vào Immersion |

### Phase 3 — Tuần 5-6: The Immersion — MVP Deployment

| Hoạt động | Kết quả |
|---|---|
| Field training tại gara thực tế | Hiểu vận hành thực, pain points chủ gara |
| Xây dựng & deploy MVP | Backend + Frontend hoạt động |
| Onboard 3-5 gara pilot | Dữ liệu thực, tier assessment |
| Tích hợp GoongIO Maps | Matching Engine có routing & ETA thực |
| Pitch Day | Vào Top 3, nhận $7,000 USD pilot funding |

### Phase 4 — Tuần 7-10: Refine & Scale Pilot

| Hoạt động | KPI |
|---|---|
| The 50/500 Challenge | Onboard 5 locations, kích hoạt 30 customers |
| Tối ưu Matching Engine | Accuracy, user satisfaction |
| Thu thập dữ liệu vận hành | Xây dựng scoring system thực tế |
| Tối ưu Unit Economics & CAC | Chi phí hợp lý, mô hình bền vững |
| Weekly review với mentors | Iterate liên tục |

### Phase 5 — Tuần 11-12: Grand Demo Day

| Hoạt động | Kết quả |
|---|---|
| Tổng hợp traction metrics | Số liệu thực từ pilot |
| Xây dựng roadmap 3,000 locations | Chiến lược scale toàn quốc |
| Demo Day pitch | Trình bày trước Investment Committee |
| Mục tiêu | Giành $500,000 USD investment |

---

## 13. Rủi ro & Giải pháp

| Rủi ro | Mức độ | Giải pháp |
|---|---|---|
| **Thu thập dữ liệu real-time từ gara** | Cao | Bắt đầu đơn giản (gara tự cập nhật qua app), sau đó tích hợp IoT/camera |
| **Gara không muốn tham gia / bị đánh giá** | Cao | Thể hiện giá trị rõ ràng (tăng khách, tối ưu vận hành), chính sách hỗ trợ onboarding |
| **Dữ liệu ban đầu chưa đủ để matching chính xác** | Trung bình | Cold-start bằng manual assessment, sau đó tự cải thiện bằng dữ liệu vận hành |
| **Người dùng chưa có thói quen dùng app rửa xe** | Trung bình | Tận dụng 4M+ VETC users, tích hợp vào flow quen thuộc, ưu đãi dùng thử |
| **Chất lượng GoongIO ETA chưa chính xác** | Thấp | Kết hợp nhiều nguồn, calibrate bằng dữ liệu thực |

---

## 14. Tầm nhìn dài hạn

### Ngắn hạn (0-6 tháng)
- Matching Engine chạy ổn định tại 5-10 gara pilot.
- Chứng minh product-market fit.
- Tối ưu unit economics.

### Trung hạn (6-18 tháng)
- Scale lên 100-500 gara.
- Trust system hoạt động tự động (scoring, nâng/hạ tier).
- Tích hợp thanh toán VETC.
- Conversational AI nâng cao.
- Demand prediction (dự đoán khung giờ cao/thấp điểm).

### Dài hạn (18+ tháng)
- **3,000+ điểm rửa xe** kết nối toàn quốc.
- Mở rộng sang các dịch vụ chăm sóc xe khác (bảo dưỡng, sơn, nội thất).
- **Vehicle Intelligence Layer** — hiểu sâu từng phương tiện, lịch sử chăm sóc, gợi ý proactive.
- Trở thành **nền tảng dịch vụ ô tô quốc gia** — "Super app for car care".

---

## Thiết kế mạng lưới giá trị

| Bên tham gia | Họ có | Họ nhận được |
|---|---|---|
| **Gara (Supply)** | Mặt bằng, nhân lực, thiết bị | Khách hàng từ VETC, tối ưu vận hành, tăng doanh thu, được đánh giá công bằng |
| **Người dùng (Demand)** | Nhu cầu rửa xe, sẵn sàng chi tiền | Gợi ý chính xác, tiết kiệm thời gian, xe được chăm sóc đúng chuẩn |
| **Tasco/VETC (Platform)** | 4M+ users, payment APIs, brand | Mở rộng ecosystem, doanh thu mới, tăng user engagement |
| **WashMind (Intelligence)** | Thuật toán, data logic, execution | Vị thế co-founder, đầu tư, dữ liệu để cải thiện liên tục |

---

> **WashMind — Đúng nơi. Đúng lúc. Đúng chuẩn.**
>
> *Hệ thống điều phối thông minh cho mạng lưới 3,000 điểm chăm sóc xe Việt Nam.*
