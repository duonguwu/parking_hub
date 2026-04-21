# WashMind Customer Portal — API Integration Specification

> **Cập nhật lần cuối:** 20/04/2026  
> **Base URL:** `http://localhost:8000` (dev) | `https://api.washmind.vn` (prod)  
> **Auth:** HttpOnly Cookie (`access_token`). FE **không** dùng `Authorization: Bearer`, **không** lưu token vào LocalStorage.  
> **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)

---

## Quy ước Response chung

Mọi API đều trả về envelope chuẩn:

```json
{
  "status": "ok",
  "message": "...",
  "data": { ... }
}
```

Lỗi trả về HTTP status code tương ứng + `{ "detail": "..." }`.

---

## ✅ Status triển khai

| # | Endpoint | Method | Auth | Status |
|---|---|---|---|---|
| 1 | `/auth/login` | POST | Public | ✅ Đã có |
| 2 | `/auth/register` | POST | Public | ✅ Đã có |
| 3 | `/auth/me` | GET | 🔒 Cookie | ✅ Đã có |
| 4 | `/customer/dashboard-summary` | GET | 🔒 Cookie | ✅ **Mới** |
| 5 | `/customer/nearby` | GET | Public | ✅ **Mới** |
| 6 | `/customer/garages/{id}/portal` | GET | Public | ✅ **Mới** |
| 7 | `/customer/bookings` | GET | 🔒 Cookie | ✅ **Mới** |
| 8 | `/customer/bookings/{id}` | GET | 🔒 Cookie | ✅ **Mới** |
| 9 | `/customer/bookings/{id}/tracking` | GET | 🔒 Cookie | ✅ **Mới** |
| 10 | `/customer/vehicles` | GET | 🔒 Cookie | ✅ **Mới** |
| 11 | `/customer/vehicles` | POST | 🔒 Cookie | ✅ **Mới** |
| 12 | `/customer/vehicles/{id}/default` | PUT | 🔒 Cookie | ✅ **Mới** |
| 13 | `/bookings/create` | POST | 🔒 Cookie | ✅ Đã có |

---

### 📦 Data được tạo

| Collection | Số lượng | Chi tiết |
|---|---|---|
| **Users** | 9 | 1 super admin + 5 garage owners + 3 customers |
| **Tenants** | 5 | 5 garages độc lập |
| **Garages** | 5 | Rải khắp HCMC với tọa độ thực (Q1, Q3, Q7, Bình Thạnh, Gò Vấp) |
| **Garage Services** | 17 | Mỗi garage 3-5 services với giá theo tier |
| **Vehicles** | 7 | VinFast VF8, Mercedes C300, Toyota Camry, Honda CR-V, Tesla Model S, BMW M5, Kia K5 |
| **Bookings** | 20 | Đầy đủ mọi status: pending, confirmed, in_service, completed, cancelled, no_show |
| **Capacity Snapshots** | 980 | 14 ngày × 14 giờ × 5 garages → fuel capacity chart với data thực |

## 1. Authentication

```
customer_an    / Customer@2026    (VinFast VF8 + Mercedes C300)
customer_binh  / Customer@2026    (Toyota Camry + Honda CR-V)
customer_cuong / Customer@2026    (Tesla Model S + BMW M5 + Kia K5)

aquaglide_owner / GarageOwner@2026   (all garage owners same pw)
admin           / WashMind@2026!
```

> FE sử dụng **HttpOnly Cookie** — phải dùng `credentials: 'include'` trong mọi fetch request.

### POST `/auth/login`

**Request:**
```json
{
  "username": "nguyenvana",
  "password": "SecurePass@123"
}
```

**Response:** HTTP `Set-Cookie: access_token=<jwt>; HttpOnly; SameSite=Lax`
```json
{
  "status": "ok",
  "message": "Login successful",
  "data": {
    "user": {
      "user_id": "6801a2f3c1d4e5b6a7890001",
      "username": "nguyenvana",
      "name": "Nguyễn Văn A",
      "role": "customer",
      "tenant_id": null
    }
  }
}
```

---

### POST `/auth/register`

**Request:**
```json
{
  "username": "nguyenvana",
  "password": "SecurePass@123",
  "name": "Nguyễn Văn A",
  "email": "a@mail.com",
  "phone": "0901234567"
}
```

**Response:** Tự động Set-Cookie → auto-login sau register.
```json
{
  "status": "ok",
  "message": "Customer registered successfully",
  "data": {
    "user": {
      "user_id": "6801a2f3c1d4e5b6a7890001",
      "username": "nguyenvana",
      "name": "Nguyễn Văn A",
      "role": "customer",
      "tenant_id": null
    }
  }
}
```

