# ️ Feature-First Architecture Guide

> **Tài liệu hướng dẫn triển khai API theo mô hình Feature-First**  
> **Chuẩn tham khảo**: Camera Module  
> **Ngày tạo**: 2026-01-30

##  Tổng quan

Feature-First Architecture tổ chức code theo **chức năng nghiệp vụ** thay vì theo **loại file**. Mỗi feature là một module độc lập với đầy đủ các thành phần: schemas, utils, views.

###  Nguyên tắc cốt lõi

1. **Separation of Concerns**: Mỗi layer có trách nhiệm riêng biệt
2. **Clean Views**: Views chỉ handle HTTP requests/responses
3. **Business Logic in Utils**: Tất cả logic nghiệp vụ ở utils
4. **Centralized Validation**: Validation tập trung trong utils
5. **Standardized Response**: Sử dụng `api_response()` thống nhất

##  Cấu trúc thư mục chuẩn

```
backend/app/api/
├── {feature_name}/
│   ├── {feature}_schemas.py    # Request/Response models
│   ├── {feature}_utils.py      # Business logic
│   ├── {feature}_views.py      # API endpoints
│   └── {feature}_models.py     # Data models (optional)
└── shared/
    ├── common_utils.py         # Shared utilities
    ├── schemas.py              # Common enums/schemas
    └── exceptions.py           # Custom exceptions
```

##  Chi tiết triển khai từng layer

### 0. **{feature}_models.py** - Database Models (khi cần)

**Mục đích**: Định nghĩa MongoDB collection model kế thừa `TenantAwareDocument`.

Dùng khi feature có collection MongoDB riêng. Nếu tái dùng model từ module khác thì chỉ cần import, không tạo file mới.

```python
"""
{Feature} Models — MongoDB document model cho {feature}.
"""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class {Feature}Model(TenantAwareDocument):
    name = fields.StringField(required=True)
    is_active = fields.BooleanField(default=True)
    # tenant_id đã có từ TenantAwareDocument

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "{feature}s"   # tên collection trong MongoDB
        indexes = [("tenant_id", "name")]
```

**Quy tắc Models:**
- Luôn kế thừa `TenantAwareDocument` — tenant filter tự động trong mọi query
- `strict = False` đã có sẵn trong Meta — không reject documents có thêm fields lạ từ DB
- Không viết business logic trong model — để trong utils
- Khi gọi `find()` / `find_one()`: **bắt buộc** truyền `current_user`

```python
# ✅ Đúng — tenant filter tự động
docs = await {Feature}Model.find({}, current_user=current_user)

# ❌ Sai — sẽ raise HTTPException 401
docs = await {Feature}Model.find({})

# ✅ Bypass tenant (seed/admin ops)
docs = await {Feature}Model.find({}, current_user={"tenant_id": "super_admin"})
```

Helper methods từ `TenantAwareDocument`:
- `create_with_tenant_check(data, current_user, name_field, target_tenant_id)` — tạo doc + check tên unique trong tenant
- `update_with_tenant_check(doc_id, update_data, current_user)` — update + enforce tenant
- `delete_with_tenant_check(doc_id, current_user)` — delete + enforce tenant

---

### 1.  **{feature}_schemas.py** - Data Models

**Mục đích**: Định nghĩa request/response schemas với validation

```python
"""
{Feature} API Schemas - Request/Response models cho {feature} endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Request Schemas
class {Feature}CreateRequest(BaseModel):
    """Schema cho tạo {feature}"""
    name: str = Field(..., description="Tên {feature}", min_length=1)
    value: int = Field(..., description="Giá trị", ge=0)

class {Feature}UpdateRequest(BaseModel):
    """Schema cho cập nhật {feature}"""
    name: Optional[str] = Field(None, description="Tên {feature}")
    value: Optional[int] = Field(None, description="Giá trị", ge=0)

# Response Schemas (nếu cần custom response format)
class {Feature}Response(BaseModel):
    """Schema cho response {feature}"""
    id: str = Field(..., description="ID của {feature}")
    name: str = Field(..., description="Tên {feature}")
    value: int = Field(..., description="Giá trị")
```

** Quy tắc Schemas:**
-   Sử dụng `Field()` với description và validation
-   Tách riêng Request và Response schemas
-   Validation constraints (ge=0, min_length, etc.)
-   Optional fields cho Update requests
-   Không để logic business trong schemas

