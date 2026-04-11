# Base Source Code Reference

> **Template & hướng dẫn dựng dự án FastAPI mới** theo pattern đã production-proven.
> **Nguồn tham khảo**: Queue Management System (112+ cameras, real-time AI inference).
> **Ngày tạo**: 2026-04-11

---

## Mục lục

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
3. [Quick Start — Setup dự án mới](#3-quick-start)
4. [MongoDB + Motor + Umongo](#4-mongodb--motor--umongo)
5. [Multi-Tenancy (TenantAwareDocument)](#5-multi-tenancy)
6. [Feature-First API](#6-feature-first-api)
7. [Authentication & Authorization (JWT + RBAC)](#7-authentication--authorization)
8. [Services & Worker Pattern (Microservices)](#8-services--worker-pattern)
9. [Redis IPC (Inter-Process Communication)](#9-redis-ipc)
10. [Shared Utilities](#10-shared-utilities)
11. [Danh sách file](#11-danh-sách-file)

---

## 1. Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────┐
│                    Client (Browser / Mobile)         │
│                    ↕ REST API / WebSocket            │
├─────────────────────────────────────────────────────┤
│              FastAPI Backend (uvicorn)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Auth     │  │ Feature  │  │ Feature  │  ...      │
│  │ Module   │  │ A Views  │  │ B Views  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │              │              │                │
│  ┌────┴──────────────┴──────────────┴────┐          │
│  │         Shared (utils, schemas)       │          │
│  └────────────────┬──────────────────────┘          │
│                   │                                  │
│  ┌────────────────┴──────────────────────┐          │
│  │   MongoDB (Motor + Umongo)            │          │
│  │   TenantAwareDocument base            │          │
│  └───────────────────────────────────────┘          │
├─────────────────────────────────────────────────────┤
│           Redis 7.x (IPC Buffer + Pub/Sub)          │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Worker A     │  │ Worker B     │  (separate      │
│  │ (standalone) │  │ (standalone) │   processes)     │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
```

**Nguyên tắc**:
- **FastAPI** là API gateway duy nhất, xử lý HTTP + WebSocket.
- **MongoDB** (Motor async + Umongo ODM) là primary database.
- **Redis** làm IPC buffer giữa các process (pub/sub, shared state, distributed lock).
- **Worker processes** chạy riêng, giao tiếp qua Redis — tách biệt lifecycle với API server.
- **Multi-tenancy** tự động qua `TenantAwareDocument` — mọi query đều filter theo `tenant_id`.

---

## 2. Cấu trúc thư mục

```
your_project/
├── main.py                      # FastAPI entry point + lifespan + middleware
├── app/
│   ├── core/
│   │   ├── config.py            # pydantic-settings (env vars)
│   │   └── logging_config.py    # Centralized logging (RotatingFile + GMT+7)
│   │
│   ├── db/
│   │   ├── mongo.py             # Motor client + Umongo instance (singleton)
│   │   └── base_model.py        # TenantAwareDocument (multi-tenant base)
│   │
│   ├── api/
│   │   ├── main_router.py       # Aggregates all feature routers
│   │   ├── auth/
│   │   │   ├── jwt_manager.py   # JWT create/decode + cookie helpers
│   │   │   ├── dependencies.py  # get_current_user (Depends)
│   │   │   └── permissions.py   # RBAC: has_permission decorator + enums
│   │   │
│   │   ├── {feature}/           # ← Feature-First module
│   │   │   ├── {feature}_schemas.py
│   │   │   ├── {feature}_utils.py
│   │   │   ├── {feature}_views.py
│   │   │   └── {feature}_models.py  (optional)
│   │   │
│   │   └── shared/
│   │       ├── common_utils.py  # api_response(), validate_id_format()
│   │       ├── schemas.py       # Operation, Resource enums
│   │       ├── exceptions.py    # Custom exception hierarchy
│   │       └── tool/
│   │           ├── convert_object_id.py
│   │           └── datetime_convert.py
│   │
│   └── services/
│       ├── shared/
│       │   ├── abstractions/
│       │   │   └── singleton.py      # Thread-safe Singleton base
│       │   └── redis_client.py       # Redis singleton (dual pools)
│       │
│       └── {worker_name}/
│           └── {worker_name}_worker.py  # Standalone worker process
│
├── .env                         # Environment variables
├── pyproject.toml               # Dependencies (uv / pip)
└── logs/                        # Auto-created by logging_config
```

---

## 3. Quick Start

### 3.1 Dependencies (pyproject.toml / requirements)

```
# Core
fastapi
uvicorn[standard]
pydantic-settings
python-dotenv

# Database
motor              # Async MongoDB driver
umongo             # ODM cho MongoDB
pymongo            # bson ObjectId

# Auth
python-jose[cryptography]   # JWT
bcrypt                       # Password hashing
passlib[bcrypt]

# Redis
redis[hiredis]     # Async Redis with hiredis parser

# Utilities
pytz
python-dateutil

# Performance (optional)
uvloop             # Faster event loop cho workers
```

### 3.2 Khởi chạy

```bash
# 1. Install dependencies
uv sync   # hoặc pip install -r requirements.txt

# 2. Start MongoDB + Redis
docker run -d --name mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  mongo:7

docker run -d --name redis -p 6379:6379 redis:7.2-alpine

# 3. Start API server
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. Start worker (separate terminal)
uv run python -m app.services.example_worker.example_worker
```

### 3.3 Env vars (.env)

```env
MONGO_URI=mongodb://admin:admin123@localhost:27017/your_db?authSource=admin
MONGO_DB=your_db

REDIS_URL=redis://localhost:6379

JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

SUPER_ADMIN_PASSWORD=admin123

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 4. MongoDB + Motor + Umongo

### Tại sao Motor + Umongo?

| Aspect | PyMongo + `get_db()` | Motor + Umongo |
|--------|---------------------|----------------|
| Async | Không (sync) | **Có** (native async) |
| Schema | Tự quản lý | **ODM** class-based |
| Tenant filter | Tự viết mỗi query | **Tự động** qua base class |
| Typo risk | Cao (string keys) | **Thấp** (field attributes) |

### Connection pattern (singleton)

```python
# db/mongo.py
mongo_instance = MotorAsyncIOInstance()  # Singleton — share across ALL models

def init_mongo():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    mongo_instance.set_db(db)  # Bind 1 lần duy nhất

def close_mongo():
    client.close()
```

### Model registration

```python
# Mọi model đăng ký chung 1 instance
@mongo_instance.register
class YourModel(TenantAwareDocument):
    name = fields.StringField(required=True)
    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "your_collection"
```

> **Xem file**: `src/db/mongo.py`, `src/db/base_model.py`

---

## 5. Multi-Tenancy

### Nguyên tắc

- **Mọi document** đều có field `tenant_id`.
- **Mọi query** (find, find_one) tự động inject tenant filter từ `current_user`.
- **Super admin** (`tenant_id == "super_admin"`) thấy tất cả.
- **Center manager** có `allowed_tenant_ids` — thấy nhiều tenant con.

### TenantAwareDocument — base class

```python
class TenantAwareDocument(Document):
    tenant_id = fields.StringField(required=True)
    created_at = fields.AwareDateTimeField(default=get_current_time)
    updated_at = fields.AwareDateTimeField(default=get_current_time)
    created_by = fields.StringField(default="system")
    updated_by = fields.StringField(default="system")
```

### Auto tenant filter

```python
# find() / find_one() override — tự thêm tenant_id vào filter
@classmethod
def find(cls, *args, **kwargs):
    filter_arg, current_user, ... = cls._extract_filter_and_user(*args, **kwargs)
    filtered = cls._add_tenant_filter(filter_arg, current_user)
    return super().find(filtered, ...)
```

### Helper methods

| Method | Chức năng |
|--------|-----------|
| `create_with_tenant_check()` | Tạo doc + check name unique trong tenant |
| `update_with_tenant_check()` | Update + enforce tenant authorization |
| `delete_with_tenant_check()` | Delete + enforce tenant + optional usage check |
| `get_by_id_with_tenant_check()` | Get by ID với tenant filter |
| `check_name_exists_in_tenant()` | Check trùng tên trong cùng tenant |

### Usage trong utils

```python
# ĐÚNG — tenant filter tự động
docs = await ProductModel.find({}, current_user=current_user)
doc = await ProductModel.find_one({"name": "ABC"}, current_user=current_user)

# SAI — sẽ raise 401
docs = await ProductModel.find({})

# Bypass (seed/admin tasks)
docs = await ProductModel.find({}, current_user={"tenant_id": "super_admin"})
```

> **Xem file**: `src/db/base_model.py`

---

## 6. Feature-First API

### Cấu trúc mỗi feature

```
api/{feature}/
├── {feature}_schemas.py    # Pydantic request/response models
├── {feature}_utils.py      # Business logic + DB operations
├── {feature}_views.py      # API endpoints (thin layer)
└── {feature}_models.py     # MongoDB model (optional)
```

### Quy tắc

| Layer | Trách nhiệm | KHÔNG được |
|-------|-------------|------------|
| **schemas** | Validation, type hints | Business logic |
| **utils** | Business logic, DB ops, error handling | Import FastAPI (Request, Depends) |
| **views** | HTTP handling, 2-4 lines/endpoint | Business logic, try-catch, validation |
| **models** | Collection definition, field schema | Business logic |

### Views pattern (siêu clean)

```python
@feature_router.get("/items")
@has_permission(["item:view"])
async def get_items(current_user: dict = Depends(get_current_user)):
    data = await get_all_items(current_user=current_user)
    return api_response(Operation.RETRIEVED, Resource.ITEMS, data)
```

### Utils pattern

```python
async def get_all_items(current_user: dict) -> List[Dict]:
    try:
        cursor = ItemModel.find({}, current_user=current_user)
        docs = await cursor.to_list(length=None)
        return [format_item(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to load items: {e}")
```

> **Xem file**: `src/api/example_feature/` (complete example)

---

## 7. Authentication & Authorization

### Flow

```
Login (username/password)
  → authenticate_user()
  → create_access_token + create_refresh_token
  → set httpOnly cookies
  → mọi request sau đó gửi cookie tự động

Request vào API
  → AuthMiddleware check cookie
  → get_current_user (Depends) decode JWT + verify user active
  → @has_permission(["module:action"]) check RBAC
  → endpoint handler
```

### JWT tokens (httpOnly cookie)

```python
# Access token: short-lived (30 min), path="/"
# Refresh token: long-lived (7 days), path="/auth" (chỉ gửi tới auth endpoints)
set_auth_cookies(response, access_token, refresh_token)
```

### RBAC Permission format

```
{module}:{action}
```

Ví dụ: `camera:view`, `user:create`, `role:edit`, `system:config`

### Permission check

```python
# Decorator trên endpoint
@has_permission(["item:view", "item:edit"])  # user cần CÓ ÍT NHẤT 1 permission
async def endpoint(current_user: dict = Depends(get_current_user)):
    ...

# Super admin bypass: tenant_id == "super_admin" → skip mọi check
# __all__ permission: bypass mọi check
```

> **Xem file**: `src/api/auth/`

---

## 8. Services & Worker Pattern

### Kiến trúc Microservices

```
Process 1: FastAPI (uvicorn)     ← API server
Process 2: Worker A              ← Standalone, async
Process 3: Worker B              ← Standalone, async
           ↕ Redis IPC ↕
```

Mỗi worker là **process riêng biệt**, có:
- Lifecycle riêng (start → run → shutdown)
- Signal handling (SIGINT, SIGTERM)
- Redis connection riêng
- Graceful shutdown

### Worker template

```python
class ExampleWorker:
    def __init__(self):
        self.should_stop = asyncio.Event()

    async def start(self):
        await redis_client.connect()
        # Initialize services

    async def run(self):
        while not self.should_stop.is_set():
            # Poll Redis, process data, publish results
            await asyncio.sleep(0.5)

    async def shutdown(self):
        await redis_client.disconnect()

    def start_blocking(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._main())
```

### Chạy worker

```bash
uv run python -m app.services.example_worker.example_worker
```

> **Xem file**: `src/services/example_worker/`

---

## 9. Redis IPC

### Dual Pool pattern

Redis client dùng **2 connection pools** riêng biệt:

| Pool | `decode_responses` | Dùng cho |
|------|--------------------|----------|
| **Text pool** | `True` | JSON stats, config, pub/sub messages |
| **Binary pool** | `False` | Binary data (files, images, frames) |

### Key schema (ví dụ)

| Key | Content | TTL |
|-----|---------|-----|
| `raw:{item_id}` | Binary data | 2s |
| `result:{item_id}` | JSON result | 30s |
| `config:{item_id}` | JSON config | — |

### Pub/Sub pattern

```python
# Publisher (worker)
await redis_client.publish(f"results:{item_id}", result_json)

# Subscriber (API server)
pubsub = await redis_client.subscribe("results:*")
async for message in pubsub.listen():
    ...
```

### Distributed lock

```python
async with redis_client.lock_context("process_item_123", timeout=10):
    # Critical section — chỉ 1 process được chạy
    await process_item(item_id)
```

> **Xem file**: `src/services/shared/redis_client.py`

---

## 10. Shared Utilities

### api_response() — Response format chuẩn

```python
return api_response(
    operation=Operation.RETRIEVED,  # CREATED, UPDATED, DELETED, ...
    resource=Resource.ITEMS,        # Tên resource
    data=items_data                 # Optional payload
)
# → {"status": "ok", "message": "Items retrieved successfully", "data": [...]}
```

### Custom Exceptions

```python
raise ValidationError("Email is required", field="email")  # 400
raise NotFoundError("User", user_id)                       # 404
raise ConflictError("Username already exists")              # 409
raise InternalServerError("Database connection failed")     # 500
raise ServiceUnavailableError("Redis")                      # 503
```

### Tools

- `convert_mongo_object_id(id_str)` — safe ObjectId conversion
- `get_current_time()` — UTC datetime
- `get_current_time_zone_7()` — Asia/Bangkok datetime
- `validate_time_format(time_str)` — validate time string

---

## 11. Danh sách file

Đọc theo thứ tự recommended:

1. `src/core/config.py` — Environment config
2. `src/core/logging_config.py` — Logging setup
3. `src/db/mongo.py` — MongoDB connection
4. `src/db/base_model.py` — TenantAwareDocument
5. `src/api/shared/` — Common utilities
6. `src/api/auth/` — Authentication system
7. `src/api/example_feature/` — Feature-First example
8. `src/api/main_router.py` — Router aggregation
9. `src/main.py` — FastAPI entry point
10. `src/services/shared/` — Redis + Singleton
11. `src/services/example_worker/` — Worker pattern

---

## Lưu ý khi dùng reference này

- **Import paths**: Thay `app.` thành package name thực tế của dự án mới.
- **Collection names**: Đổi tên collection trong models cho phù hợp domain.
- **Resource enum**: Thêm resource types mới vào `schemas.py`.
- **Permissions**: Đổi module/action trong `permissions.py` cho phù hợp domain.
- **Redis keys**: Thiết kế key schema riêng cho domain mới.
- **Worker logic**: Thay đổi `run()` loop cho phù hợp nghiệp vụ.

**Mục tiêu**: Copy reference → đổi tên → chạy được ngay. Tất cả patterns đã production-proven.
