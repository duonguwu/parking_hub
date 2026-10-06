#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed dữ liệu demo cho Phase Quản lý.

Toàn bộ là dữ liệu giả. Toạ độ quanh các tâm quận thật của TP.HCM, có nhiễu ngẫu nhiên.
Chạy lại với cùng --seed cho ra cùng bộ dữ liệu.

Sinh ra:
  - ~150 bãi đỗ (8 loại hình, cấp tích hợp 1–4, hạng sao từ checklist kiểm định)
    kèm tenant + tài khoản chủ bãi `owner_<quận>_<nn>`
  - bảng giá theo bãi (giá theo quận và loại hình)
  - 40 tài xế `customer_01..40`, mỗi người 1–2 xe
  - ~3.000 lượt đặt trong 90 ngày qua + lượt sắp tới + xe đang trong bãi + xe vãng lai
  - snapshot lấp đầy theo giờ 8 tuần cho bãi cấp ≥ 2
  - chỉ số vận hành và điểm chất lượng tính lại từ lượt đặt

Usage:
  cd backend
  uv run python scripts/seed_data.py --reset          # xoá dữ liệu demo cũ rồi seed
  uv run python scripts/seed_data.py --reset --lots 60 --bookings 1000
Trong Docker:
  docker exec -it parkinghub-backend-app uv run python scripts/seed_data.py --reset