### 2. ️ **{feature}_utils.py** - Business Logic

**Mục đích**: Xử lý tất cả business logic, validation, database operations

```python
"""
{Feature} Utils - Business logic cho {feature} operations
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from app.db.database import get_db_connection
from app.api.shared.common_utils import validate_id_format, create_success_response

async def get_all_{feature}s() -> List[Dict[str, Any]]:
    """
    Lấy danh sách tất cả {feature}s
    
    Returns:
        List[Dict]: Danh sách {feature}s với thông tin đầy đủ
        
    Raises:
        HTTPException: Nếu có lỗi database
    """
    try:
        # Database operations
        data = fetch_from_database()
        return data
    except Exception as e:
        print(f"Error loading {feature}s: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load {feature}s")

async def get_{feature}_by_id(item_id: str) -> Dict[str, Any]:
    """
    Lấy {feature} theo ID
    
    Args:
        item_id: ID của {feature}
        
    Returns:
        Dict: Thông tin {feature}
        
    Raises:
        HTTPException: Nếu ID không hợp lệ hoặc không tìm thấy
    """
    # Validation ngay đầu function
    if not validate_id_format(item_id):
        raise HTTPException(status_code=400, detail="Invalid {feature} ID format")
    
    try:
        # Business logic here
        data = fetch_by_id(item_id)
        if not data:
            raise HTTPException(status_code=404, detail="{Feature} not found")
        return data
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Error getting {feature} {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def create_{feature}_data(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo {feature} mới
    
    Args:
        request_data: Dữ liệu {feature} cần tạo
        
    Returns:
        Dict: Success response với data
        
    Raises:
        HTTPException: Nếu có lỗi validation hoặc database
    """
    try:
        # Additional business validation
        if request_data.get("value", 0) < 0:
            raise HTTPException(status_code=400, detail="Value must be non-negative")
        
        # Database operations
        created_item = create_in_database(request_data)
        
        return create_success_response(
            message="Created successfully",
            data=created_item
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating {feature}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create {feature}")
```

** Quy tắc Utils: **
-   Tất cả validation ở đây (không ở views)
-   Handle tất cả exceptions và convert thành HTTPException
-   Sử dụng `create_success_response()` cho success responses
-   Logging với `print()` (đơn giản, production-ready)
-   Type hints đầy đủ
-   Docstrings chi tiết với Args, Returns, Raises
-    Không import FastAPI dependencies (Request, Depends, etc.)

### 3.  **{feature}_views.py** - API Endpoints

**Mục đích**: Chỉ handle HTTP requests/responses, delegate logic cho utils

```python
"""
{Feature} Views - API endpoints cho {feature} management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.api.{feature}.{feature}_schemas import (
    {Feature}CreateRequest,
    {Feature}UpdateRequest
)
from app.api.{feature}.{feature}_utils import (
    get_all_{feature}s,
    get_{feature}_by_id,
    create_{feature}_data,
    update_{feature}_data,
    delete_{feature}_data
)
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

# Tạo router với tags cho OpenAPI grouping
{feature}_router = APIRouter(tags=["{feature} management"])

@{feature}_router.get("/{feature}s")
async def get_{feature}s() -> Dict[str, Any]:
    """Lấy danh sách tất cả {feature}s"""
    {feature}s_data = await get_all_{feature}s()
    return api_response(
        operation=Operation.RETRIEVED,
        resource=Resource.{FEATURE}S,
        data={feature}s_data
    )

@{feature}_router.get("/{feature}s/{{item_id}}")
async def get_{feature}_endpoint(item_id: str) -> Dict[str, Any]:
    """Lấy {feature} theo ID"""
    {feature}_data = await get_{feature}_by_id(item_id)
    return api_response(
        operation=Operation.RETRIEVED,
        resource=Resource.{FEATURE},
        data={feature}_data
    )

@{feature}_router.post("/{feature}s")
async def create_{feature}_endpoint(request: {Feature}CreateRequest) -> Dict[str, Any]:
    """Tạo {feature} mới"""
    return await create_{feature}_data(request.model_dump())

@{feature}_router.put("/{feature}s/{{item_id}}")
async def update_{feature}_endpoint(item_id: str, request: {Feature}UpdateRequest) -> Dict[str, Any]:
    """Cập nhật {feature}"""
    return await update_{feature}_data(item_id, request.model_dump(exclude_unset=True))

@{feature}_router.delete("/{feature}s/{{item_id}}")
async def delete_{feature}_endpoint(item_id: str) -> Dict[str, Any]:
    """Xóa {feature}"""
    return await delete_{feature}_data(item_id)
```

