Ừ, chốt lại thành một **mini design document** thì tui sẽ viết thế này. Và tui check lại vụ giao thông: Cổng giao thông TP.HCM **có riêng “Tình trạng giao thông” theo thời gian thực và “Cảnh báo kẹt xe”**, ngoài camera, sự cố, rào chắn và phân luồng. Họ còn mô tả mật độ giao thông realtime để chọn lộ trình. [Cổng Thông Tin Giao Thông Hồ Chí Minh](https://giaothong.hochiminhcity.gov.vn/Userguide/?utm_source=chatgpt.com)

# Parking HUB — Smart Parking Routing

### 1. Mục tiêu

Không chỉ tìm **bãi đỗ gần nhất**, mà tìm:

> **Bãi đỗ phù hợp nhất + con đường hợp lý nhất để user đến được bãi đó trong điều kiện thực tế hiện tại.**

Flow tổng:

```text
Vị trí user + Điểm đến
        ↓
Candidate parking
        ↓
Filter bãi phù hợp
        ↓
Tính route đến từng bãi
        ↓
Traffic + Weather + Flood + Incident
        ↓
Đánh giá route
        ↓
Parking availability tại ETA
        ↓
Rank
        ↓
Top 3 parking
```

---

## 2. Các nhóm thông tin cần kết hợp

| Layer | Thông tin | Mục đích |
|---|---|---|
| 🅿️ **Parking** | loại xe, giá, giờ mở cửa, tiện ích, số chỗ trống | Bãi có phù hợp không |
| 🗺️ **Route / OSM** | distance, ETA, road graph | Đường đi cơ sở |
| 🚗 **Traffic** | mật độ giao thông, kẹt xe, camera | Tránh đường đang ùn |
| 🌧️ **Weather** | mưa hiện tại + lượng mưa + dự báo rất ngắn hạn theo vị trí | Dự đoán tình trạng route sắp tới |
| 🌊 **Flood** | lịch sử + realtime evidence + thời tiết | Tránh đường ngập/nguy cơ ngập |
| 🚧 **Incident** | sự cố, rào chắn, phân luồng | Block/penalty đoạn đường |
| 📷 **Camera AI** | traffic, nước, mưa, visibility | Sensor bổ sung cho dữ liệu realtime |

Riêng nguồn giao thông TP.HCM đáng khai thác vì phía chính thức đã có **tình trạng giao thông, cảnh báo kẹt xe, camera, sự cố, rào chắn và phân luồng**. [Cổng Thông Tin Giao Thông Hồ Chí Minh](https://giaothong.hochiminhcity.gov.vn/Userguide/?utm_source=chatgpt.com)

---

# 3. Traffic

Ưu tiên theo thứ tự:

```text
Official traffic state
        +
Congestion warning
        +
Incident / road work
        +
Camera AI
        ↓
Traffic state của road segment
```

Camera AI đóng vai trò bổ sung:

```text
FREE
MODERATE
CONGESTED
UNKNOWN
```

Case **đèn đỏ nhưng xe đông** trước mắt có thể chấp nhận sai. Sau này dùng nhiều frame theo thời gian để phân biệt:

```text
đông → thoáng → đông → thoáng
       traffic light

đông → đông → đông → đông
       congestion
```

Quan trọng là nguồn chính thức nói rõ họ có **mật độ giao thông theo thời gian thực**, và hệ thống của họ cũng hỗ trợ tìm route theo tình trạng giao thông. [Cổng Thông Tin Giao Thông Hồ Chí Minh](https://www.giaothong.hochiminhcity.gov.vn/About/?utm_source=chatgpt.com)

---

# 4. Weather — layer tui nghĩ rất đáng đầu tư

Không dùng:

```text
TP.HCM: đang mưa
```

mà nên hướng tới:

```text
rain(lat, lng, time)
```

Ví dụ cùng lúc:

```text
Gia Định       12 mm/h  🌧️🌧️🌧️
Bến Thành       2 mm/h  🌦️
Thủ Đức         0 mm/h  ☁️
Tân Sơn Nhất    7 mm/h  🌧️
```

Route dài 20 phút thì còn có thể xét:

```text
User ─────────────── Parking
        ↑
   segment này user
   tới sau 12 phút

→ lúc đó có mưa không?
```

Do đó dữ liệu lý tưởng là **rainfall radar / precipitation nowcast**, chứ không chỉ weather forecast toàn thành phố.

Weather không nhất thiết block route. Nó làm tăng:

```text
Traffic Risk
Flood Risk
Travel Time Uncertainty
```

Đây có thể trở thành một điểm khá đặc trưng của Parking HUB.

---

# 5. Flood — mô hình 3 tầng

Phần này tui vẫn giữ nguyên vì khá hợp bài toán:

```text
            FLOOD INTELLIGENCE

 Historical         Realtime           Weather
     │                  │                 │
điểm từng ngập       camera AI        mưa hiện tại
tần suất ngập        user report      cường độ mưa
mức ngập cũ          official data    rain nowcast
     │                  │                 │
     └──────────────────┼─────────────────┘
                        ↓
                  Flood Risk
                        ↓
              road segment penalty
```

### Layer 1 — Historical

Cho biết:

> **Đường này vốn có dễ ngập không?**

Không dùng history để kết luận **đang ngập**.

### Layer 2 — Realtime evidence

Camera thấy:

```text
road wet
standing water
flooded
```

hoặc report / nguồn chính thức.

Cho biết:

> **Hiện tại có bằng chứng ngập không?**

### Layer 3 — Weather

Nếu:

```text
historical risk HIGH
+ heavy rain NOW
+ camera suspicious
```

→ xác suất ngập cực cao.

Tức:

\[
P(Flood_{now}) =
f(History,\ Camera,\ Report,\ Rain)
\]

---

# 6. Cuối cùng mới chọn bãi

Đầu tiên lấy khoảng **10–30 parking candidate** gần user/điểm đến.

Hard filter:

```text
✓ đúng loại xe
✓ đang mở
✓ đáp ứng yêu cầu
✓ còn/khả năng còn chỗ

✗ đường bị block
✗ ngập nghiêm trọng
```

Sau đó route + ranking:

\[
Score =
ParkingQuality
- TravelTime
- TrafficRisk
- FloodRisk
- WeatherRisk
- Price
- WalkingDistance
\]

Cuối cùng trả **Top 3**, nhưng quan trọng là giải thích được:

> 🥇 **Parking A — Recommended**  
> 11 phút • 2.7 km • còn ~14 chỗ  
> 🟢 Giao thông tốt  
> 🟢 Không ghi nhận ngập  
> 🌦 Có mưa nhẹ trên một đoạn tuyến
>
> **Parking B gần hơn 500 m**, nhưng route đang ùn và đi qua khu vực có nguy cơ ngập cao.

---

### Kiến trúc chốt lại

```text
                USER
                  │
          Parking Candidates
                  │
          Parking Hard Filter
                  │
                  ▼
             OSM ROUTING
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     TRAFFIC    WEATHER    FLOOD
        │         │       ┌─┴──────────┐
 Official/API   Radar   History Camera
 Camera AI     Nowcast  Report  Weather
        │         │       └─┬──────────┘
        └─────────┼─────────┘
                  ▼
             ROUTE RISK
                  │
        Parking availability
             at ETA
                  │
                  ▼
             FINAL RANK
                  │
              TOP 3
```

**Nếu chia roadmap**, tui sẽ làm `OSM routing + official traffic + parking realtime` trước → thêm **weather spatial/nowcast** → thêm **historical flood** → cuối cùng mới thêm **Camera AI** để xác nhận traffic/ngập. Như vậy mỗi bước đều chạy được độc lập, không biến project thành một cục CV + GIS + weather khổng lồ ngay từ đầu.