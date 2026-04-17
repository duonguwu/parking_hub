# WashMind Backend — Test & Bug Report (Phase 1)
> **Ngày:** 17/04/2026 23:20 (GMT+7) | **Phase:** 1 — Backend Foundation

---

## 1. Tổng quan

| Metric | Giá trị |
|--------|---------|
| **Tổng test cases** | 50 |
| **✅ Passed** | **41** (82%) |
| **❌ Failed** | **9** (18%) |
| **Thời gian chạy** | ~3.3s |
| **Framework** | pytest + pytest-asyncio + httpx |
| **DB test** | `washmind_test` (auto cleanup) |

```bash
# Lệnh chạy test
uv run pytest test/ -v              # tất cả
uv run pytest test/test_auth.py -v  # chỉ auth
uv run pytest test/ -k "login"      # filter
```

---

## 2. Kết quả theo Module

### ✅ Auth Module — 17/17 PASSED

| # | Test | Mô tả |
|---|------|--------|
| 1 | `test_root` | GET / → `{"status":"ok","app":"WashMind"}` |
| 2 | `test_health` | Health check API + MongoDB |
| 3 | `test_register_customer_success` | Đăng ký customer + JWT cookie |
| 4 | `test_register_duplicate_username` | Trùng username → 409 |
| 5 | `test_register_invalid_data` | Invalid → 422 |
| 6 | `test_register_garage_success` | Đăng ký garage (tenant+user+garage) |
| 7 | `test_register_garage_duplicate` | Trùng → 409 |
| 8 | `test_login_customer_by_username` | Login by username |
| 9 | `test_login_customer_by_email` | Login by email |
| 10 | `test_login_garage_owner` | Garage owner login |
| 11 | `test_login_superadmin` | Super admin login |
| 12 | `test_login_wrong_password` | Sai password → 401 |
| 13 | `test_login_nonexistent_user` | User ko tồn tại → 401 |
| 14 | `test_get_me_authenticated` | /auth/me với cookie |
| 15 | `test_get_me_unauthenticated` | Ko cookie → 401 |
| 16 | `test_refresh_token` | Refresh JWT |
| 17 | `test_logout` | Logout xóa cookie |

### 🔶 Garage Module — 6/10

| # | Test | Status | Lỗi |
|---|------|--------|-----|
| 1 | `test_list_garages_as_admin` | ✅ | — |
| 2 | `test_list_garages_as_garage_owner` | ❌ | BUG-01: tenant filter 0 results |
| 3 | `test_list_garages_as_customer` | ✅ | — |
| 4 | `test_get_garage_by_id` | ❌ | BUG-02: 422 validation |
| 5 | `test_get_garage_not_found` | ✅ | — |
| 6 | `test_update_garage` | ❌ | Cascade từ BUG-01 |
| 7 | `test_update_capacity` | ❌ | Cascade từ BUG-01 |
| 8 | `test_search_nearby` | ✅ | — |
| 9 | `test_search_nearby_tier_filter` | ✅ | — |

### 🔶 Tenant Module — 3/5

| # | Test | Status | Lỗi |
|---|------|--------|-----|
| 1 | `test_list_tenants_as_admin` | ✅ | — |
| 2 | `test_list_tenants_forbidden_customer` | ✅ | — |
| 3 | `test_list_tenants_forbidden_garage_owner` | ✅ | — |
| 4 | `test_get_tenant_by_id` | ❌ | BUG-02: 422 |
| 5 | `test_update_tenant` | ❌ | BUG-02: 422 |

### 🔶 User Module — 8/9

| # | Test | Status | Lỗi |
|---|------|--------|-----|
| 1 | `test_list_users_as_garage_owner` | ❌ | BUG-01 |
| 2 | `test_list_users_as_admin` | ✅ | — |
| 3 | `test_create_staff_user` | ✅ | — |
| 4 | `test_create_manager_user` | ✅ | Fixed (raw insert) |
| 5 | `test_create_invalid_role` | ✅ | — |
| 6 | `test_customer_cannot_create_users` | ✅ | — |
| 7 | `test_update_user` | ✅ | — |
| 8 | `test_deactivate_user` | ✅ | — |
| 9 | `test_cannot_deactivate_self` | ✅ | — |