"""
import argparse
import asyncio
import math
import os
import random
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.logging_config import setup_logging
setup_logging(service="seed", console_level=20)

import logging
logger = logging.getLogger(__name__)

OWNER_PASSWORD = "Owner@2026"
CUSTOMER_PASSWORD = "Customer@2026"
SEED_TAG = "seed_demo"          # created_by của mọi bản ghi do script tạo, để --reset xoá đúng phần này

# ── Khu vực ──────────────────────────────────────────────────────
# (mã, tên quận, tâm lat, lng, bán kính km, số bãi, hệ số giá, đường)
DISTRICTS = [
    ("q1", "Quận 1", 10.7756, 106.7004, 1.3, 26, 1.5,
     ["Nguyễn Huệ", "Lê Lợi", "Đồng Khởi", "Hai Bà Trưng", "Lý Tự Trọng", "Nam Kỳ Khởi Nghĩa", "Pasteur",
      "Tôn Đức Thắng", "Nguyễn Thị Minh Khai", "Lê Thánh Tôn", "Phạm Ngũ Lão", "Calmette"]),
    ("q3", "Quận 3", 10.7843, 106.6844, 1.2, 18, 1.3,
     ["Võ Văn Tần", "Nguyễn Đình Chiểu", "Điện Biên Phủ", "Cách Mạng Tháng 8", "Lê Văn Sỹ", "Trần Quốc Thảo",
      "Nam Kỳ Khởi Nghĩa", "Võ Thị Sáu"]),
    ("q4", "Quận 4", 10.7579, 106.7050, 0.9, 8, 1.1, ["Khánh Hội", "Hoàng Diệu", "Tôn Thất Thuyết", "Nguyễn Tất Thành"]),
    ("q5", "Quận 5", 10.7546, 106.6678, 1.1, 12, 1.0,
     ["Trần Hưng Đạo", "An Dương Vương", "Nguyễn Trãi", "Hùng Vương", "Châu Văn Liêm", "Lê Hồng Phong"]),
    ("q7", "Quận 7", 10.7324, 106.7218, 1.8, 16, 1.2,
     ["Nguyễn Văn Linh", "Nguyễn Thị Thập", "Huỳnh Tấn Phát", "Nguyễn Lương Bằng", "Tân Trào", "Lê Văn Lương"]),
    ("q10", "Quận 10", 10.7727, 106.6680, 1.0, 12, 1.0,
     ["3 Tháng 2", "Sư Vạn Hạnh", "Thành Thái", "Tô Hiến Thành", "Lý Thường Kiệt", "Ngô Gia Tự"]),
    ("bt", "Bình Thạnh", 10.8040, 106.7123, 1.6, 18, 1.1,
     ["Điện Biên Phủ", "Xô Viết Nghệ Tĩnh", "Nguyễn Hữu Cảnh", "Phan Đăng Lưu", "Bạch Đằng", "Ung Văn Khiêm"]),
    ("pn", "Phú Nhuận", 10.7994, 106.6802, 1.0, 12, 1.1,
     ["Phan Xích Long", "Nguyễn Văn Trỗi", "Hoàng Văn Thụ", "Phan Đình Phùng", "Huỳnh Văn Bánh"]),
    ("tb", "Tân Bình", 10.8020, 106.6528, 1.6, 14, 1.0,
     ["Cộng Hoà", "Trường Sơn", "Hoàng Văn Thụ", "Bạch Đằng", "Lý Thường Kiệt", "Út Tịch"]),
    ("td", "TP. Thủ Đức", 10.8040, 106.7400, 1.6, 14, 1.0,
     ["Xa Lộ Hà Nội", "Thảo Điền", "Quốc Hương", "Mai Chí Thọ", "Song Hành", "Trần Não"]),
]

# Loại hình: (tên hiển thị trong tên bãi, trọng số theo quận trung tâm / ngoại vi)
LOT_TYPE_WEIGHTS = {
    "central": {"office_basement": 26, "parking_building": 10, "apartment_basement": 8, "covered_garage": 10,
                "outdoor_commercial": 18, "street": 16, "residential": 8, "transit_hub": 4},
    "outer":   {"office_basement": 12, "parking_building": 8, "apartment_basement": 22, "covered_garage": 12,
                "outdoor_commercial": 22, "street": 6, "residential": 14, "transit_hub": 4},
}
CENTRAL = {"q1", "q3"}
LOT_NAME_PREFIX = {
    "office_basement": "Hầm toà nhà", "parking_building": "Nhà xe cao tầng", "apartment_basement": "Hầm chung cư",
    "covered_garage": "Nhà xe có mái", "outdoor_commercial": "Bãi xe", "street": "Điểm đỗ lòng đường",
    "residential": "Sân nhà", "transit_hub": "Bãi đầu mối",
}
CAPACITY_RANGE = {
    "office_basement": (60, 220), "parking_building": (200, 600), "apartment_basement": (80, 300),
    "covered_garage": (25, 80), "outdoor_commercial": (30, 120), "street": (12, 40),
    "residential": (2, 6), "transit_hub": (100, 300),
}
# Hệ số giá theo loại hình (nhân với giá mẫu và hệ số quận)
PRICE_FACTOR = {
    "office_basement": 1.15, "parking_building": 1.0, "apartment_basement": 0.9, "covered_garage": 0.85,
    "outdoor_commercial": 0.75, "street": 0.7, "residential": 0.6, "transit_hub": 0.8,
}
# Cấp tích hợp: trọng số 1..4
LEVEL_WEIGHTS = {
    "office_basement": [10, 30, 40, 20], "parking_building": [5, 20, 40, 35], "apartment_basement": [15, 40, 35, 10],
    "covered_garage": [25, 45, 25, 5], "outdoor_commercial": [35, 40, 20, 5], "street": [30, 30, 35, 5],
    "residential": [40, 55, 5, 0], "transit_hub": [10, 30, 40, 20],
}

FIRST_NAMES = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hải", "Hạnh", "Hiếu", "Hoa", "Hùng", "Khánh", "Khoa",
               "Lan", "Linh", "Long", "Mai", "Minh", "Nam", "Ngọc", "Nhung", "Phong", "Phúc", "Quân", "Quyên",
               "Sơn", "Tâm", "Thảo", "Thành", "Trang", "Trung", "Tú", "Tuấn", "Vân", "Việt", "Vy", "Yến"]
LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Ngô", "Dương"]
MIDDLE = ["Văn", "Thị", "Minh", "Hoàng", "Thanh", "Ngọc", "Đức", "Thu", "Gia", "Quốc"]
CARS = [("Toyota", "Vios", "sedan"), ("Toyota", "Corolla Cross", "suv"), ("Hyundai", "Accent", "sedan"),
        ("Hyundai", "Santa Fe", "suv"), ("Kia", "Seltos", "suv"), ("Kia", "Morning", "hatchback"),
        ("Mazda", "CX-5", "suv"), ("Mazda", "3", "sedan"), ("Honda", "City", "sedan"), ("Honda", "CR-V", "suv"),
        ("Ford", "Ranger", "truck"), ("Ford", "Everest", "suv"), ("VinFast", "VF 5", "hatchback"),
        ("VinFast", "VF 8", "suv"), ("Mitsubishi", "Xpander", "van"), ("Mercedes-Benz", "C 200", "sedan")]
COLORS = ["Trắng", "Đen", "Bạc", "Xám", "Đỏ", "Xanh"]
REVIEW_GOOD = ["Bãi rộng, dễ vào", "Bảo vệ hướng dẫn nhiệt tình", "Đến nơi là có chỗ đúng như đặt",
               "Giá hợp lý, gần chỗ làm", "Vào ra nhanh, không phải chờ", "Hầm sạch, đủ sáng"]
REVIEW_BAD = ["Lối vào hơi hẹp, khó quay đầu", "Đến nơi phải chờ khá lâu mới có chỗ",
              "Giá cao hơn so với khu vực", "Thiếu đèn ở góc trong"]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def jitter(lat: float, lng: float, radius_km: float):
    r = radius_km * math.sqrt(random.random())
    a = random.uniform(0, 2 * math.pi)
    return (round(lat + (r / 111.0) * math.cos(a), 6),
            round(lng + (r / (111.0 * math.cos(math.radians(lat)))) * math.sin(a), 6))


def round_k(v: float, step: int = 1000) -> int:
    return int(max(step, round(v / step) * step))


def person_name() -> str:
    return f"{random.choice(LAST_NAMES)} {random.choice(MIDDLE)} {random.choice(FIRST_NAMES)}"


def plate(i: int) -> str:
    return f"{random.choice(['51', '50', '59'])}{random.choice('ABCDEFGHK')}-{10000 + (i * 7919) % 89999:05d}"


# ── Thuộc tính bãi theo loại hình ────────────────────────────────

def make_attributes(lot_type: str) -> dict:
    r = random.random
    cover = {"office_basement": "basement", "apartment_basement": "basement", "parking_building": "full_roof",
             "covered_garage": random.choice(["full_roof", "partial_roof"]), "transit_hub": random.choice(["full_roof", "open"]),
             }.get(lot_type, "open")
    premium = lot_type in ("office_basement", "parking_building", "transit_hub")
    a = {
        "cover": cover,
        "max_height_m": round(random.choice([1.9, 2.0, 2.1, 2.2, 2.4]), 1) if cover in ("basement", "full_roof") else None,
        "guard": "24h" if premium or (lot_type == "apartment_basement" and r() < 0.7) else random.choice(["none", "hours", "hours", "24h"]),
        "cctv": "full" if premium else random.choice(["none", "partial", "partial", "full"]),
        "ev_chargers": {"count": random.choice([2, 4, 6, 8]), "power_kw": random.choice([7, 11, 22, 60]), "connectors": ["Type 2"]}
        if (premium and r() < 0.6) or (lot_type == "apartment_basement" and r() < 0.35) else {"count": 0},
        "flood_risk": "none" if cover in ("full_roof",) or lot_type == "parking_building" else
        random.choices(["none", "heavy_rain", "frequent"], [6, 3, 1])[0],
        "parking_style": "stacked" if lot_type in ("residential", "street") and r() < 0.4 else
        ("attendant" if r() < 0.3 else "self"),
        "lighting": "good" if premium or cover == "basement" else random.choice(["basic", "basic", "good", "poor"]),
        "surface": "concrete" if cover != "open" else random.choice(["asphalt", "concrete", "gravel"]),
        "fire_safety": premium or cover == "basement" or r() < 0.4,
        "restroom": premium or r() < 0.3,
        "payment_methods": ["cash", "transfer"] + (["card"] if premium else []),
    }
    if a["guard"] == "hours":
        a["guard_hours"] = "06:00 – 22:00"
    return a


def make_hours(lot_type: str, is_24h: bool) -> dict:
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if is_24h:
        return {"is_24h": True, **{d: {"open": "00:00", "close": "23:59"} for d in days}}
    open_, close = random.choice([("06:00", "22:00"), ("05:30", "23:00"), ("07:00", "21:00")])
    hours = {"is_24h": False, **{d: {"open": open_, "close": close} for d in days}}
    if lot_type == "office_basement" and random.random() < 0.4:
        hours["sunday"] = {"open": open_, "close": close, "closed": True}
    return hours


def make_pricing(stype: dict, factor: float) -> dict:
    p = dict(stype["default_pricing"])
    p["peak_rules"] = list(p.get("peak_rules") or [])
    if p.get("mode") == "block":
        p["first_block_price"] = round_k(p["first_block_price"] * factor)
        p["next_block_price"] = round_k(p["next_block_price"] * factor)
        if p.get("daily_cap"):
            p["daily_cap"] = round_k(p["daily_cap"] * factor, 10000)
    else:
        p["flat_price"] = round_k(p["flat_price"] * factor, 10000 if p["flat_price"] >= 500000 else 1000)
    return p


# ── Main ─────────────────────────────────────────────────────────

async def main(args):
    random.seed(args.seed)
    from app.db.mongo import init_mongo, get_motor_client
    from app.api.auth.auth_utils import hash_password, seed_super_admin
    from app.api.booking.booking_models import BookingModel
    from app.api.capacity.capacity_models import CapacitySnapshotModel
    from app.api.capacity.occupancy_profile_utils import occupancy_profile
    from app.api.garage.garage_classification_utils import compute_grade, suggest_checklist
    from app.api.garage.garage_models import GarageModel
    from app.api.garage.garage_stats_utils import recompute_garage_stats
    from app.api.garage_service.garage_service_models import GarageServiceModel
    from app.api.garage_service.pricing_utils import quote_price, display_price, to_local, LOCAL_TZ
    from app.api.service_type.service_type_models import ServiceTypeModel
    from app.api.service_type.service_type_utils import seed_default_service_types
    from app.api.tenant.tenant_models import TenantModel
    from app.api.user.user_models import UserModel
    from app.api.vehicle.vehicle_models import VehicleModel

    init_mongo()
    _ = get_motor_client()
    from main import ensure_indexes
    await ensure_indexes()
    await seed_super_admin()
    await seed_default_service_types()
    stypes = {s["code"]: s async for s in ServiceTypeModel.collection.find({})}

    if args.reset:
        logger.info("Xoá dữ liệu demo cũ…")
        demo_garages = [g["_id"] async for g in GarageModel.collection.find({"created_by": SEED_TAG}, {"_id": 1})]
        for coll, q in [
            (BookingModel, {"garage_id": {"$in": demo_garages}}),
            (CapacitySnapshotModel, {"garage_id": {"$in": demo_garages}}),
            (GarageServiceModel, {"garage_id": {"$in": demo_garages}}),
            (GarageModel, {"created_by": SEED_TAG}),
            (TenantModel, {"created_by": SEED_TAG}),
            (VehicleModel, {"created_by": SEED_TAG}),
            (UserModel, {"created_by": SEED_TAG}),
        ]:
            r = await coll.collection.delete_many(q)
            logger.info(f"  {coll.collection.name}: -{r.deleted_count}")
    elif await GarageModel.collection.count_documents({"created_by": SEED_TAG}):
        logger.error("Đã có dữ liệu demo. Chạy lại với --reset để seed lại.")
        return

    now = now_utc()
    owner_hash = hash_password(OWNER_PASSWORD)
    customer_hash = hash_password(CUSTOMER_PASSWORD)
    meta = {"created_at": now, "updated_at": now, "created_by": SEED_TAG, "updated_by": SEED_TAG}

    # ── 1. Bãi đỗ + chủ bãi ──
    scale = args.lots / sum(d[5] for d in DISTRICTS)
    garages, tenants, owners, services = [], [], [], []
    used_slugs = set()
    for code, dname, clat, clng, radius, count, dfactor, streets in DISTRICTS:
        n = max(1, round(count * scale))
        weights = LOT_TYPE_WEIGHTS["central" if code in CENTRAL else "outer"]
        for i in range(1, n + 1):
            lot_type = random.choices(list(weights), list(weights.values()))[0]
            street = random.choice(streets)
            number = random.randint(1, 350)
            name = f"{LOT_NAME_PREFIX[lot_type]} {street}" + (f" {number}" if lot_type in ("residential", "outdoor_commercial") else "")
            slug = slugify(f"{name}-{code}")
            while slug in used_slugs:
                slug = f"{slug}-{random.randint(2, 99)}"
            used_slugs.add(slug)
            lat, lng = jitter(clat, clng, radius)
            attrs = make_attributes(lot_type)
            level = random.choices([1, 2, 3, 4], LEVEL_WEIGHTS[lot_type])[0]
            if lot_type == "residential":
                level = min(level, 2)
            lo, hi = CAPACITY_RANGE[lot_type]
            total = random.randint(lo, hi)
            is_24h = lot_type in ("parking_building", "apartment_basement", "transit_hub") or random.random() < 0.25
            status = random.choices(["active", "pending_review", "suspended"], [92, 6, 2])[0]
            owner_username = f"owner_{code}_{i:02d}"

            svc_codes = ["park_hourly"]
            if is_24h or random.random() < 0.5:
                svc_codes.append("park_overnight")
            if lot_type not in ("street",) and random.random() < 0.6:
                svc_codes.append("park_daily")
            if lot_type in ("office_basement", "parking_building", "covered_garage", "outdoor_commercial") and random.random() < 0.6:
                svc_codes.append("park_workday")
            if lot_type not in ("street",) and random.random() < 0.55:
                svc_codes.append("park_monthly")
            if attrs["ev_chargers"]["count"]:
                svc_codes.append("ev_charging")
            if lot_type in ("office_basement", "parking_building", "covered_garage") and random.random() < 0.3:
                svc_codes.append("car_wash")
            if lot_type in ("office_basement", "transit_hub") and random.random() < 0.2:
                svc_codes.append("valet")

            reservable = {"street": 0.3, "residential": 1.0}.get(lot_type, random.choice([0.3, 0.4, 0.5, 0.6]))
            monthly = int(total * random.choice([0, 0.1, 0.2, 0.3])) if "park_monthly" in svc_codes else 0
            g = {
                "_id": None, "tenant_id": slug, "name": name, "slug": slug,
                "location": {"type": "Point", "coordinates": [lng, lat]},
                "entrance_location": {"type": "Point", "coordinates": [round(lng + random.uniform(-0.0003, 0.0003), 6),
                                                                       round(lat + random.uniform(-0.0003, 0.0003), 6)]},
                "address": {"street": f"{number} {street}", "ward": "", "district": dname, "city": "TP. Hồ Chí Minh"},
                "lot_type": lot_type, "integration_level": level,
                "capacity": {"total_spots": total, "walk_in_spots": max(0, total - monthly),
                             "monthly_spots": monthly, "reservable_ratio": reservable,
                             "grace_minutes": random.choice([15, 15, 20, 30])},
                "attributes": attrs,
                "occupancy": {"occupied": 0, "source": "manual", "updated_at": None},
                "operating_hours": make_hours(lot_type, is_24h),
                "services_offered": svc_codes,
                "photos": [],
                "description": f"{LOT_NAME_PREFIX[lot_type]} tại {street}, {dname}. Dữ liệu demo.",
                "contacts": {"phone": f"09{random.randint(10000000, 99999999)}", "manager_name": person_name()},
                "status": status, "is_verified": False,
                "is_accepting_bookings": status == "active" and random.random() > 0.03,
                "grade": 1, "grade_score": 0, "grade_assessment": {}, "quality_score": 0.0, "next_inspection_at": None,
                "stats": {}, **meta,
            }
            # Kiểm định: bãi đang hoạt động cấp ≥ 2 phần lớn đã được kiểm định
            if status == "active" and (level >= 2 or random.random() < 0.3):
                items = suggest_checklist(g)
                for k in items:            # người kiểm định chỉnh vài mục so với khai báo
                    if random.random() < 0.08:
                        items[k] = not items[k]
                gr = compute_grade(items)
                assessed = now - timedelta(days=random.randint(5, 170))
                g.update({
                    "grade": gr["grade"], "grade_score": gr["score"], "is_verified": True,
                    "grade_assessment": {"items": items, "note": "", "assessed_at": assessed, "assessed_by": "superadmin"},
                    "next_inspection_at": assessed + timedelta(days=180),
                })
            g.pop("_id")
            garages.append(g)
            tenants.append({
                "tenant_id": slug, "name": name, "slug": slug, "type": "garage", "status": "active",
                "contact": {"phone": g["contacts"]["phone"], "email": f"{owner_username}@example.com",
                            "address": f"{number} {street}, {dname}, TP. Hồ Chí Minh"},
                "subscription_plan": "free",
                "settings": {"timezone": "Asia/Ho_Chi_Minh", "currency": "VND", "language": "vi"}, **meta,
            })
            owners.append({
                "tenant_id": slug, "username": owner_username, "email": f"{owner_username}@example.com",
                "phone": g["contacts"]["phone"], "password_hash": owner_hash, "name": person_name(),
                "role": "garage_owner", "is_active": True, "allowed_tenant_ids": [],
                "customer_profile": {}, "staff_profile": {}, "last_login": None, **meta,
            })
            factor = dfactor * PRICE_FACTOR[lot_type] * random.uniform(0.9, 1.1)
            for sc in svc_codes:
                pricing = make_pricing(stypes[sc], factor if stypes[sc]["category"] != "addon" else random.uniform(0.9, 1.2))
                services.append({
                    "tenant_id": slug, "_slug": slug, "service_type_code": sc,
                    "price": display_price(pricing), "pricing": pricing,
                    "estimated_duration_minutes": stypes[sc].get("estimated_duration_minutes", 60),
                    "is_available": True, "note": "", **meta,
                })

    res = await GarageModel.collection.insert_many(garages)
    for g, oid in zip(garages, res.inserted_ids):
        g["_id"] = oid
    by_slug = {g["slug"]: g for g in garages}
    await TenantModel.collection.insert_many(tenants)
    ures = await UserModel.collection.insert_many(owners)
    for t_slug, uid in zip([o["tenant_id"] for o in owners], ures.inserted_ids):
        await TenantModel.collection.update_one({"slug": t_slug}, {"$set": {"owner_user_id": str(uid)}})
    for s in services:
        s["garage_id"] = by_slug[s.pop("_slug")]["_id"]
    await GarageServiceModel.collection.insert_many(services)
    svc_map = {(s["garage_id"], s["service_type_code"]): s for s in services}
    logger.info(f"Bãi: {len(garages)} · dịch vụ: {len(services)}")

    # ── 2. Tài xế + xe ──
    customers, vehicles = [], []
    for i in range(1, args.customers + 1):
        uname = f"customer_{i:02d}"
        customers.append({
            "tenant_id": "platform", "username": uname, "email": f"{uname}@example.com",
            "phone": f"09{random.randint(10000000, 99999999)}", "password_hash": customer_hash,
            "name": person_name(), "role": "customer", "is_active": True, "allowed_tenant_ids": [],
            "customer_profile": {}, "staff_profile": {}, "last_login": None, **meta,
        })
    cres = await UserModel.collection.insert_many(customers)
    plate_seq = 0
    cust_plates = {}
    for c, oid in zip(customers, cres.inserted_ids):
        c["_id"] = oid
        cust_plates[oid] = []
        for k in range(random.choice([1, 1, 2])):
            brand, model, body = random.choice(CARS)
            plate_seq += 1
            p = plate(plate_seq + random.randint(0, 3) * 1000)
            while any(v["license_plate"] == p for v in vehicles):
                plate_seq += 1
                p = plate(plate_seq)
            vehicles.append({
                "tenant_id": "platform", "owner_user_id": str(oid), "license_plate": p, "brand": brand, "model": model,
                "year": random.randint(2016, 2025), "color": random.choice(COLORS), "vehicle_type": "standard",
                "body_type": body, "size_class": "large" if body in ("suv", "truck", "van") else "medium",
                "minimum_garage_tier": 1, "vetc_linked": False, "is_default": k == 0, "is_active": True, **meta,
            })
            cust_plates[oid].append(p)
    await VehicleModel.collection.insert_many(vehicles)
    plate_vehicle = {v["license_plate"]: v for v in vehicles}
    vres = await VehicleModel.collection.find({"created_by": SEED_TAG}, {"license_plate": 1}).to_list(length=None)
    for v in vres:
        plate_vehicle[v["license_plate"]]["_id"] = v["_id"]
    logger.info(f"Tài xế: {len(customers)} · xe: {len(vehicles)}")

    # ── 3. Lượt đặt ──
    bookable = [g for g in garages if g["status"] == "active" and g["integration_level"] >= 2]
    lot_weight = [math.sqrt(g["capacity"]["total_spots"]) * (1.5 if g["integration_level"] >= 3 else 1) for g in bookable]
    # Mỗi tài xế có 2–4 bãi quen (tạo khách quay lại)
    favorites = {c["_id"]: random.choices(bookable, lot_weight, k=random.randint(2, 4)) for c in customers}
    seq = 0

    def code() -> str:
        nonlocal seq
        seq += 1
        return f"PH-SEED-{seq:05d}"

    def svc_for(g: dict) -> str:
        opts = [c for c in g["services_offered"] if c in ("park_hourly", "park_overnight", "park_daily")]
        return random.choices(opts, [8 if c == "park_hourly" else 2 for c in opts])[0]

    def window(code_: str, day_local: datetime):
        if code_ == "park_overnight":
            s = day_local.replace(hour=random.choice([18, 19, 20]), minute=0)
            return s, s.replace(hour=7) + timedelta(days=1)
        if code_ == "park_daily":
            s = day_local.replace(hour=random.randint(6, 10), minute=random.choice([0, 30]))
            return s, s + timedelta(days=random.choice([1, 1, 2, 3]))
        s = day_local.replace(hour=random.choices(range(6, 22), [2, 6, 9, 6, 4, 4, 5, 4, 4, 4, 5, 6, 7, 6, 4, 2])[0],
                              minute=random.choice([0, 15, 30, 45]))
        return s, s + timedelta(minutes=random.choice([60, 90, 120, 120, 180, 240, 300, 480]))

    def build(g, cust, svc, start, end, status, source="app"):
        gsvc = svc_map[(g["_id"], svc)]
        quote = quote_price(gsvc["pricing"], start, end)["amount"]
        grace = start + timedelta(minutes=g["capacity"]["grace_minutes"])
        created = start - timedelta(hours=random.uniform(0.5, 48)) if source != "walk_in" else start
        p = random.choice(cust_plates[cust["_id"]]) if cust else plate(random.randint(1, 99999))
        stamps = {"created_at": created}
        if g["integration_level"] >= 3 or status not in ("pending", "rejected", "expired"):
            stamps["reserved_at"] = created + timedelta(minutes=random.randint(0, 20) if g["integration_level"] == 2 else 0)
        b = {
            "tenant_id": g["tenant_id"], "booking_code": code(),
            "customer_id": cust["_id"] if cust else None, "garage_id": g["_id"],
            "vehicle_id": plate_vehicle.get(p, {}).get("_id") if cust else None,
            "license_plate": p, "service_type_code": svc, "quoted_price": int(quote), "final_price": None,
            "payment_status": "unpaid", "payment_method": "", "start_time": start, "end_time": end,
            "grace_until": grace, "status": status, "source": source, "timestamps": stamps,
            "matching_context": {}, "feedback": {}, "cancellation_reason": "", "cancelled_by": "",
            "created_at": created, "updated_at": created, "created_by": SEED_TAG, "updated_by": SEED_TAG,
        }
        if status in ("checked_in", "checked_out"):
            cin = max(created, start + timedelta(minutes=random.randint(-20, 25)))
            stamps["checked_in_at"] = cin
        if status == "checked_out":
            cout = end + timedelta(minutes=random.randint(-40, 50))
            cout = max(cout, stamps["checked_in_at"] + timedelta(minutes=20))
            stamps["checked_out_at"] = cout
            billed_from = stamps["checked_in_at"] if source == "walk_in" else max(stamps["checked_in_at"], start)
            final = quote_price(gsvc["pricing"], billed_from, cout)["amount"]
            if gsvc["pricing"].get("mode") == "flat":
                final = max(final, int(quote))
            b["final_price"] = int(final)
            if random.random() < 0.93:
                b.update(payment_status="paid", payment_method=random.choice(["cash", "transfer", "transfer"]))
                stamps["paid_at"] = cout
            if cust and random.random() < 0.4:
                rating = random.choices([5, 4, 3, 2, 1], [50, 30, 10, 6, 4])[0]
                b["feedback"] = {"rating": rating, "quick_feedback": "thumbs_up" if rating >= 4 else "thumbs_down",
                                 "comment": random.choice(REVIEW_GOOD if rating >= 4 else REVIEW_BAD) if random.random() < 0.6 else "",
                                 "complaint": rating <= 2 and random.random() < 0.5}
        elif status == "cancelled":
            b["cancelled_by"] = "garage" if random.random() < 0.15 else "customer"
            b["cancellation_reason"] = "Bãi hết chỗ đột xuất" if b["cancelled_by"] == "garage" else "Đổi kế hoạch"
            stamps["cancelled_at"] = created + (start - created) * random.random()
        elif status == "no_show":
            stamps["no_show_at"] = grace + timedelta(minutes=5)
        elif status == "rejected":
            stamps["rejected_at"] = created + timedelta(minutes=random.randint(5, 60))
            b["cancellation_reason"] = "Bãi đã kín trong khung giờ này"
        elif status == "expired":
            stamps["expired_at"] = start
        return b

    bookings = []
    target_past = args.bookings
    for _ in range(target_past):
        cust = random.choice(customers)
        g = random.choice(favorites[cust["_id"]]) if random.random() < 0.6 else random.choices(bookable, lot_weight)[0]
        svc = svc_for(g)
        day = to_local(now - timedelta(days=random.uniform(0.3, 90)))
        start, end = window(svc, day.replace(second=0, microsecond=0))
        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
        if end > now - timedelta(minutes=30):
            continue
        if g["integration_level"] == 2 and random.random() < 0.06:
            status = random.choice(["rejected", "expired"])
        else:
            status = random.choices(["checked_out", "cancelled", "no_show"], [84, 10, 6])[0]
        bookings.append(build(g, cust, svc, start, end, status))

    # Xe vãng lai (không qua app) ≈ 35% số lượt
    for _ in range(int(target_past * 0.35)):
        g = random.choices(bookable, lot_weight)[0]
        day = to_local(now - timedelta(days=random.uniform(0.3, 90)))
        start, end = window("park_hourly", day.replace(second=0, microsecond=0))
        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
        if end > now - timedelta(minutes=30):
            continue
        bookings.append(build(g, None, "park_hourly", start, end, "checked_out", source="walk_in"))

    # Hiện tại: xe đang trong bãi + lượt sắp tới
    inside_count = {}
    for g in bookable:
        # Lượt đã xong từ sáng tới giờ (để "doanh thu hôm nay" có số liệu)
        today_start = to_local(now).replace(hour=6, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
        for _ in range(random.randint(2, 8)):
            span = (now - timedelta(hours=1) - today_start).total_seconds()
            if span <= 0:
                break
            start = today_start + timedelta(seconds=random.uniform(0, span))
            end = min(start + timedelta(minutes=random.choice([45, 60, 90, 120, 180])), now - timedelta(minutes=10))
            if end <= start + timedelta(minutes=20):
                continue
            walk = random.random() < 0.4
            bookings.append(build(g, None if walk else random.choice(customers), "park_hourly", start, end,
                                  "checked_out", source="walk_in" if walk else "app"))
        for _ in range(random.randint(1, 3)):
            cust = random.choice(customers)
            start = now - timedelta(minutes=random.randint(20, 240))
            bookings.append(build(g, cust, "park_hourly", start, start + timedelta(hours=random.choice([2, 3, 4, 6])), "checked_in"))
            inside_count[g["_id"]] = inside_count.get(g["_id"], 0) + 1
        for _ in range(random.randint(0, 2)):
            start = now - timedelta(minutes=random.randint(10, 120))
            bookings.append(build(g, None, "park_hourly", start, start + timedelta(hours=3), "checked_in", source="walk_in"))
            inside_count[g["_id"]] = inside_count.get(g["_id"], 0) + 1
    for _ in range(max(40, args.customers * 2)):
        cust = random.choice(customers)
        g = random.choice(favorites[cust["_id"]])
        svc = svc_for(g)
        start = (now + timedelta(minutes=random.randint(20, 60 * 24 * 5))).replace(second=0, microsecond=0)
        start = start.replace(minute=(start.minute // 15) * 15)
        _, end = window(svc, to_local(start))
        end = end.astimezone(timezone.utc)
        if end <= start:
            end = start + timedelta(hours=2)
        status = "reserved" if g["integration_level"] >= 3 or random.random() < 0.5 else "pending"
        bookings.append(build(g, cust, svc, start, end, status))

    bookings.sort(key=lambda b: b["start_time"])
    for i in range(0, len(bookings), 2000):
        await BookingModel.collection.insert_many(bookings[i:i + 2000])
    logger.info(f"Lượt đặt: {len(bookings)} (trong đó vãng lai {sum(1 for b in bookings if b['source'] == 'walk_in')})")

    # ── 4. Chỗ trống hiện tại + snapshot 8 tuần ──
    tracked = [g for g in garages if g["status"] == "active" and g["integration_level"] >= 2]
    snaps = []
    hour_now = now.replace(minute=0, second=0, microsecond=0)
    for g in tracked:
        total = g["capacity"]["total_spots"]
        bias = random.uniform(-0.12, 0.12)       # mỗi bãi đông/vắng hơn trung bình loại hình một chút
        for h in range(args.weeks * 7 * 24, 0, -1):
            ts = hour_now - timedelta(hours=h)
            loc = to_local(ts)
            rate = occupancy_profile(g["lot_type"], loc.hour, loc.weekday()) + bias + random.gauss(0, 0.06)
            rate = max(0.0, min(1.0, rate))
            occ = round(rate * total)
            snaps.append({
                "tenant_id": g["tenant_id"], "garage_id": g["_id"], "timestamp": ts,
                "total_spots": total, "occupied": occ, "held": 0, "available": total - occ,
                "occupancy_rate": round(occ / total, 3),
                "source": "simulated" if g["integration_level"] >= 3 else "manual",
                "hour_of_day": loc.hour, "day_of_week": loc.weekday(), **meta,
            })
        loc = to_local(now)
        cur = occupancy_profile(g["lot_type"], loc.hour, loc.weekday()) + bias
        occupied = max(inside_count.get(g["_id"], 0), min(total, round(max(0.0, cur) * total)))
        updated = now if g["integration_level"] >= 3 else now - timedelta(minutes=random.randint(3, 90))
        await GarageModel.collection.update_one({"_id": g["_id"]}, {"$set": {"occupancy": {
            "occupied": occupied, "source": "simulated" if g["integration_level"] >= 3 else "manual", "updated_at": updated,
        }}})
        if len(snaps) >= 20000:
            await CapacitySnapshotModel.collection.insert_many(snaps)
            snaps = []
    if snaps:
        await CapacitySnapshotModel.collection.insert_many(snaps)
    logger.info(f"Snapshot: {len(tracked)} bãi × {args.weeks} tuần")

    # ── 5. Chỉ số vận hành + điểm chất lượng ──
    for g in bookable:
        await recompute_garage_stats(g["_id"])
    logger.info("Đã tính lại chỉ số vận hành")

    logger.info("──────────────────────────────────────────")
    logger.info(f"Chủ bãi : owner_<quận>_<nn>, ví dụ {owners[0]['username']}  / {OWNER_PASSWORD}")
    logger.info(f"Tài xế  : customer_01 … customer_{args.customers:02d}  / {CUSTOMER_PASSWORD}")
    logger.info("Admin   : SUPER_ADMIN_USERNAME / SUPER_ADMIN_PASSWORD trong .env")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed dữ liệu demo Parking HUB")
    ap.add_argument("--reset", action="store_true", help="Xoá dữ liệu demo cũ (created_by=seed_demo) trước khi seed")
    ap.add_argument("--lots", type=int, default=150)
    ap.add_argument("--customers", type=int, default=40)
    ap.add_argument("--bookings", type=int, default=2300, help="Số lượt qua app trong quá khứ (vãng lai cộng thêm ~35%)")
    ap.add_argument("--weeks", type=int, default=8, help="Số tuần snapshot lấp đầy")
    ap.add_argument("--seed", type=int, default=2026)
    asyncio.run(main(ap.parse_args()))