---

### GET `/auth/me`

🔒 Yêu cầu cookie.

**Response:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "6801a2f3c1d4e5b6a7890001",
    "username": "nguyenvana",
    "name": "Nguyễn Văn A",
    "role": "customer",
    "tenant_id": null,
    "permissions": []
  }
}
```

---

## 2. Customer Dashboard Summary

> Phục vụ `CustomerHome.tsx`. Aggregated endpoint gộp 3 nguồn: vehicle health + nearby garages + active booking.

### GET `/customer/dashboard-summary`

🔒 Yêu cầu cookie.

**Query Params:**

| Param | Type | Required | Mô tả |
|---|---|---|---|
| `lat` | float | optional | Vĩ độ user hiện tại |
| `lng` | float | optional | Kinh độ user hiện tại |

> Nếu không truyền `lat`/`lng` thì `smart_recommendations` trả về `[]`.

**Request:**
```
GET /customer/dashboard-summary?lat=10.7761&lng=106.7011
```

**Response:**
```json
{
  "status": "ok",
  "message": "Dashboard_summary retrieved successfully",
  "data": {
    "vehicle_diagnostics": {
      "default_vehicle_id": "6801b3c4d5e6f7a8b9000001",
      "license_plate": "51K-123.45",
      "brand": "VinFast",
      "model": "VF8",
      "vehicle_type": "premium",
      "finish_degradation": -12,
      "days_since_last_service": 14
    },
    "smart_recommendations": [
      {
        "id": "6801c4d5e6f7a8b900000a",
        "name": "AutoSpa Quận 3",
        "tier": "PRO",
        "distance": "0.8 KM",
        "wait_time": "5 MINS",
        "status": "AVAILABLE",
        "score": 76.5,
        "lat": 10.7761,
        "lng": 106.7011
      },
      {
        "id": "6801c4d5e6f7a8b900000b",
        "name": "EcoWash D7",
        "tier": "STANDARD",
        "distance": "2.3 KM",
        "wait_time": "READY",
        "status": "AVAILABLE",
        "score": 58.0,
        "lat": 10.7325,
        "lng": 106.7155
      }
    ],
    "active_booking": null
  }
}
```

> **Khi có active booking:**
```json
{
  "active_booking": {
    "id": "6801d5e6f7a8b900000c01",
    "booking_code": "WM-20260420-A3B2",
    "status": "confirmed",
    "garage_id": "6801c4d5e6f7a8b900000a",
    "service_type_code": "wash_premium",
    "price": 150000,
    "requested_time": "2026-04-20T09:00:00"
  }
}
```

> **Mapping `finish_degradation`:** giá trị âm = bề mặt xe đang xuống cấp (Phase 3 Intelligence tính thực, hiện tại dùng công thức `~0.85% per day` từ ngày rửa cuối).
> 
> **Mapping `tier`:** `1=BASIC`, `2=STANDARD`, `3=PRO`, `4=ELITE`

---

## 3. Network Map — Nearby Garages

> Phục vụ `CustomerMap.tsx` dùng Leaflet.

### GET `/customer/nearby`

🌐 **Public** — không cần cookie.

**Query Params:**

| Param | Type | Required | Default | Mô tả |
|---|---|---|---|---|
| `lat` | float | ✅ | — | Vĩ độ |
| `lng` | float | ✅ | — | Kinh độ |
| `radius_km` | float | optional | `10` | Bán kính tìm (tối đa 50km) |

**Request:**
```
GET /customer/nearby?lat=10.7761&lng=106.7011&radius_km=10
```

**Response:**
```json
{
  "status": "ok",
  "message": "Garages retrieved successfully",
  "data": {
    "garages": [
      {
        "id": "6801c4d5e6f7a8b900000a",
        "name": "AutoSpa Quận 3",
        "lat": 10.7834,
        "lng": 106.6856,
        "score": 76.5,
        "distance": "0.8km",
        "tier": "PRO",
        "active": true
      },
      {
        "id": "6801c4d5e6f7a8b900000b",
        "name": "EcoWash D7",
        "lat": 10.7325,
        "lng": 106.7155,
        "score": 58.0,
        "distance": "5.1km",
        "tier": "STANDARD",
        "active": false
      }
    ]
  }
}
```

> `active = true` khi garage `is_accepting_bookings: true`.  
> `distance` tính theo đường chim bay từ coords user → garage.

---

## 4. Garage Detail Portal

> Phục vụ `GarageDetail.tsx`. Aggregated endpoint gộp: info + amenities + services + capacity chart.

### GET `/customer/garages/{garage_id}/portal`

🌐 **Public** — không cần cookie.

**Path Params:** `garage_id` — MongoDB ObjectId (24 ký tự hex)

**Request:**
```
GET /customer/garages/6801c4d5e6f7a8b900000a/portal
```

**Response:**
```json
{
  "status": "ok",
  "message": "Garage retrieved successfully",
  "data": {
    "info": {
      "name": "AutoSpa Quận 3",
      "slug": "autospa-q3",
      "tier": "PRO",
      "tier_num": 3,
      "efficiency_score": 7.6,
      "is_verified": true,
      "is_accepting_bookings": true,
      "address": {
        "street": "123 Nguyễn Huệ",
        "ward": "Phường Bến Nghé",
        "district": "Quận 3",
        "city": "TP Hồ Chí Minh"
      },
      "description": "",
      "photos": [],
      "stats": {
        "total_services": 1250,
        "avg_rating": 4.3,
        "retention_rate": 0.65,
        "on_time_rate": 0.88
      },
      "metrics": {
        "equipment": 6.0,
        "process": 5.5,
        "staff": 5.0,
        "capacity": 7.0,
        "reliability": 4.8
      }
    },
    "amenities": ["wifi", "waiting_area", "coffee"],
    "services": [
      {
        "id": "6801e6f7a8b900000d01",
        "code": "wash_premium",
        "name": "Rửa xe Premium",
        "desc": "Rửa ngoại thất + nội thất cơ bản",
        "category": "wash",
        "time_mins": 30,
        "price_vnd": 150000,
        "is_popular": true
      },
      {
        "id": "6801e6f7a8b900000d02",
        "code": "interior",
        "name": "Vệ sinh nội thất",
        "desc": "Hút bụi, lau nội thất, khử mùi",
        "category": "interior",
        "time_mins": 60,
        "price_vnd": 250000,
        "is_popular": false
      },
      {
        "id": "6801e6f7a8b900000d03",
        "code": "detailing",
        "name": "Detailing chuyên sâu",
        "desc": "Làm mới ngoại thất chuyên sâu",
        "category": "detailing",
        "time_mins": 180,
        "price_vnd": 800000,
        "is_popular": true
      }
    ],
    "capacity_load": [
      { "time": "07:00", "load_percent": 15 },
      { "time": "08:00", "load_percent": 35 },
      { "time": "09:00", "load_percent": 50 },
      { "time": "10:00", "load_percent": 65 },
      { "time": "11:00", "load_percent": 75 },
      { "time": "12:00", "load_percent": 90 },
      { "time": "13:00", "load_percent": 85 },
      { "time": "14:00", "load_percent": 80 },
      { "time": "15:00", "load_percent": 70 },
      { "time": "16:00", "load_percent": 60 },
      { "time": "17:00", "load_percent": 55 },
      { "time": "18:00", "load_percent": 45 },
      { "time": "19:00", "load_percent": 30 },
      { "time": "20:00", "load_percent": 20 }
    ]
  }
}
```

> **`capacity_load`:** Nếu có đủ dữ liệu thực (≥5 capacity snapshots cùng day-of-week), BE trả dữ liệu thực aggregate theo giờ. Nếu chưa có data, BE trả pattern điển hình (như trên).
> 
> **`efficiency_score`:** Trên thang 0–10 (BE lưu 0–100 trong DB, tự chia cho FE).
> 
> **`is_popular`:** `true` khi `code` thuộc `["wash_premium", "detailing"]`.

---

## 5. Bookings

### GET `/customer/bookings`

🔒 Yêu cầu cookie.

**Query Params:**

| Param | Type | Required | Mô tả |
|---|---|---|---|
| `status` | string | optional | Filter theo status (case-insensitive) |

**Status values:** `pending` · `confirmed` · `customer_arriving` · `customer_arrived` · `in_service` · `completed` · `cancelled_by_customer` · `cancelled_by_garage` · `no_show`

**Request:**
```
GET /customer/bookings
GET /customer/bookings?status=completed
```

**Response:**
```json
{
  "status": "ok",
  "message": "Bookings retrieved successfully",
  "data": [
    {
      "id": "6801d5e6f7a8b900000c01",
      "booking_code": "WM-20260420-A3B2",
      "tenant_id": "autospa-q3",
      "customer_id": "6801a2f3c1d4e5b6a7890001",
      "garage_id": "6801c4d5e6f7a8b900000a",
      "vehicle_id": "6801b3c4d5e6f7a8b9000001",
      "service_type_code": "wash_premium",
      "price": 150000,
      "requested_time": "2026-04-20T09:00:00",
      "estimated_arrival": "2026-04-20T09:00:00",
      "status": "completed",
      "timestamps": {
        "created_at": "2026-04-20T08:15:00",
        "confirmed_at": "2026-04-20T08:20:00",
        "customer_departed_at": "2026-04-20T08:40:00",
        "customer_arrived_at": "2026-04-20T08:55:00",
        "service_started_at": "2026-04-20T09:02:00",
        "service_completed_at": "2026-04-20T09:38:00",
        "customer_confirmed_at": null,
        "cancelled_at": null
      },
      "matching_context": {
        "match_score": 87.5,
        "estimated_travel_minutes": 15
      },
      "feedback": {
        "rating": 5,
        "quick_feedback": "thumbs_up",
        "comment": "Rất hài lòng!"
      },
      "cancellation_reason": "",
      "cancelled_by": ""
    }
  ]
}
```

---

### GET `/customer/bookings/{booking_id}`

🔒 Yêu cầu cookie. Trả về chi tiết 1 booking.

**Response:** Cùng schema với 1 item trong list bookings ở trên.

---

### GET `/customer/bookings/{booking_id}/tracking`

🔒 Yêu cầu cookie. Phục vụ `BookingTracker.tsx`.

**Response:**
```json
{
  "status": "ok",
  "data": {
    "booking": {
      "id": "6801d5e6f7a8b900000c01",
      "booking_code": "WM-20260420-A3B2",
      "status": "in_service",
      "service_type_code": "wash_premium",
      "price": 150000,
      "garage_id": "6801c4d5e6f7a8b900000a"
    },
    "timeline": [
      {
        "status": "CREATED",
        "timestamp": "2026-04-20T08:15:00",
        "description": "Yêu cầu đã được hệ thống ghi nhận"
      },
      {
        "status": "CONFIRMED",
        "timestamp": "2026-04-20T08:20:00",
        "description": "Gara đã chấp nhận lịch hẹn"
      },
      {
        "status": "CUSTOMER_DEPARTING",
        "timestamp": "2026-04-20T08:40:00",
        "description": "Khách hàng đang trên đường đến"
      },
      {
        "status": "CUSTOMER_ARRIVED",
        "timestamp": "2026-04-20T08:55:00",
        "description": "Khách hàng đã đến gara"
      },
      {
        "status": "IN_SERVICE",
        "timestamp": "2026-04-20T09:02:00",
        "description": "Đang tiến hành dịch vụ"
      }
    ]
  }
}
```

> Timeline chỉ chứa các bước đã xảy ra (có timestamp). Bước chưa xảy ra không xuất hiện.  
> FE render bằng cách check `timeline[i].status` để highlight step hiện tại.

---

### POST `/bookings/create`

🔒 Yêu cầu cookie. Đặt lịch mới.

**Request:**
```json
{
  "garage_id": "6801c4d5e6f7a8b900000a",
  "service_type_code": "wash_premium",
  "requested_time": "2026-04-21T09:00:00",
  "vehicle_id": "6801b3c4d5e6f7a8b9000001",
  "matching_context": {
    "match_score": 87.5,
    "was_top_recommendation": true
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Booking created successfully",
  "data": {
    "id": "6801d5e6f7a8b900000c02",
    "booking_code": "WM-20260421-X9Y1",
    "status": "pending",
    "price": 150000,
    "requested_time": "2026-04-21T09:00:00"
  }
}
```

**Errors:**
- `409` — Slot congested: `"Garage is not accepting bookings"` / `"No slot available at requested time"`
- `409` — Service chưa có tại garage: `"Service not offered at this garage"`
- `409` — Redis lock contention: `"Slot contention — please retry"`

---

## 6. Vehicle Management

### GET `/customer/vehicles`

🔒 Yêu cầu cookie.

**Response:**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "6801b3c4d5e6f7a8b9000001",
      "owner_user_id": "6801a2f3c1d4e5b6a7890001",
      "license_plate": "51K-123.45",
      "brand": "VinFast",
      "model": "VF8",
      "year": 2023,
      "color": "Black",
      "vehicle_type": "premium",
      "body_type": "suv",
      "size_class": "large",
      "minimum_garage_tier": 2,
      "vetc_linked": false,
      "is_default": true,
      "is_active": true
    },
    {
      "id": "6801b3c4d5e6f7a8b9000002",
      "license_plate": "51A-99999",
      "brand": "Mercedes-Benz",
      "model": "S-Class",
      "year": 2022,
      "color": "White",
      "vehicle_type": "luxury",
      "body_type": "sedan",
      "size_class": "large",
      "minimum_garage_tier": 3,
      "vetc_linked": false,
      "is_default": false,
      "is_active": true
    }
  ]
}
```

---

### POST `/customer/vehicles`

🔒 Yêu cầu cookie.

**Request:**
```json
{
  "license_plate": "51B-12345",
  "brand": "Toyota",
  "model": "Camry",
  "year": 2021,
  "color": "Silver",
  "vehicle_type": "standard",
  "body_type": "sedan",
  "size_class": "medium",
  "is_default": false
}
```

> **`vehicle_type` values:** `standard` · `premium` · `luxury` · `super`  
> **`body_type` values:** `sedan` · `suv` · `hatchback` · `truck` · `van` · `coupe`  
> **`size_class` values:** `compact` · `medium` · `large` · `xl`

**Response:** `201 Created`
```json
{
  "status": "ok",
  "message": "Vehicle created successfully",
  "data": {
    "id": "6801b3c4d5e6f7a8b9000003",
    "license_plate": "51B-12345",
    "brand": "Toyota",
    "model": "Camry",
    "minimum_garage_tier": 1,
    "is_default": false,
    "is_active": true
  }
}
```

**Errors:**
- `409` — `"License plate already registered"`

---

### PUT `/customer/vehicles/{vehicle_id}/default`

🔒 Yêu cầu cookie. Đặt xe làm mặc định (auto bỏ default của xe cũ).

**Request:** *(no body)*
```
PUT /customer/vehicles/6801b3c4d5e6f7a8b9000002/default
```

**Response:**
```json
{
  "status": "ok",
  "message": "Vehicle set as default successfully"
}
```

---

## Booking State Machine

Booking trải qua các trạng thái theo thứ tự:

```
pending → confirmed → customer_arriving → customer_arrived → in_service → completed
                ↘ cancelled_by_customer
                ↘ cancelled_by_garage
                ↘ no_show
```

**Action endpoints** (POST, đã có sẵn):

| Action | Endpoint | Auth |
|---|---|---|
| Tạo booking | `POST /bookings/create` | Customer |
| Gara xác nhận | `POST /bookings/confirm` | Garage staff |
| Customer "Đang đến" | `POST /bookings/depart` | Customer |
| Customer check-in | `POST /bookings/checkin` | Customer |
| Bắt đầu rửa | `POST /bookings/start_service` | Garage staff |
| Hoàn thành | `POST /bookings/complete` | Garage staff |
| Hủy | `POST /bookings/cancel` | Customer hoặc Garage |
| Gửi feedback | `POST /bookings/feedback` | Customer |

---

## Lưu ý cho FE Dev

### Fetch pattern chuẩn

```typescript
const API = 'http://localhost:8000'

// Luôn dùng credentials: 'include' để gửi HttpOnly cookie
const apiFetch = (path: string, options?: RequestInit) =>
  fetch(`${API}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
  })