### ✅ Vehicle Module — 9/9 PASSED

| # | Test | Mô tả |
|---|------|--------|
| 1 | `test_create_vehicle` | Tạo xe + auto tier mapping |
| 2 | `test_create_luxury_vehicle` | Luxury → tier 3 |
| 3 | `test_create_duplicate_plate` | Trùng biển số → 409 |
| 4 | `test_list_vehicles` | List xe user |
| 5 | `test_list_vehicles_unauthenticated` | No auth → 401 |
| 6 | `test_get_vehicle` | Get by ID |
| 7 | `test_update_vehicle` | Update color/year |
| 8 | `test_update_vehicle_type_updates_tier` | Đổi type → auto tier |
| 9 | `test_delete_vehicle` | Soft delete |

---

## 3. Bug Registry

### 🔴 BUG-01: Garage Owner thấy 0 kết quả (OPEN)

| | |
|-|-|
| **Severity** | 🔴 HIGH |
| **Affected** | Garage, User module |
| **Symptom** | `POST /garage/get_all` + `POST /user/get_all` trả `[]` cho garage_owner |
| **Root Cause** | `TenantAwareDocument._add_tenant_filter()` filter `tenant_id=current_user["tenant_id"]`. JWT token chứa `tenant_id` = slug từ `register_garage()`. Khi slug bị append timestamp (dòng 174 auth_utils.py) → slug trong JWT khác slug thực của garage |
| **Files** | `app/db/base_model.py:76`, `app/api/auth/auth_utils.py:169-174` |
| **Fix** | Verify slug consistency: đảm bảo tenant.slug == user.tenant_id == garage.tenant_id. Thêm logging trong `_add_tenant_filter()` khi debug |

### 🟡 BUG-02: POST + `@has_permission` + body → 422 (OPEN)

| | |
|-|-|
| **Severity** | 🟡 MEDIUM |
| **Affected** | Tenant (get_by_id, update), Garage (get_by_id) |
| **Symptom** | Endpoints POST với body + `@has_permission` decorator → 422 Unprocessable Entity |
| **Root Cause** | `@has_permission` dùng `@wraps` + `*args, **kwargs` wrapper. Dù set `wrapper.__signature__`, FastAPI vẫn không resolve body param đúng ở một số endpoint. User create/update hoạt động vì cùng pattern nhưng khác model |
| **Files** | `app/api/auth/permissions.py:138-175` |
| **Fix** | Option A: Debug `inspect.signature(wrapper)` so sánh PASS vs FAIL endpoints. Option B: Chuyển sang `Depends`-based RBAC (FastAPI native). Option C: Remove decorator, gọi `check_permission()` inline trong mỗi endpoint |

### ✅ BUG-03: `DictField.fail()` missing (FIXED)

| | |
|-|-|
| **Root Cause** | umongo v4 + marshmallow v4: `DictField` thiếu method `fail()` khi validate `{}` |
| **Fix** | Dùng `collection.insert_one()` raw thay umongo model constructor trong `user_utils.py:create_staff_user()` |

### ✅ BUG-04: `passlib` + `bcrypt>=5.0` crash (FIXED)

| | |
|-|-|
| **Root Cause** | passlib internal test hash > 72 bytes, bcrypt 5.0 enforce limit |
| **Fix** | Thay `passlib.CryptContext` bằng `bcrypt.hashpw()` / `bcrypt.checkpw()` trực tiếp trong `auth_utils.py` |

### ✅ BUG-05: `ListField(default=None)` crash umongo (FIXED)

| | |
|-|-|
| **Root Cause** | umongo `ListField` ko chấp nhận `None` default |
| **Fix** | Đổi thành `default=list` trong `user_models.py:allowed_tenant_ids` |

### ✅ BUG-06: `NoDBDefinedError` in tests (FIXED)

