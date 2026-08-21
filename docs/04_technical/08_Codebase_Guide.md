# 08. Hướng dẫn mã nguồn cho dev mới

Có gì trong repo, chỗ nào dùng lại được, chỗ nào phải sửa, và sửa theo thứ tự nào

Phiên bản: 1.0
Ngày: 21/08/2026
Đối tượng đọc: lập trình viên mới tham gia dự án
Tài liệu liên quan: [09. Nguyên tắc thiết kế giao diện](09_Frontend_Design_System.md)

---

## Mục lục

1. [Đọc tài liệu này để làm gì](#1-đọc-tài-liệu-này-để-làm-gì)
2. [Chạy dự án](#2-chạy-dự-án)
3. [Quy ước tên gọi và bản đồ nghiệp vụ](#3-quy-ước-tên-gọi-và-bản-đồ-nghiệp-vụ)
4. [Backend](#4-backend)
5. [Frontend](#5-frontend)
6. [Xác thực và phân quyền, đầu cuối](#6-xác-thực-và-phân-quyền-đầu-cuối)
7. [Những gì đã được dọn](#7-những-gì-đã-được-dọn)
8. [Nợ kỹ thuật và lỗi đã phát hiện](#8-nợ-kỹ-thuật-và-lỗi-đã-phát-hiện)
9. [Thứ tự refactor đề xuất](#9-thứ-tự-refactor-đề-xuất)
10. [Quy ước để không tạo lại rác cũ](#10-quy-ước-để-không-tạo-lại-rác-cũ)

---

## 1. Đọc tài liệu này để làm gì

Repo này không phải dự án trống. Nó là một nền tảng đã chạy được, gồm xác thực bằng JWT trong cookie, phân quyền theo vai trò, kiến trúc đa chủ thể, ba màn hình theo vai trò ở frontend, và một số module nghiệp vụ nền như quản lý điểm phục vụ, đặt chỗ, công suất, ghép nối và chấm điểm.

Phần khung này được giữ lại có chủ đích. Việc của bạn không phải viết lại từ đầu, mà là:

Một, hiểu khung có sẵn để dùng lại. Hai, biết module nào là khung dùng chung và module nào là nghiệp vụ cần đổi cho bài toán bãi đỗ xe. Ba, biết chỗ nào đang là dữ liệu mẫu hoặc màn hình trống để không tưởng là tính năng thật.

Ba mức tái sử dụng dùng xuyên suốt tài liệu:

| Mức | Nghĩa là gì |
|---|---|
| Giữ nguyên | Là khung dùng chung, không phụ thuộc nghiệp vụ. Sửa chỉ khi có lý do kỹ thuật rõ ràng |
| Đổi nghiệp vụ | Cấu trúc dùng lại được, nhưng tên trường, dữ liệu mẫu và logic bên trong phải chỉnh theo bài toán bãi đỗ xe |
| Viết lại | Chỉ dùng làm tham khảo về cách tổ chức, phần logic sẽ viết mới |

---

## 2. Chạy dự án

### 2.1. Yêu cầu môi trường

MongoDB đang chạy và truy cập được. Redis không bắt buộc, hệ thống tự chạy tiếp khi không có Redis nhưng mất phần cache và khoá phân tán. Python 3.11 trở lên, dùng uv. Node 18 trở lên.

### 2.2. Backend

```bash
cd backend
cp .env.sample .env          # sửa MONGO_URI, JWT_SECRET_KEY, SUPER_ADMIN_PASSWORD
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Khi khởi động, backend tự làm bốn việc trong `main.py`: kết nối MongoDB, tạo index cho toàn bộ collection, seed tài khoản super admin theo biến môi trường, seed danh mục dịch vụ mẫu, và kết nối Redis theo kiểu tốt nhất có thể.

Tài liệu API tự sinh ở `http://localhost:8000/docs`. Kiểm tra sống ở `/health`.

Tài khoản super admin lấy từ `SUPER_ADMIN_USERNAME` và `SUPER_ADMIN_PASSWORD` trong file `.env`. Nếu để trống mật khẩu thì bước seed sẽ bỏ qua.

### 2.3. Frontend

```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173
npm run build                # chạy tsc rồi build, hiện tại pass sạch
```

Địa chỉ backend đặt trong `src/config/app.ts`, override bằng biến `VITE_API_BASE`.

### 2.4. Dữ liệu mẫu và kiểm thử

Sinh dữ liệu mẫu để có gì mà xem trên giao diện:

```bash
cd backend
uv run python scripts/seed_data.py            # thêm mới, bỏ qua bản ghi đã có
uv run python scripts/seed_data.py --reset    # xoá dữ liệu cũ rồi seed lại
```

Script tạo 30 bãi đỗ tại Quận 1, 3, 5, 7 với toạ độ thực tại Thành phố Hồ Chí Minh, kèm chủ thể và chủ bãi tương ứng, 6 khách hàng có xe, khoảng 120 lượt đặt trải trong 90 ngày, và 4 tuần snapshot công suất theo giờ để các biểu đồ có dữ liệu. Tên bãi, số liệu và đánh giá đều là dữ liệu giả, chỉ toạ độ là thật.

Tài khoản sau khi seed: chủ bãi `owner_q1_01` tới `owner_q7_08` với mật khẩu `GarageOwner@2026`, khách hàng `customer_an` và năm tài khoản khác với mật khẩu `Customer@2026`. Đây là mật khẩu dữ liệu mẫu, không dùng ở môi trường thật.

Chạy kiểm thử:

```bash
cd backend
uv run pytest test -q
```

Bộ kiểm thử hiện có 113 test và đang pass hết. Nó phủ xác thực, chủ thể, người dùng, bãi, xe, dịch vụ theo bãi, danh mục dịch vụ, luồng đặt chỗ, công suất, và các hàm chấm điểm của engine ghép nối. Test dùng database riêng tên `parkinghub_test` và tự xoá sau khi chạy, nên không ảnh hưởng dữ liệu phát triển.

Bộ kiểm thử này là lưới an toàn khi refactor. Sửa xong một module thì chạy lại, đừng đợi tới cuối.

### 2.5. Lưu ý về cơ sở dữ liệu

Tên database mặc định đã đổi thành `parkinghub`. Dữ liệu thử nghiệm cũ nếu có vẫn nằm trong database tên cũ và không bị xoá. Muốn dùng lại thì đổi `MONGO_DB` trong `.env`, nhưng khuyến nghị bắt đầu bằng database mới cho sạch.

---

## 3. Quy ước tên gọi và bản đồ nghiệp vụ

Mã nguồn hiện tại dùng từ `garage` cho điểm phục vụ. Trong dự án này, `garage` được đọc là **bãi đỗ xe**. Việc đổi tên biến và collection trên toàn hệ thống là một refactor lớn, nên nó được tách riêng thành một bước có kiểm soát ở mục 9, không làm rải rác.

Bản đồ đọc hiểu, dùng ngay khi đọc code hôm nay:

| Tên trong code | Đọc là | Ghi chú |
|---|---|---|
| `garage`, `GarageModel`, collection `garages` | Bãi đỗ xe | Trường `tier`, `capacity`, `location`, `operating_hours` dùng lại gần như trọn vẹn |
| `garage_service`, `GarageServiceModel` | Dịch vụ mà một bãi cung cấp và giá của bãi đó | Ví dụ gửi theo giờ, gửi qua đêm, gói tháng |
| `service_type`, `ServiceTypeModel` | Danh mục dịch vụ cấp nền tảng | Đang là dữ liệu mẫu, xem mục 4.4 |
| `booking`, `BookingModel` | Lượt đặt chỗ, và về sau là lượt gửi xe | Cần mở rộng từ đặt theo lượt sang đặt theo khoảng thời gian |
| `capacity` | Công suất và tình trạng chỗ trống | Sẽ là nơi nhận dữ liệu từ camera đếm chỗ |
| `matching` | Engine gợi ý bãi phù hợp | Giữ nguyên tư duy, đổi biến đầu vào |
| `vehicle`, `VehicleModel` | Xe của người dùng | Có `license_plate` unique, dùng được cho nhận diện biển số về sau |
| `tenant`, `TenantModel` | Chủ thể vận hành, mỗi chủ bãi là một tenant | Khung đa chủ thể, giữ nguyên |
| `tier` 1 tới 4 | Cấp của bãi | Ý nghĩa cấp sẽ đổi theo tài liệu 05, cấu trúc giữ nguyên |

---

## 4. Backend

Stack: FastAPI, MongoDB qua motor và umongo, Redis, pydantic-settings, JWT trong HttpOnly cookie.

### 4.1. Cấu trúc thư mục

```
backend/
  main.py                     Điểm khởi động: lifespan, index, middleware auth, CORS, health
  pyproject.toml              Khai báo dependency, quản lý bằng uv
  .env.sample                 Mẫu biến môi trường
  app/
    core/config.py            Toàn bộ cấu hình đọc từ .env
    core/logging_config.py    Cấu hình log ra console và file
    db/mongo.py               Kết nối motor, khởi tạo umongo instance
    db/base_model.py          TenantAwareDocument, lớp cha có cách ly đa chủ thể
    api/
      shared/                 api_response, exceptions, schemas, tool chuyển đổi
      auth/                   Đăng nhập, JWT, RBAC, dependencies
      tenant/  user/          Quản trị chủ thể và người dùng
      garage/  vehicle/       Nghiệp vụ điểm phục vụ và xe
      service_type/           Danh mục dịch vụ cấp nền tảng
      garage_service/         Dịch vụ và giá theo từng bãi
      booking/                Máy trạng thái đặt chỗ
      capacity/               Theo dõi và dự đoán công suất
      matching/               Engine ghép nối và các hàm chấm điểm
      search_log/             Ghi nhận truy vấn tìm kiếm
      customer/               Nhóm endpoint gộp cho app khách hàng
      garage_portal/          Nhóm endpoint gộp cho cổng chủ bãi
      main_router.py          Gom toàn bộ router
    services/
      osm/osm_client.py       Định tuyến và thời gian di chuyển, có fallback Haversine
      weather/weather_service.py  Thời tiết theo toạ độ
      shared/redis_client.py  Cache và khoá phân tán
  scripts/seed_data.py        Sinh dữ liệu mẫu cho phát triển và demo
  test/                       113 test, chạy bằng pytest, dùng database riêng
  reference/base_source_code_ref/   Bản mẫu khung code, có example_feature để tham khảo quy ước
```

### 4.2. Khung dùng chung, giữ nguyên

| File | Dòng | Vai trò | Vì sao giữ |
|---|---|---|---|
| `app/core/config.py` | 63 | Đọc toàn bộ cấu hình từ `.env` qua pydantic-settings | Không phụ thuộc nghiệp vụ. Thêm cấu hình mới thì thêm field ở đây, không đọc `os.environ` rải rác |
| `app/core/logging_config.py` | 79 | Log ra console và file theo service | Dùng được ngay |
| `app/db/mongo.py` | 58 | Khởi tạo motor client và umongo instance | Dùng được ngay |
| `app/db/base_model.py` | 263 | `TenantAwareDocument`: tự chèn `tenant_id` vào mọi truy vấn, tự set `created_at`, `created_by`, `updated_at`, `updated_by` | Đây là phần giá trị nhất của khung. Mọi model mới nên kế thừa lớp này |
| `app/api/shared/common_utils.py` | 41 | `api_response` chuẩn hoá cấu trúc response | Giữ để toàn hệ thống có một dạng response duy nhất |
| `app/api/shared/exceptions.py` | 48 | Lớp lỗi dùng chung | Giữ |
| `app/api/shared/schemas.py` | 63 | Enum `Operation`, `Resource` cho `api_response` | Thêm giá trị mới khi có resource mới |
| `app/api/shared/tool/` | 2 file | Chuyển ObjectId và chuyển múi giờ, mặc định giờ Việt Nam | Giữ |
| `app/api/auth/jwt_manager.py` | 69 | Tạo và giải mã token, set và clear cookie | Giữ |
| `app/api/auth/dependencies.py` | 84 | `get_current_user` đọc token từ cookie, trả dict user | Giữ |
| `app/api/auth/permissions.py` | 228 | Danh mục permission, bảng permission theo vai trò, `require_permission` | Giữ cơ chế, sửa danh sách vai trò và permission theo nghiệp vụ mới |
| `app/api/auth/auth_utils.py` | 298 | Xác thực, đăng ký khách, đăng ký chủ bãi kèm tạo tenant, seed super admin | Giữ, chỉnh lại phần đăng ký chủ bãi theo hồ sơ bãi đỗ |
| `app/api/auth/auth_views.py` | 142 | Endpoint đăng nhập, đăng ký, refresh, logout, me | Giữ |
| `app/api/tenant/*` | 172 | Quản lý chủ thể | Giữ |
| `app/api/user/*` | 271 | Quản lý người dùng theo tenant | Giữ |
| `app/services/osm/osm_client.py` | 213 | Gọi OSRM lấy thời gian di chuyển, cache theo Redis, fallback Haversine khi lỗi | Giữ. Đây là thành phần cần cho gợi ý theo điểm đến |
| `app/services/weather/weather_service.py` | 135 | Lấy thời tiết theo toạ độ, có cache | Giữ |
| `app/services/shared/redis_client.py` | 112 | Cache và khoá phân tán | Giữ |

### 4.3. Module nghiệp vụ, đổi theo bài toán bãi đỗ

| Module | File chính | Dòng | Hiện làm gì | Mức | Việc cần làm |
|---|---|---|---|---|---|
| `garage` | `garage_models.py` | 80 | Model điểm phục vụ: `location` dạng GeoJSON có index 2dsphere, `tier` và `tier_score`, `capacity`, `operating_hours`, `services_offered`, `current_load`, `stats` | Đổi nghiệp vụ | Đổi bộ thuộc tính sang đặc thù bãi đỗ theo tài liệu 05 mục 4: loại che chắn, giới hạn chiều cao, bảo vệ, trụ sạc, nguy cơ ngập, toạ độ cổng vào |
| `garage` | `garage_views.py`, `garage_utils.py` | 269 | CRUD, tìm quanh toạ độ, cập nhật tải hiện tại | Đổi nghiệp vụ | Giữ luồng, đổi trường. `search_nearby` dùng lại được nguyên vẹn |
| `vehicle` | 4 file | 312 | Xe của người dùng, `license_plate` unique, loại xe | Giữ nguyên | Sau này là điểm nối với nhận diện biển số |
| `service_type` | 3 file | 184 | Danh mục dịch vụ cấp nền tảng, seed tự động khi khởi động | Đổi nghiệp vụ | Dữ liệu seed hiện là bốn mục mẫu: gửi theo giờ, qua đêm, theo ngày, gói tháng. Đây là chỗ chốt lại đầu tiên khi thiết kế nghiệp vụ |
| `garage_service` | 3 file | 220 | Dịch vụ và giá theo từng bãi, unique theo cặp bãi và mã dịch vụ | Đổi nghiệp vụ | Bổ sung giá theo khung giờ và giá theo tháng |
| `booking` | `booking_models.py` | 85 | Máy trạng thái đặt chỗ, `booking_code` unique | Đổi nghiệp vụ | Mở rộng từ đặt theo lượt sang chiếm giữ theo khoảng thời gian, thêm cửa sổ giữ chỗ và thời gian chờ thêm |
| `booking` | `booking_utils.py`, `booking_views.py` | 560 | Tạo, xác nhận, bắt đầu, hoàn tất, huỷ, phản hồi, có dùng khoá phân tán để tránh trùng slot | Đổi nghiệp vụ | Giữ máy trạng thái và khoá, đổi tên trạng thái theo nghiệp vụ gửi xe |
| `capacity` | 3 file | 416 | Ghi nhận tải hiện tại, snapshot theo giờ và theo ngày trong tuần với TTL 90 ngày, dự đoán tình trạng tại thời điểm khách đến | Đổi nghiệp vụ | Đây là chỗ dữ liệu từ camera đếm chỗ sẽ đổ vào. Cấu trúc snapshot dùng lại được |
| `matching` | `matching_engine.py` | 412 | Pipeline 5 bước: lọc cứng, làm giàu đặc trưng, chấm điểm, cá nhân hoá, xếp hạng có đa dạng hoá | Đổi nghiệp vụ | Giữ pipeline. Đổi đầu vào từ thời gian phục vụ sang nhịp xe vào và xe ra |
| `matching` | `scoring.py` | 218 | Tám hàm chấm điểm độc lập và bộ trọng số theo ngữ cảnh | Giữ nguyên phần lớn | Mỗi hàm độc lập nên thay từng hàm được, không phải viết lại cả file |
| `search_log` | 2 file | 121 | Ghi truy vấn tìm kiếm, các lựa chọn đã hiển thị và lựa chọn cuối, TTL 180 ngày | Giữ nguyên | Đây là nguyên liệu cho cá nhân hoá về sau, đừng bỏ |
| `customer` | `customer_views.py` | 445 | Nhóm endpoint gộp cho app khách: dashboard, bãi gần đây, chi tiết bãi, danh sách và theo dõi lượt đặt, xe của tôi | Đổi nghiệp vụ | Đây là lớp gộp dữ liệu cho giao diện. Sửa ở đây khi đổi màn hình, không sửa ở module gốc |
| `garage_portal` | `garage_portal_utils.py` | 809 | Nhóm endpoint gộp cho cổng chủ bãi: tổng quan, công suất theo khung giờ, hàng đợi, phân tích, dịch vụ, điểm và cấp | Đổi nghiệp vụ | File lớn nhất và nhiều số liệu dẫn xuất nhất, nên đọc kỹ trước khi sửa |

### 4.4. Dữ liệu seed đang là dữ liệu mẫu

Có đúng hai chỗ seed dữ liệu khi khởi động, cả hai đều idempotent:

`app/api/auth/auth_utils.py` hàm `seed_super_admin` tạo tài khoản quản trị cấp cao nhất theo biến môi trường. Giữ nguyên.

`app/api/service_type/service_type_utils.py` hàm `seed_default_service_types` tạo bốn mục danh mục dịch vụ: `park_hourly`, `park_overnight`, `park_daily`, `park_monthly`. Đây là dữ liệu mẫu để các luồng đặt chỗ, tính giá và dashboard có gì mà chạy. Khi chốt nghiệp vụ thật, thay danh sách này. Nếu đổi mã dịch vụ thì phải sửa đồng bộ ba chỗ: bảng icon trong `garage_portal_utils.py`, cờ `is_popular` trong `customer_views.py`, và danh sách chọn trong `SmartBookingModal.tsx`.

### 4.5. Quy ước code của backend

Mỗi module nghiệp vụ có bốn file theo cùng một khuôn: `*_models.py` cho document MongoDB, `*_schemas.py` cho pydantic request và response, `*_utils.py` cho toàn bộ logic, `*_views.py` chỉ để khai báo endpoint và gọi utils. Endpoint không chứa logic. Đây là quy ước cần giữ.

Router khai báo trong file views với `prefix` riêng, rồi gom trong `app/api/main_router.py`.

Phân quyền dùng `Depends(require_permission([...]))` trong chữ ký hàm, không dùng decorator `has_permission`. Lý do đã ghi trong `permissions.py`: FastAPI không resolve đúng body pydantic khi đi qua wrapper.

Mọi response trả qua `api_response(operation=..., resource=..., data=..., message=...)`.

Mọi truy vấn dữ liệu có tính chất theo chủ thể phải truyền `current_user` để `TenantAwareDocument` chèn `tenant_id`. Bỏ `current_user` là mở đường cho rò rỉ dữ liệu giữa các chủ bãi.

Bản mẫu khung ở `backend/reference/base_source_code_ref/` có một `example_feature` viết đúng quy ước trên. Đọc nó khi cần tạo module mới.

### 4.6. Danh sách endpoint hiện có

| Nhóm | Tiền tố | Endpoint |
|---|---|---|
| Xác thực | `/auth` | `login`, `register`, `register-garage`, `refresh`, `logout`, `me` |
| Chủ thể | `/tenant` | `get_all`, `get_by_id`, `update` |
| Người dùng | `/user` | `get_all`, `get_by_id`, `create`, `update`, `delete` |
| Bãi | `/garage` | `get_all`, `search_nearby`, `get_by_id`, `update`, `update_capacity` |
| Xe | `/vehicle` | `get_all`, `get_by_id`, `create`, `update`, `delete` |
| Danh mục dịch vụ | `/service-types` | `get_all`, `get_by_code` |
| Dịch vụ theo bãi | `/garage-services` | `list_by_garage`, `upsert`, `remove` |
| Đặt chỗ | `/bookings` | `create`, `confirm`, `depart`, `checkin`, `start_service`, `complete`, `cancel`, `feedback`, `get_all`, `get_by_id` |
| Công suất | `/capacity` | `current_and_predicted`, `update_load` |
| Ghép nối | `/match` | `search`, `feedback` |
| Cổng khách hàng | `/customer` | `dashboard-summary`, `nearby`, `garages/{id}/portal`, `bookings`, `bookings/{id}`, `bookings/{id}/tracking`, `vehicles`, `vehicles/{id}/default` |
| Cổng chủ bãi | `/garage-portal` | `dashboard/overview`, `dashboard/capacity`, `queue`, `queue/bookings/{id}`, `analytics`, `services`, `services/{id}`, `score` |

Lưu ý về hai phong cách API đang tồn tại song song. Các module lõi dùng kiểu RPC, tức là `POST /garage/get_all`. Hai nhóm cổng giao diện dùng kiểu REST, tức là `GET /customer/bookings`. Chọn một phong cách và thống nhất là một việc trong danh sách nợ kỹ thuật ở mục 8.

---

## 5. Frontend

Stack: React 18, TypeScript, Vite, Tailwind CSS 4, React Router 6, Leaflet cho bản đồ, lucide-react cho icon.

### 5.1. Cấu trúc thư mục

```
frontend/
  index.html
  vite.config.ts              Alias @ trỏ vào src
  src/
    main.tsx                  Bọc App trong AuthProvider
    App.tsx                   Toàn bộ định tuyến và bảo vệ route theo vai trò
    index.css                 Design token và lớp typography, xem tài liệu 09
    config/app.ts             Tên sản phẩm, tagline, địa chỉ API. Nhận diện tập trung ở đây
    components/Brand.tsx      Wordmark dùng chung, hiện là chữ, chưa dùng ảnh
    components/ui/            button, card, badge theo kiểu shadcn
    components/SmartBookingModal.tsx   Modal đặt chỗ nhiều bước
    layouts/                  CustomerLayout, GarageLayout, AdminLayout
    pages/auth/               LoginPage
    pages/customer/           7 trang cho khách hàng
    pages/garage/             5 trang cho chủ bãi
    pages/admin/              1 trang, đang là chỗ trống
    services/api.ts           Toàn bộ lời gọi API và kiểu dữ liệu
    services/auth-context.tsx Context đăng nhập
    services/utils.ts         cn, gộp class Tailwind
```

### 5.2. Ba màn hình theo vai trò

Định tuyến khai báo trong `App.tsx`. Mỗi nhóm route có một layout riêng và danh sách vai trò được phép.

| Nhóm | Đường dẫn gốc | Layout | Vai trò được phép |
|---|---|---|---|
| Khách hàng | `/app` | `CustomerLayout` | `customer` |
| Chủ bãi | `/garage` | `GarageLayout` | `garage_owner`, `garage_manager`, `garage_staff` |
| Quản trị nền tảng | `/admin` | `AdminLayout` | `super_admin`, `platform_ops` |

Vào `/` thì `RoleRedirect` đọc vai trò và đưa về đúng nhóm. Chưa đăng nhập thì về `/login`. Đăng nhập rồi mà vai trò không thuộc nhóm thì cũng bị đẩy về `/login`, đây là một điểm cần sửa vì gây vòng lặp khó hiểu, xem mục 8.

### 5.3. Bảng trang

| Trang | File | Dòng | Route | API đang gọi | Mức |
|---|---|---|---|---|---|
| Đăng nhập và đăng ký | `pages/auth/LoginPage.tsx` | 193 | `/login` | `authApi.login`, `authApi.register` | Giữ nguyên bố cục, chữ trong trang là chữ tạm |
| Trang chủ khách | `pages/customer/CustomerHome.tsx` | 206 | `/app` | `customerApi.dashboardSummary` | Đổi nghiệp vụ |
| Bản đồ | `pages/customer/CustomerMap.tsx` | 204 | `/app/map` | `customerApi.nearby` | Đổi nghiệp vụ, dùng Leaflet, phần khung bản đồ giữ được |
| Chi tiết bãi | `pages/customer/GarageDetail.tsx` | 249 | `/app/garages/:id` | `customerApi.garagePortal` | Đổi nghiệp vụ |
| Danh sách lượt đặt | `pages/customer/CustomerBookings.tsx` | 120 | `/app/bookings` | `customerApi.bookings` | Đổi nghiệp vụ |
| Theo dõi lượt đặt | `pages/customer/BookingTracker.tsx` | 129 | `/app/bookings/:id` | `customerApi.bookingTracking` | Đổi nghiệp vụ, dòng thời gian trạng thái dùng lại được |
| Xe của tôi | `pages/customer/CustomerVehicles.tsx` | 127 | `/app/vehicles` | `customerApi.vehicles`, `addVehicle`, `setDefaultVehicle` | Giữ nguyên |
| Hồ sơ khách | `pages/customer/CustomerProfile.tsx` | 1 | `/app/profile` | Không | Chỗ trống, chưa làm |
| Tổng quan chủ bãi | `pages/garage/GarageDashboard.tsx` | 256 | `/garage` | `garageApi.dashboardOverview`, `dashboardCapacity`, `queue` | Đổi nghiệp vụ |
| Hàng đợi | `pages/garage/GarageQueue.tsx` | 266 | `/garage/queue` | `garageApi.queue`, `updateBookingStatus` | Đổi nghiệp vụ |
| Phân tích | `pages/garage/GarageAnalytics.tsx` | 243 | `/garage/analytics` | `garageApi.analytics` | Đổi nghiệp vụ |
| Dịch vụ và giá | `pages/garage/GarageServices.tsx` | 164 | `/garage/services` | `garageApi.services` và CRUD | Đổi nghiệp vụ |
| Điểm và cấp | `pages/garage/GarageScore.tsx` | 219 | `/garage/score` | `garageApi.score` | Đổi nghiệp vụ |
| Quản trị nền tảng | `pages/admin/AdminDashboard.tsx` | 1 | `/admin` | Không | Chỗ trống, chưa làm |

Toàn bộ trang đều gọi API thật, không có dữ liệu giả cắm cứng trong trang. Hai trang chỗ trống là `AdminDashboard` và `CustomerProfile`, mỗi trang một dòng.

### 5.4. Lớp gọi API

`services/api.ts` là file duy nhất được phép biết địa chỉ backend. Cấu trúc gồm ba phần:

Phần một, `apiFetch` bọc `fetch` với `credentials: 'include'` để cookie đi kèm, và tự set `Content-Type`.

Phần hai, các `interface` mô tả dữ liệu trả về, ví dụ `User`, `NearbyGarage`, `Booking`, `MatchResult`. Đây là hợp đồng giữa backend và frontend, sửa backend thì sửa cả đây.

Phần ba, bốn nhóm hàm gọi API: `authApi`, `customerApi`, `matchingApi`, `garageApi`. Thêm endpoint mới thì thêm vào nhóm tương ứng, không gọi `fetch` trực tiếp trong trang.

Ngoài ra file có hai bảng ánh xạ để hiển thị: `BOOKING_STATUS_MAP` và `TIER_COLOR`. Đây là chỗ đổi nhãn trạng thái khi nghiệp vụ đổi.

### 5.5. Nhận diện thương hiệu

Toàn bộ nhận diện gom về hai chỗ, không rải rác trong trang:

`src/config/app.ts` giữ `APP_NAME`, `APP_TAGLINE`, `API_BASE`. Đổi tên sản phẩm thì sửa đúng file này.

`src/components/Brand.tsx` là wordmark dùng chung, hiện render chữ. Khi có logo chính thức, thay phần bên trong bằng thẻ `img` và mọi nơi dùng `Brand` sẽ đổi theo.

---

## 6. Xác thực và phân quyền, đầu cuối

### 6.1. Luồng đăng nhập

```
Người dùng nhập username và password ở LoginPage
        |
POST /auth/login
        |
Backend xác thực, tạo access token và refresh token
Set hai HttpOnly cookie: access_token, refresh_token
Trả về thông tin user, gồm role và permissions
        |
FE lưu user trong AuthProvider (bộ nhớ, không dùng localStorage)
        |
RoleRedirect đưa về /app, /garage hoặc /admin theo role
        |
Mỗi request sau đó tự mang cookie nhờ credentials: 'include'
```

Trên backend có hai lớp chặn. Lớp thứ nhất là `AuthMiddleware` trong `main.py`, chặn mọi đường dẫn không nằm trong danh sách công khai `PUBLIC_PATH_PREFIXES` khi không có access token hợp lệ. Lớp thứ hai là `Depends(require_permission([...]))` ở từng endpoint, kiểm tra permission cụ thể.

Token nằm trong cookie HttpOnly nên JavaScript không đọc được. Đây là thiết kế có chủ đích, đừng chuyển sang localStorage.

### 6.2. Vai trò hiện có

Định nghĩa trong `app/api/auth/permissions.py`, bảng `ROLE_PERMISSIONS`.

| Vai trò | Ý nghĩa hiện tại | Đọc lại cho dự án này |
|---|---|---|
| `super_admin` | Toàn quyền, bỏ qua mọi kiểm tra, `tenant_id` bằng `super_admin` | Giữ |
| `platform_ops` | Vận hành nền tảng: xem và sửa chủ thể, xem bãi, xem báo cáo | Giữ |
| `garage_owner` | Chủ điểm phục vụ, quản lý nhân sự trong chủ thể của mình | Chủ bãi đỗ |
| `garage_manager` | Quản lý ca, không quản lý nhân sự | Quản lý bãi |
| `garage_staff` | Nhân viên, chỉ xem và cập nhật lượt đặt cùng công suất | Bảo vệ tại bãi |
| `customer` | Khách hàng | Người lái xe |
| `fleet_manager` | Quản lý đội xe | Giữ, dùng cho khách doanh nghiệp |

Thêm vai trò mới cần làm ba việc: thêm vào `ROLE_PERMISSIONS`, thêm module và permission tương ứng nếu có nghiệp vụ mới, và thêm vai trò đó vào `allowedRoles` của route tương ứng trong `App.tsx`.

### 6.3. Cách ly đa chủ thể

`TenantAwareDocument` trong `app/db/base_model.py` là cơ chế chính. Khi gọi `Model.find(query, current_user=current_user)`, lớp cha tự chèn điều kiện `tenant_id` theo user. Super admin thấy tất cả. User có `allowed_tenant_ids` thấy nhiều chủ thể con, dùng cho trường hợp một đơn vị quản lý nhiều bãi.

Đây là phần cần cẩn thận nhất khi viết module mới. Quên truyền `current_user` là mở đường cho một chủ bãi đọc dữ liệu của chủ bãi khác.

---

## 7. Những gì đã được dọn

Lần dọn này chỉ xử lý nhận diện thương hiệu cũ, dữ liệu mẫu mang nghiệp vụ cũ, và rác của bản mẫu khởi tạo. Không xoá module nghiệp vụ nào, không đổi kiến trúc.

| Việc | Chi tiết |
|---|---|
| Gom nhận diện về một chỗ | Thêm `src/config/app.ts` và `src/components/Brand.tsx`. Mọi nơi trước đây nhúng tên và logo trực tiếp giờ dùng hai file này |
| Bỏ file logo cũ | Xoá file logo nhận diện cũ và mọi tham chiếu trong `LoginPage`, `CustomerLayout`, `GarageLayout` |
| Bỏ tên sản phẩm cũ trong code | Đổi ở `main.py`, `config.py`, `permissions.py`, `auth_utils.py`, `osm_client.py`, `pyproject.toml`, `.env`, `.env.sample`, `index.html`, `package.json`, `api.ts`, ba layout, `LoginPage` |
| Đổi dữ liệu mẫu danh mục dịch vụ | Từ danh mục dịch vụ rửa xe và chăm sóc xe sang bốn mục mẫu về gửi xe. Đồng bộ cả bảng icon ở backend và danh sách chọn ở frontend |
| Đổi tên trường lệch nghiệp vụ | `avg_wash_time_seconds` thành `avg_service_time_seconds`, sửa đồng bộ backend và frontend |
| Bỏ chữ và số liệu bịa trong giao diện | Xoá dòng khoe số thành viên, ảnh đại diện lấy từ dịch vụ ngoài trong trang đăng nhập, ảnh nền lấy từ dịch vụ ngoài, các nhãn cứng như hạng thành viên và chức danh không có thật |
| Bỏ rác bản mẫu Vite | Xoá `src/App.css`, `src/assets/react.svg` vì không nơi nào dùng |
| Bỏ tài liệu sản phẩm cũ trong frontend | Xoá thư mục `frontend/.docs`. Phần nguyên tắc thiết kế được viết lại trong tài liệu 09 |
| Viết lại dữ liệu mẫu trong `scripts/seed_data.py` | 30 điểm dịch vụ theo nghiệp vụ cũ được đổi thành 30 bãi đỗ xe, giữ nguyên toạ độ thực và toàn bộ cấu trúc script. Tên bãi sinh theo tên đường và quận, tên đăng nhập chủ bãi đổi thành `owner_q1_01` và tương tự, email đổi sang `example.com`, bảng giá và trọng số chọn dịch vụ đổi theo bốn mục dịch vụ mới, các câu đánh giá mẫu viết lại theo trải nghiệm gửi xe |
| Cập nhật bộ kiểm thử | Đổi tên database test, đổi mã dịch vụ trong test, đổi assert tên ứng dụng sang đọc từ cấu hình. Sau khi sửa, cả 113 test vẫn pass |
| Sửa đường dẫn cổng chủ bãi bị lệch | Backend mount cổng chủ bãi ở `/api/v1/garage` trong khi frontend gọi `/garage`, nên năm màn hình chủ bãi trả về 404. Đã đổi cả hai về `/garage-portal` |
| Làm `npm run build` chạy sạch | Bỏ import không dùng, bỏ biến không dùng, đổi `vite.config.ts` sang `import.meta.url`, thêm `@types/node` |
| Đổi tham chiếu tài liệu trong code | Các chú thích trỏ tới tài liệu nội bộ cũ giờ trỏ tới tài liệu 08 |

Một thứ chưa xoá và cần bạn quyết định: thư mục `frontend/.design` chứa ảnh chụp và mã HTML của các màn hình thiết kế theo nghiệp vụ cũ. Thư mục này không được git theo dõi, nên xoá là không lấy lại được. Nó không ảnh hưởng gì tới lúc chạy. Đề nghị xem qua rồi tự xoá, hoặc giữ như tham khảo về ngôn ngữ thị giác.

---

## 8. Nợ kỹ thuật và lỗi đã phát hiện

Xếp theo mức ảnh hưởng. Đây là danh sách việc thật, không phải nhận xét chung.

| Mức | Vấn đề | Ở đâu | Đề xuất |
|---|---|---|---|
| Cao | Không có cơ chế tự làm mới token. Access token hết hạn sau 60 phút thì mọi request trả 401 và người dùng bị đẩy ra ngoài, dù đã có endpoint `/auth/refresh` và refresh token sống 7 ngày | `services/api.ts` | Bọc `apiFetch`: gặp 401 thì gọi `/auth/refresh` một lần rồi thử lại request. Chống gọi lặp bằng một promise dùng chung |
| Cao | Route bị chặn thì đẩy về `/login` dù người dùng đã đăng nhập. Người dùng vai trò khách gõ `/garage` sẽ thấy trang đăng nhập, tưởng là bị đăng xuất | `App.tsx`, `ProtectedRoute` | Đẩy về trang chủ đúng vai trò của họ, hoặc một trang thông báo không có quyền |
| Cao | Hai phong cách API song song. Module lõi dùng `POST /garage/get_all` kiểu RPC, hai cổng giao diện dùng REST | `app/api/*/*_views.py` | Chọn REST cho toàn bộ endpoint mới. Không sửa hàng loạt ngay, sửa dần theo module khi chạm tới |
| Trung bình | Ảnh đại diện người dùng lấy từ một dịch vụ sinh ảnh ngoài internet. Không có mạng là hỏng, và đây là dữ liệu người dùng gửi ra ngoài | `layouts/CustomerLayout.tsx` | Thay bằng chữ cái đầu của tên, giống cách `GarageLayout` đang làm |
| Trung bình | Hai trang chỗ trống nhưng vẫn có route: quản trị nền tảng và hồ sơ khách hàng | `pages/admin/AdminDashboard.tsx`, `pages/customer/CustomerProfile.tsx` | Hoặc làm thật, hoặc để một trang thông báo đang phát triển cho rõ ràng |
| Trung bình | `AdminLayout` chỉ là một `Outlet`, không có điều hướng nào. Vai trò quản trị nền tảng chưa có màn hình thật | `layouts/AdminLayout.tsx` | Dựng theo khuôn `GarageLayout` khi bắt đầu làm màn hình quản trị |
| Trung bình | Nhiều chữ trong giao diện là tiếng Anh trộn tiếng Việt, và cắm trực tiếp trong JSX | Hầu hết trang | Chốt một ngôn ngữ chính là tiếng Việt, và gom chuỗi hiển thị lại khi cần đa ngôn ngữ |
| Trung bình | Danh mục dịch vụ mẫu bị nhắc ở ba chỗ khác nhau. Đổi mã dịch vụ mà quên một chỗ là hỏng âm thầm | `service_type_utils.py`, `garage_portal_utils.py`, `customer_views.py`, `SmartBookingModal.tsx` | Lấy danh mục từ API `/service-types/get_all` thay vì cắm cứng ở frontend |
| Trung bình | `garage_portal_utils.py` dài 809 dòng, gộp nhiều loại số liệu dẫn xuất trong một file | `app/api/garage_portal/` | Tách theo màn hình: overview, queue, analytics, score |
| Thấp | Gói frontend chưa tách chunk, một file JavaScript hơn 500 KB | Cấu hình Vite | Tách theo route bằng import động khi có thời gian |
| Thấp | `logs/` và `dist/` nằm trong repo backend | `backend/` | Đưa vào gitignore nếu chưa có |
| Thấp | Địa chỉ OSRM mặc định là bản demo công khai, có giới hạn tần suất | `app/core/config.py` | Tự triển khai OSRM khi lên môi trường thật |
| Thấp | `search_log` ghi truy vấn nhưng chưa có chỗ nào đọc | `app/api/search_log/` | Giữ nguyên. Đây là nguyên liệu cho cá nhân hoá, sẽ dùng sau |

---

## 9. Thứ tự refactor đề xuất

Mỗi bước có kết quả kiểm tra được. Không nhảy bước, vì bước sau dựa trên bước trước.

**Bước 1, chạy được và hiểu được.** Dựng môi trường, chạy backend và frontend, đăng nhập bằng tài khoản super admin, đi hết ba nhóm route để thấy màn hình nào có gì. Không sửa gì trong bước này.

**Bước 2, sửa hai lỗi chặn trải nghiệm.** Làm cơ chế tự làm mới token, và sửa hành vi đẩy về trang đăng nhập khi thiếu quyền. Hai việc này nhỏ nhưng chặn mọi thứ phía sau, vì cứ 60 phút là bị đăng xuất.

**Bước 3, chốt danh mục dịch vụ và mô hình giá.** Đây là quyết định nghiệp vụ đầu tiên có ảnh hưởng lan rộng, vì nó chạm tới đặt chỗ, tính giá, dashboard và cả giao diện. Sửa seed trong `service_type_utils.py`, rồi cho frontend lấy danh mục từ API thay vì cắm cứng.

**Bước 4, đổi hồ sơ bãi.** Sửa `garage_models.py` theo bộ thuộc tính trong tài liệu 05 mục 4: toạ độ cổng vào, loại che chắn, giới hạn chiều cao, bảo vệ, trụ sạc, nguy cơ ngập, cách tổ chức đỗ. Cập nhật `garage_utils.py`, `garage_views.py` và các màn hình liên quan. Sau bước này bộ lọc tìm kiếm mới có nghĩa.

**Bước 5, mở rộng đặt chỗ theo khoảng thời gian.** Sửa `booking_models.py` và `booking_utils.py` để một lượt là chiếm giữ một khoảng thời gian, có cửa sổ giữ chỗ và thời gian chờ thêm. Giữ máy trạng thái và khoá phân tán đang có.

**Bước 6, đổi đầu vào của công suất.** Chuẩn bị `capacity` để nhận số chỗ trống từ nguồn ngoài thay vì chỉ từ cập nhật thủ công. Chưa cần camera thật, chỉ cần một endpoint nhận số liệu và ghi snapshot.

**Bước 7, chỉnh engine ghép nối.** Đổi biến đầu vào của `matching_engine.py` từ thời gian phục vụ sang nhịp xe vào và xe ra. Các hàm trong `scoring.py` sửa từng hàm, không viết lại cả file.

**Bước 8, đổi tên trên toàn hệ thống.** Chỉ làm sau khi các bước trên đã ổn định: đổi `garage` thành `parking_lot` ở tên module, model, collection và endpoint. Làm một lần, một nhánh riêng, không trộn với thay đổi nghiệp vụ, và cần kịch bản chuyển dữ liệu.

**Bước 9, màn hình quản trị nền tảng.** Dựng `AdminLayout` và các trang quản trị: danh sách bãi, tình trạng onboard, sức khoẻ thiết bị, bản đồ nhu cầu chưa được phục vụ.

---

## 10. Quy ước để không tạo lại rác cũ

Sáu quy ước, rút ra từ chính những gì phải dọn ở mục 7.

**Không cắm tên sản phẩm vào bất cứ đâu ngoài `src/config/app.ts`.** Cần hiển thị tên thì import `APP_NAME` hoặc dùng `Brand`.

**Không cắm số liệu bịa vào giao diện.** Nếu chưa có dữ liệu thật thì để trạng thái rỗng có thông báo rõ ràng, không điền số cho đẹp. Số bịa sẽ bị mang đi demo và không ai biết nó là bịa.

**Không phụ thuộc dịch vụ ngoài cho những thứ không cần thiết.** Ảnh đại diện, ảnh nền, font, tất cả nên nằm trong dự án.

**Không gọi `fetch` trực tiếp trong trang.** Mọi lời gọi API đi qua `services/api.ts` để còn chỗ xử lý lỗi, làm mới token và ghi log tập trung.

**Không truy vấn dữ liệu mà thiếu `current_user`.** Đây là ranh giới cách ly giữa các chủ bãi.

**Mỗi module backend giữ đúng bốn file theo khuôn models, schemas, utils, views, và endpoint không chứa logic.** Đây là điều làm cho một người mới đọc module lạ vẫn biết tìm gì ở đâu.