// Example: Lấy dashboard
const res = await apiFetch('/customer/dashboard-summary?lat=10.77&lng=106.70')
const { data } = await res.json()
// data.vehicle_diagnostics, data.smart_recommendations, data.active_booking
```

### Tier label mapping

```typescript
const TIER_LABELS: Record<number, string> = {
  1: 'BASIC', 2: 'STANDARD', 3: 'PRO', 4: 'ELITE'
}
// BE đã map sẵn trong response — /customer/nearby và /customer/dashboard-summary
// trả label string trực tiếp, không cần map lại ở FE
```

### Booking status mapping cho UI

```typescript
const STATUS_MAP = {
  pending:              { label: 'Chờ xác nhận', color: 'yellow' },
  confirmed:            { label: 'Đã xác nhận',  color: 'blue' },
  customer_arriving:    { label: 'Đang đến',      color: 'blue' },
  customer_arrived:     { label: 'Đã đến',        color: 'green' },
  in_service:           { label: 'Đang rửa xe',   color: 'blue' },
  completed:            { label: 'Hoàn thành',    color: 'green' },
  cancelled_by_customer:{ label: 'Đã hủy',        color: 'red' },
  cancelled_by_garage:  { label: 'Gara hủy',      color: 'red' },
  no_show:              { label: 'Không đến',     color: 'gray' },
}
```

---

## Performance Notes

- `GET /customer/nearby` — nên cache phía FE ~30 giây (kết quả thay đổi chậm)
- `GET /customer/garages/{id}/portal` — **nên cache phía BE bằng Redis** (lượt đọc cao, data ít thay đổi). BE sẽ implement Redis cache trong Phase tiếp theo.
- `GET /customer/dashboard-summary` — gọi mỗi lần user mở app, không cache (active booking cần real-time).
- `GET /customer/bookings/{id}/tracking` — có thể poll mỗi 10s khi đang `in_service`.