** Quy tắc Views:**
-   **Siêu ngắn gọn**: 2-4 lines per endpoint
-   **Không validation**: Để utils handle
-   **Không try-catch**: Utils đã handle exceptions
-   **Sử dụng api_response()**: Standardized response format
-   **Type hints**: Rõ ràng input/output types
-   **Docstrings ngắn**: Chỉ mô tả chức năng
-    **Không business logic**: Chỉ HTTP handling

##  Response Format chuẩn

###   Success Response (sử dụng `api_response()`)

```python
# GET requests
return api_response(
    operation=Operation.RETRIEVED,
    resource=Resource.CAMERAS,
    data=cameras_data
)

# POST/PUT requests  
return api_response(
    operation=Operation.CREATED,  # hoặc UPDATED
    resource=Resource.CAMERA,
    data={"id": "cam_001", "name": "Camera 1"}
)

# DELETE requests
return api_response(
    operation=Operation.DELETED,
    resource=Resource.CAMERA
)
```

**Output format:**
```json
{
  "status": "ok",
  "message": "Cameras retrieved successfully",
  "data": [...]
}
```

###    Error Response (HTTPException)

```python
# Validation errors (400)
raise HTTPException(status_code=400, detail="Invalid camera ID format")

# Not found (404)
raise HTTPException(status_code=404, detail="Camera not found")

# Server errors (500)
raise HTTPException(status_code=500, detail="Failed to update camera config")
```

##  So sánh với Camera Module (Chuẩn tham khảo)

###  Camera Module Structure
```
app/api/camera/
├── camera_schemas.py    #   Chỉ có CameraConfigUpdate (đơn giản)
├── camera_utils.py      #   3 functions: get_all, get_config, update_config
└── camera_views.py      #   3 endpoints siêu clean
```

###  Camera Utils Pattern
```python
#   Validation tập trung
if not validate_id_format(camera_id):
    raise HTTPException(status_code=400, detail="Invalid camera ID format")

#   Error handling nhất quán  
try:
    # business logic
    return create_success_response("Config updated")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")
```

###  Camera Views Pattern
```python
#   Siêu clean - chỉ 2-3 lines
@camera_router.get("/cameras/{camera_id}/config")
async def get_camera_config_endpoint(camera_id: str) -> Dict[str, Any]:
    """Lấy config của camera"""
    config_data = await get_camera_config(camera_id)
    return api_response(
        operation=Operation.RETRIEVED,
        resource=Resource.CAMERA_CONFIG,
        data=config_data
    )
```

## ️ Common Pitfalls

###    Những gì KHÔNG nên làm

1. **Logic trong Views**:
   ```python
   #    SAI
   @router.post("/items")
   async def create_item(request: ItemRequest):
       if not validate_id_format(request.id):  # Logic trong view
           raise HTTPException(...)
   ```

2. **Validation trùng lặp**:
   ```python
   #    SAI - validation ở cả views và utils
   # views.py
   if not validate_id_format(item_id):
       raise HTTPException(...)
   
   # utils.py  
   if not validate_id_format(item_id):  # Trùng lặp
       raise HTTPException(...)
   ```

3. **Response format không nhất quán**:
   ```python
   #    SAI
   return {"success": True, "data": data}  # Custom format
   
   #   ĐÚNG
   return api_response(Operation.RETRIEVED, Resource.ITEMS, data)
   ```

###   Best Practices

1. **Single Responsibility**: Mỗi function chỉ làm 1 việc
2. **Fail Fast**: Validation ngay đầu function
3. **Consistent Naming**: `get_all_{feature}s()`, `get_{feature}_by_id()`
4. **Proper Logging**: Sử dụng `print()` cho simplicity
5. **Type Safety**: Type hints đầy đủ

##  Tài liệu tham khảo

- **Camera Module**: `/app/api/camera/` - Chuẩn implementation
- **Shared Utils**: `/app/api/shared/common_utils.py` - Helper functions
- **Response Guide**: `/app/api/shared/response_helpers_guide.md` - Response patterns

---

** Mục tiêu cuối cùng**: Mỗi feature module độc lập, dễ maintain, test được, và có API response format nhất quán.