| | |
|-|-|
| **Root Cause** | `ASGITransport` không trigger FastAPI lifespan → umongo chưa bind DB |
| **Fix** | Gọi `init_mongo()` thủ công trong `conftest.py` trước khi tạo client |

### ✅ BUG-07: httpx cookie leak → false pass (FIXED)

| | |
|-|-|
| **Root Cause** | httpx `AsyncClient` session-scoped giữ cookies giữa requests |
| **Fix** | Tạo fresh `AsyncClient` cho unauthenticated tests |

---

## 4. Tóm tắt

### Đã Fix (5 bugs)
| # | Bug | Impact |
|---|-----|--------|
| 3 | DictField + marshmallow v4 | User create crash |
| 4 | passlib + bcrypt 5.0 | All auth crash |
| 5 | ListField default=None | Model import crash |
| 6 | No DB in tests | All tests crash |
| 7 | Cookie leak | False test pass |

### Cần Fix (2 bugs)
| # | Bug | Priority | Est. |
|---|-----|----------|------|
| 1 | Tenant filter 0 results | 🔴 HIGH | 30 min |
| 2 | Decorator + body 422 | 🟡 MED | 1 hour |

---

## 5. Test Infrastructure

### File Structure
```
test/
├── conftest.py         # Fixtures: client, cookies, registered users
├── test_auth.py        # 17 tests
├── test_garage.py      # 10 tests
├── test_tenant.py      #  5 tests
├── test_user.py        #  9 tests
└── test_vehicle.py     #  9 tests
```

### Fixture Flow
```
client (session-scope)
├── init_mongo() → drop washmind_test → create indexes → seed superadmin
├── superadmin_cookies ← login(superadmin)
├── registered_customer ← POST /auth/register
└── registered_garage   ← POST /auth/register-garage
    → creates: Tenant + User(garage_owner) + Garage
```

---

## 6. API Endpoint Reference

| Module | Method | Endpoint | Auth | Permission |
|--------|--------|----------|------|------------|
| Auth | POST | `/auth/register` | — | — |
| Auth | POST | `/auth/register-garage` | — | — |
| Auth | POST | `/auth/login` | — | — |
| Auth | GET | `/auth/me` | Cookie | — |
| Auth | POST | `/auth/refresh` | Cookie | — |
| Auth | POST | `/auth/logout` | Cookie | — |
| Tenant | POST | `/tenant/get_all` | Cookie | `tenant:view` |
| Tenant | POST | `/tenant/get_by_id` | Cookie | `tenant:view` |
| Tenant | POST | `/tenant/update` | Cookie | `tenant:edit` |
| User | POST | `/user/get_all` | Cookie | `user:view` |
| User | POST | `/user/get_by_id` | Cookie | `user:view` |
| User | POST | `/user/create` | Cookie | `user:create` |
| User | POST | `/user/update` | Cookie | `user:edit` |
| User | POST | `/user/delete` | Cookie | `user:delete` |
| Garage | POST | `/garage/get_all` | Cookie | `garage:view` |
| Garage | POST | `/garage/get_by_id` | Cookie | `garage:view` |
| Garage | POST | `/garage/update` | Cookie | `garage:edit` |
| Garage | POST | `/garage/update_capacity` | Cookie | `capacity:edit` |
| Garage | POST | `/garage/search_nearby` | — | — |
| Vehicle | POST | `/vehicle/get_all` | Cookie | — |
| Vehicle | POST | `/vehicle/get_by_id` | Cookie | — |
| Vehicle | POST | `/vehicle/create` | Cookie | — |
| Vehicle | POST | `/vehicle/update` | Cookie | — |
| Vehicle | POST | `/vehicle/delete` | Cookie | — |

---

## 7. Next Steps

1. **Fix BUG-01** — Debug tenant_id mismatch (30 min)
2. **Fix BUG-02** — Decorator signature hoặc inline permission check (1h)
3. **Target: 50/50 tests green** trước khi bắt đầu Phase 2
4. **Phase 2** — Matching Engine + Service Logs (Data Moat)
