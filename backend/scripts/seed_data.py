#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed Data Script
================
Tạo dữ liệu mẫu cho toàn bộ hệ thống, phục vụ phát triển và demo.

Toàn bộ dữ liệu trong file này là dữ liệu giả, chỉ toạ độ là toạ độ thực tại TP.HCM.

Collections được seed:
  - tenants         (30 chủ bãi)
  - users           (30 chủ bãi + 6 khách hàng)
  - garages         (30 bãi đỗ xe tại Q1, Q3, Q5, Q7, toạ độ thực TP.HCM)
  - garage_services (mỗi bãi 2 tới 4 dịch vụ kèm giá)
  - vehicles        (2-3 xe/customer)
  - bookings        (~120 bookings phân bổ 90 ngày qua)
  - capacity_snapshots (4 tuần dữ liệu giờ để fuel charts)

Usage:
  cd backend
  uv run python scripts/seed_data.py            # additive (skip existing)
  uv run python scripts/seed_data.py --reset    # xoá data cũ trước
"""
import asyncio
import argparse
import sys
import os
import random
from datetime import datetime, timedelta, timezone
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYTHONPATH", ".")

from dotenv import load_dotenv
load_dotenv()

from app.core.logging_config import setup_logging
setup_logging(service="seed", console_level=20)

import logging
logger = logging.getLogger(__name__)

# ── Time helpers ────────────────────────────────────────────────

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def days_ago(n: float) -> datetime:
    return now_utc() - timedelta(days=n)

def rand_dt(days_back_max=90, hour_min=7, hour_max=20) -> datetime:
    base = now_utc() - timedelta(
        days=random.uniform(0.5, days_back_max),
        hours=0,
    )
    return base.replace(
        hour=random.randint(hour_min, hour_max),
        minute=random.choice([0, 15, 30, 45]),
        second=0, microsecond=0,
    )

def gen_booking_code(seq: int) -> str:
    d = now_utc().strftime("%Y%m%d")
    return f"WM-{d}-{seq:04d}"


# ─────────────────────────────────────────────────────────────────
# DỮ LIỆU BÃI ĐỖ MẪU — 30 bãi tại Q1, Q3, Q5, Q7
# ─────────────────────────────────────────────────────────────────
# tier 1=Basic, 2=Standard, 3=Pro, 4=Elite
# Toạ độ là GPS thực tế gần đúng tại TP.HCM. Tên và số liệu là dữ liệu giả.

GARAGES_DATA = [

    # ═══════════════════════════════════════════════════════════
    # QUẬN 1  (8 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "bai-do-q1-01",
        "name": "Hầm đỗ xe Nguyễn Huệ Q1",
        "district": "Quận 1", "street": "25 Nguyễn Huệ", "ward": "Phường Bến Nghé",
        "lat": 10.7769, "lng": 106.7009,
        "tier": 4, "tier_score": 91.5, "total_bays": 6,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 93, "process_score": 90, "staff_score": 88, "capacity_score": 95, "reliability_score": 91},
        "owner": {"username": "owner_q1_01", "name": "Trần Minh Khoa", "email": "owner.q1.01@example.com", "phone": "0901111001"},
        "stats": {"total_services": 3250, "avg_rating": 4.85, "retention_rate": 0.72, "complaint_rate": 0.01, "on_time_rate": 0.94, "avg_actual_processing_minutes": 42},
        "in_service": 4, "waiting": 2, "wait_minutes": 10,
    },
    {
        "slug": "bai-do-q1-02",
        "name": "Hầm đỗ xe Lê Lợi Q1",
        "district": "Quận 1", "street": "47 Lê Lợi", "ward": "Phường Bến Thành",
        "lat": 10.7750, "lng": 106.7003,
        "tier": 4, "tier_score": 87.2, "total_bays": 5,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 91, "process_score": 85, "staff_score": 86, "capacity_score": 84, "reliability_score": 90},
        "owner": {"username": "owner_q1_02", "name": "Nguyễn Bảo Long", "email": "owner.q1.02@example.com", "phone": "0901111011"},
        "stats": {"total_services": 2780, "avg_rating": 4.75, "retention_rate": 0.68, "complaint_rate": 0.02, "on_time_rate": 0.92, "avg_actual_processing_minutes": 50},
        "in_service": 3, "waiting": 1, "wait_minutes": 8,
    },
    {
        "slug": "bai-do-q1-03",
        "name": "Hầm đỗ xe Nam Kỳ Khởi Nghĩa Q1",
        "district": "Quận 1", "street": "118 Nam Kỳ Khởi Nghĩa", "ward": "Phường Bến Thành",
        "lat": 10.7820, "lng": 106.6972,
        "tier": 3, "tier_score": 74.8, "total_bays": 5,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 78, "process_score": 72, "staff_score": 75, "capacity_score": 80, "reliability_score": 69},
        "owner": {"username": "owner_q1_03", "name": "Lê Hoàng Nam", "email": "owner.q1.03@example.com", "phone": "0901111012"},
        "stats": {"total_services": 1920, "avg_rating": 4.5, "retention_rate": 0.58, "complaint_rate": 0.03, "on_time_rate": 0.87, "avg_actual_processing_minutes": 35},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },
    {
        "slug": "bai-do-q1-04",
        "name": "Hầm đỗ xe Đinh Tiên Hoàng Q1",
        "district": "Quận 1", "street": "15 Đinh Tiên Hoàng", "ward": "Phường Đakao",
        "lat": 10.7837, "lng": 106.7028,
        "tier": 4, "tier_score": 89.0, "total_bays": 4,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 95, "process_score": 88, "staff_score": 90, "capacity_score": 80, "reliability_score": 92},
        "owner": {"username": "owner_q1_04", "name": "Phạm Anh Tuấn", "email": "owner.q1.04@example.com", "phone": "0901111013"},
        "stats": {"total_services": 1450, "avg_rating": 4.92, "retention_rate": 0.80, "complaint_rate": 0.005, "on_time_rate": 0.96, "avg_actual_processing_minutes": 120},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "bai-do-q1-05",
        "name": "Hầm đỗ xe Nguyễn Du Q1",
        "district": "Quận 1", "street": "88 Nguyễn Du", "ward": "Phường Bến Nghé",
        "lat": 10.7761, "lng": 106.6984,
        "tier": 3, "tier_score": 70.5, "total_bays": 6,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 70, "staff_score": 72, "capacity_score": 78, "reliability_score": 60},
        "owner": {"username": "owner_q1_05", "name": "Trần Thị Thu", "email": "owner.q1.05@example.com", "phone": "0901111014"},
        "stats": {"total_services": 2100, "avg_rating": 4.3, "retention_rate": 0.52, "complaint_rate": 0.04, "on_time_rate": 0.85, "avg_actual_processing_minutes": 28},
        "in_service": 3, "waiting": 2, "wait_minutes": 18,
    },
    {
        "slug": "bai-do-q1-06",
        "name": "Hầm đỗ xe Hai Bà Trưng Q1",
        "district": "Quận 1", "street": "22 Hai Bà Trưng", "ward": "Phường Đakao",
        "lat": 10.7815, "lng": 106.7012,
        "tier": 3, "tier_score": 75.3, "total_bays": 4,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 80, "process_score": 75, "staff_score": 78, "capacity_score": 68, "reliability_score": 75},
        "owner": {"username": "owner_q1_06", "name": "Vũ Đình Hưng", "email": "owner.q1.06@example.com", "phone": "0901111015"},
        "stats": {"total_services": 1680, "avg_rating": 4.55, "retention_rate": 0.60, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 55},
        "in_service": 2, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "bai-do-q1-07",
        "name": "Bãi đỗ có mái che Lý Tự Trọng Q1",
        "district": "Quận 1", "street": "233 Lý Tự Trọng", "ward": "Phường Cầu Kho",
        "lat": 10.7760, "lng": 106.6996,
        "tier": 2, "tier_score": 55.0, "total_bays": 8,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 58, "process_score": 58, "staff_score": 52, "capacity_score": 60, "reliability_score": 47},
        "owner": {"username": "owner_q1_07", "name": "Đặng Văn Sơn", "email": "owner.q1.07@example.com", "phone": "0901111016"},
        "stats": {"total_services": 4200, "avg_rating": 3.9, "retention_rate": 0.40, "complaint_rate": 0.06, "on_time_rate": 0.78, "avg_actual_processing_minutes": 18},
        "in_service": 5, "waiting": 3, "wait_minutes": 25,
    },
    {
        "slug": "bai-do-q1-08",
        "name": "Bãi đỗ có mái che Phạm Ngũ Lão Q1",
        "district": "Quận 1", "street": "166 Phạm Ngũ Lão", "ward": "Phường Phạm Ngũ Lão",
        "lat": 10.7689, "lng": 106.6965,
        "tier": 2, "tier_score": 58.5, "total_bays": 5,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 1.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 62, "process_score": 58, "staff_score": 60, "capacity_score": 55, "reliability_score": 57},
        "owner": {"username": "owner_q1_08", "name": "Bùi Thị Lan Anh", "email": "owner.q1.08@example.com", "phone": "0901111017"},
        "stats": {"total_services": 1350, "avg_rating": 4.1, "retention_rate": 0.45, "complaint_rate": 0.05, "on_time_rate": 0.82, "avg_actual_processing_minutes": 25},
        "in_service": 2, "waiting": 1, "wait_minutes": 20,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 3  (7 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "bai-do-q3-01",
        "name": "Hầm đỗ xe Võ Văn Tần Q3",
        "district": "Quận 3", "street": "78 Võ Văn Tần", "ward": "Phường 6",
        "lat": 10.7834, "lng": 106.6856,
        "tier": 4, "tier_score": 88.0, "total_bays": 4,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 90, "process_score": 88, "staff_score": 85, "capacity_score": 82, "reliability_score": 95},
        "owner": {"username": "owner_q3_01", "name": "Lê Thị Hà", "email": "owner.q3.01@example.com", "phone": "0901111002"},
        "stats": {"total_services": 2100, "avg_rating": 4.72, "retention_rate": 0.68, "complaint_rate": 0.02, "on_time_rate": 0.91, "avg_actual_processing_minutes": 65},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "bai-do-q3-02",
        "name": "Hầm đỗ xe Bà Huyện Thanh Quan Q3",
        "district": "Quận 3", "street": "44 Bà Huyện Thanh Quan", "ward": "Phường 9",
        "lat": 10.7820, "lng": 106.6851,
        "tier": 4, "tier_score": 85.5, "total_bays": 3,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 88, "process_score": 86, "staff_score": 84, "capacity_score": 78, "reliability_score": 90},
        "owner": {"username": "owner_q3_02", "name": "Nguyễn Tiến Đạt", "email": "owner.q3.02@example.com", "phone": "0901111021"},
        "stats": {"total_services": 980, "avg_rating": 4.80, "retention_rate": 0.75, "complaint_rate": 0.01, "on_time_rate": 0.93, "avg_actual_processing_minutes": 90},
        "in_service": 1, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "bai-do-q3-03",
        "name": "Hầm đỗ xe Trần Cao Vân Q3",
        "district": "Quận 3", "street": "35 Trần Cao Vân", "ward": "Phường 8",
        "lat": 10.7876, "lng": 106.6862,
        "tier": 3, "tier_score": 73.2, "total_bays": 5,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 76, "process_score": 73, "staff_score": 72, "capacity_score": 75, "reliability_score": 70},
        "owner": {"username": "owner_q3_03", "name": "Hoàng Thị Minh", "email": "owner.q3.03@example.com", "phone": "0901111022"},
        "stats": {"total_services": 1560, "avg_rating": 4.4, "retention_rate": 0.55, "complaint_rate": 0.04, "on_time_rate": 0.86, "avg_actual_processing_minutes": 40},
        "in_service": 2, "waiting": 1, "wait_minutes": 14,
    },
    {
        "slug": "bai-do-q3-04",
        "name": "Hầm đỗ xe Cách Mạng Tháng 8 Q3",
        "district": "Quận 3", "street": "156 Cách Mạng Tháng 8", "ward": "Phường 10",
        "lat": 10.7843, "lng": 106.6901,
        "tier": 3, "tier_score": 69.5, "total_bays": 6,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 68, "staff_score": 70, "capacity_score": 74, "reliability_score": 63},
        "owner": {"username": "owner_q3_04", "name": "Trần Văn Hải", "email": "owner.q3.04@example.com", "phone": "0901111023"},
        "stats": {"total_services": 2350, "avg_rating": 4.2, "retention_rate": 0.50, "complaint_rate": 0.05, "on_time_rate": 0.84, "avg_actual_processing_minutes": 30},
        "in_service": 3, "waiting": 2, "wait_minutes": 20,
    },
    {
        "slug": "bai-do-q3-05",
        "name": "Hầm đỗ xe Lý Chính Thắng Q3",
        "district": "Quận 3", "street": "67 Lý Chính Thắng", "ward": "Phường 8",
        "lat": 10.7889, "lng": 106.6875,
        "tier": 3, "tier_score": 72.8, "total_bays": 4,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 75, "process_score": 72, "staff_score": 74, "capacity_score": 70, "reliability_score": 72},
        "owner": {"username": "owner_q3_05", "name": "Lê Ngọc Bích", "email": "owner.q3.05@example.com", "phone": "0901111024"},
        "stats": {"total_services": 1230, "avg_rating": 4.45, "retention_rate": 0.57, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 38},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "bai-do-q3-06",
        "name": "Bãi đỗ có mái che Nam Kỳ Khởi Nghĩa Q3",
        "district": "Quận 3", "street": "92 Nam Kỳ Khởi Nghĩa", "ward": "Phường 7",
        "lat": 10.7862, "lng": 106.6844,
        "tier": 2, "tier_score": 58.0, "total_bays": 6,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 60, "process_score": 57, "staff_score": 60, "capacity_score": 58, "reliability_score": 55},
        "owner": {"username": "owner_q3_06", "name": "Phạm Văn Tùng", "email": "owner.q3.06@example.com", "phone": "0901111025"},
        "stats": {"total_services": 3100, "avg_rating": 3.9, "retention_rate": 0.38, "complaint_rate": 0.07, "on_time_rate": 0.77, "avg_actual_processing_minutes": 20},
        "in_service": 4, "waiting": 2, "wait_minutes": 22,
    },
    {
        "slug": "bai-do-q3-07",
        "name": "Bãi đỗ có mái che Điện Biên Phủ Q3",
        "district": "Quận 3", "street": "211 Điện Biên Phủ", "ward": "Phường 6",
        "lat": 10.7907, "lng": 106.6922,
        "tier": 2, "tier_score": 52.3, "total_bays": 8,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 3.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 55, "process_score": 55, "staff_score": 48, "capacity_score": 60, "reliability_score": 43},
        "owner": {"username": "owner_q3_07", "name": "Ngô Văn Dũng", "email": "owner.q3.07@example.com", "phone": "0901111026"},
        "stats": {"total_services": 5800, "avg_rating": 3.7, "retention_rate": 0.35, "complaint_rate": 0.08, "on_time_rate": 0.75, "avg_actual_processing_minutes": 16},
        "in_service": 5, "waiting": 3, "wait_minutes": 28,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 5  (8 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "bai-do-q5-01",
        "name": "Hầm đỗ xe Hùng Vương Q5",
        "district": "Quận 5", "street": "200 Hùng Vương", "ward": "Phường 9",
        "lat": 10.7540, "lng": 106.6773,
        "tier": 4, "tier_score": 84.0, "total_bays": 4,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 87, "process_score": 84, "staff_score": 82, "capacity_score": 80, "reliability_score": 87},
        "owner": {"username": "owner_q5_01", "name": "Trần Minh Quang", "email": "owner.q5.01@example.com", "phone": "0901111031"},
        "stats": {"total_services": 1850, "avg_rating": 4.7, "retention_rate": 0.70, "complaint_rate": 0.02, "on_time_rate": 0.90, "avg_actual_processing_minutes": 70},
        "in_service": 2, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "bai-do-q5-02",
        "name": "Hầm đỗ xe An Dương Vương Q5",
        "district": "Quận 5", "street": "55 An Dương Vương", "ward": "Phường 8",
        "lat": 10.7531, "lng": 106.6737,
        "tier": 3, "tier_score": 76.0, "total_bays": 5,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 79, "process_score": 76, "staff_score": 78, "capacity_score": 74, "reliability_score": 73},
        "owner": {"username": "owner_q5_02", "name": "Lý Thị Phượng", "email": "owner.q5.02@example.com", "phone": "0901111032"},
        "stats": {"total_services": 1640, "avg_rating": 4.5, "retention_rate": 0.58, "complaint_rate": 0.03, "on_time_rate": 0.87, "avg_actual_processing_minutes": 38},
        "in_service": 2, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "bai-do-q5-03",
        "name": "Hầm đỗ xe Phan Văn Khỏe Q5",
        "district": "Quận 5", "street": "145 Phan Văn Khỏe", "ward": "Phường 12",
        "lat": 10.7519, "lng": 106.6751,
        "tier": 3, "tier_score": 70.2, "total_bays": 4,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 73, "process_score": 70, "staff_score": 70, "capacity_score": 68, "reliability_score": 70},
        "owner": {"username": "owner_q5_03", "name": "Trương Văn Bảo", "email": "owner.q5.03@example.com", "phone": "0901111033"},
        "stats": {"total_services": 1280, "avg_rating": 4.3, "retention_rate": 0.52, "complaint_rate": 0.04, "on_time_rate": 0.85, "avg_actual_processing_minutes": 35},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },
    {
        "slug": "bai-do-q5-04",
        "name": "Hầm đỗ xe Trần Hưng Đạo B Q5",
        "district": "Quận 5", "street": "128 Trần Hưng Đạo B", "ward": "Phường 7",
        "lat": 10.7556, "lng": 106.6818,
        "tier": 3, "tier_score": 68.5, "total_bays": 6,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 70, "process_score": 68, "staff_score": 68, "capacity_score": 72, "reliability_score": 65},
        "owner": {"username": "owner_q5_04", "name": "Nguyễn Thị Vân", "email": "owner.q5.04@example.com", "phone": "0901111034"},
        "stats": {"total_services": 3200, "avg_rating": 4.2, "retention_rate": 0.48, "complaint_rate": 0.05, "on_time_rate": 0.83, "avg_actual_processing_minutes": 30},
        "in_service": 3, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "bai-do-q5-05",
        "name": "Bãi đỗ có mái che Châu Văn Liêm Q5",
        "district": "Quận 5", "street": "33 Châu Văn Liêm", "ward": "Phường 14",
        "lat": 10.7508, "lng": 106.6763,
        "tier": 2, "tier_score": 60.0, "total_bays": 5,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 65, "process_score": 62, "staff_score": 58, "capacity_score": 60, "reliability_score": 55},
        "owner": {"username": "owner_q5_05", "name": "Đinh Hữu Phú", "email": "owner.q5.05@example.com", "phone": "0901111035"},
        "stats": {"total_services": 4500, "avg_rating": 4.0, "retention_rate": 0.42, "complaint_rate": 0.05, "on_time_rate": 0.80, "avg_actual_processing_minutes": 18},
        "in_service": 3, "waiting": 2, "wait_minutes": 18,
    },
    {
        "slug": "bai-do-q5-06",
        "name": "Bãi đỗ có mái che Ngô Quyền Q5",
        "district": "Quận 5", "street": "77 Ngô Quyền", "ward": "Phường 6",
        "lat": 10.7552, "lng": 106.6784,
        "tier": 2, "tier_score": 55.5, "total_bays": 6,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 58, "process_score": 55, "staff_score": 56, "capacity_score": 58, "reliability_score": 50},
        "owner": {"username": "owner_q5_06", "name": "Lưu Thị Kim", "email": "owner.q5.06@example.com", "phone": "0901111036"},
        "stats": {"total_services": 5200, "avg_rating": 3.8, "retention_rate": 0.38, "complaint_rate": 0.07, "on_time_rate": 0.76, "avg_actual_processing_minutes": 20},
        "in_service": 4, "waiting": 3, "wait_minutes": 25,
    },
    {
        "slug": "bai-do-q5-07",
        "name": "Bãi đỗ xe Nguyễn Trãi Q5",
        "district": "Quận 5", "street": "88 Nguyễn Trãi", "ward": "Phường 3",
        "lat": 10.7578, "lng": 106.6826,
        "tier": 1, "tier_score": 38.0, "total_bays": 10,
        "description": "Bãi ngoài trời, lối vào rộng, phù hợp gửi ngắn. Khu vực Quận 5.",
        "amenities": ["cctv"],
        "services": ["park_hourly", "park_overnight"],
        "vehicle_types": ["standard"],
        "assessment": {"equipment_score": 40, "process_score": 42, "staff_score": 35, "capacity_score": 45, "reliability_score": 28},
        "owner": {"username": "owner_q5_07", "name": "Nguyễn Văn Mạnh", "email": "owner.q5.07@example.com", "phone": "0901111037"},
        "stats": {"total_services": 8900, "avg_rating": 3.2, "retention_rate": 0.28, "complaint_rate": 0.12, "on_time_rate": 0.68, "avg_actual_processing_minutes": 12},
        "in_service": 7, "waiting": 5, "wait_minutes": 30,
    },
    {
        "slug": "bai-do-q5-08",
        "name": "Bãi đỗ có mái che Lê Hồng Phong Q5",
        "district": "Quận 5", "street": "222 Lê Hồng Phong", "ward": "Phường 4",
        "lat": 10.7499, "lng": 106.6748,
        "tier": 2, "tier_score": 57.8, "total_bays": 4,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 5.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 60, "process_score": 58, "staff_score": 60, "capacity_score": 52, "reliability_score": 58},
        "owner": {"username": "owner_q5_08", "name": "Hứa Thị Ngọc", "email": "owner.q5.08@example.com", "phone": "0901111038"},
        "stats": {"total_services": 1800, "avg_rating": 4.05, "retention_rate": 0.45, "complaint_rate": 0.04, "on_time_rate": 0.82, "avg_actual_processing_minutes": 22},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 7  (7 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "bai-do-q7-01",
        "name": "Hầm đỗ xe Nguyễn Thị Thập Q7",
        "district": "Quận 7", "street": "120 Nguyễn Thị Thập", "ward": "Phường Tân Phú",
        "lat": 10.7325, "lng": 106.7155,
        "tier": 3, "tier_score": 72.0, "total_bays": 5,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 70, "staff_score": 75, "capacity_score": 80, "reliability_score": 63},
        "owner": {"username": "owner_q7_01", "name": "Nguyễn Văn Bình", "email": "owner.q7.01@example.com", "phone": "0901111003"},
        "stats": {"total_services": 1580, "avg_rating": 4.3, "retention_rate": 0.55, "complaint_rate": 0.04, "on_time_rate": 0.86, "avg_actual_processing_minutes": 32},
        "in_service": 3, "waiting": 2, "wait_minutes": 15,
    },
    {
        "slug": "bai-do-q7-02",
        "name": "Hầm đỗ xe Huỳnh Tấn Phát Q7",
        "district": "Quận 7", "street": "45 Huỳnh Tấn Phát", "ward": "Phường Bình Thuận",
        "lat": 10.7231, "lng": 106.7222,
        "tier": 4, "tier_score": 88.5, "total_bays": 5,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 91, "process_score": 88, "staff_score": 87, "capacity_score": 85, "reliability_score": 91},
        "owner": {"username": "owner_q7_02", "name": "Hoàng Minh Trí", "email": "owner.q7.02@example.com", "phone": "0901111041"},
        "stats": {"total_services": 2250, "avg_rating": 4.88, "retention_rate": 0.78, "complaint_rate": 0.01, "on_time_rate": 0.95, "avg_actual_processing_minutes": 75},
        "in_service": 3, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "bai-do-q7-03",
        "name": "Hầm đỗ xe Nguyễn Văn Linh Q7",
        "district": "Quận 7", "street": "88 Nguyễn Văn Linh", "ward": "Phường Tân Hưng",
        "lat": 10.7289, "lng": 106.7178,
        "tier": 3, "tier_score": 74.5, "total_bays": 6,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 78, "process_score": 74, "staff_score": 76, "capacity_score": 75, "reliability_score": 69},
        "owner": {"username": "owner_q7_03", "name": "Phạm Thị Xuân", "email": "owner.q7.03@example.com", "phone": "0901111042"},
        "stats": {"total_services": 1890, "avg_rating": 4.45, "retention_rate": 0.60, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 40},
        "in_service": 3, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "bai-do-q7-04",
        "name": "Hầm đỗ xe Nguyễn Hữu Thọ Q7",
        "district": "Quận 7", "street": "200 Nguyễn Hữu Thọ", "ward": "Phường Tân Hưng",
        "lat": 10.7312, "lng": 106.7195,
        "tier": 4, "tier_score": 90.2, "total_bays": 4,
        "description": "Bãi trong hầm toà nhà, kiểm soát ra vào, bảo vệ trực 24 giờ, có trụ sạc xe điện. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging", "elevator", "car_wash"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["luxury", "super"],
        "assessment": {"equipment_score": 94, "process_score": 91, "staff_score": 89, "capacity_score": 84, "reliability_score": 93},
        "owner": {"username": "owner_q7_04", "name": "Vũ Thanh Hùng", "email": "owner.q7.04@example.com", "phone": "0901111043"},
        "stats": {"total_services": 820, "avg_rating": 4.95, "retention_rate": 0.85, "complaint_rate": 0.005, "on_time_rate": 0.97, "avg_actual_processing_minutes": 180},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "bai-do-q7-05",
        "name": "Bãi đỗ có mái che Đào Trí Q7",
        "district": "Quận 7", "street": "33 Đào Trí", "ward": "Phường Phú Thuận",
        "lat": 10.7198, "lng": 106.7245,
        "tier": 2, "tier_score": 58.2, "total_bays": 5,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 62, "process_score": 58, "staff_score": 60, "capacity_score": 57, "reliability_score": 54},
        "owner": {"username": "owner_q7_05", "name": "Đỗ Văn Quý", "email": "owner.q7.05@example.com", "phone": "0901111044"},
        "stats": {"total_services": 1420, "avg_rating": 3.95, "retention_rate": 0.40, "complaint_rate": 0.06, "on_time_rate": 0.80, "avg_actual_processing_minutes": 22},
        "in_service": 2, "waiting": 1, "wait_minutes": 18,
    },
    {
        "slug": "bai-do-q7-06",
        "name": "Bãi đỗ có mái che Lê Văn Lương Q7",
        "district": "Quận 7", "street": "156 Lê Văn Lương", "ward": "Phường Tân Quy",
        "lat": 10.7352, "lng": 106.7162,
        "tier": 2, "tier_score": 53.8, "total_bays": 8,
        "description": "Bãi có mái che, phù hợp gửi cả ngày và gửi qua đêm. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv"],
        "services": ["park_hourly", "park_overnight", "park_daily"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 56, "process_score": 54, "staff_score": 52, "capacity_score": 60, "reliability_score": 46},
        "owner": {"username": "owner_q7_06", "name": "Tạ Thị Hồng", "email": "owner.q7.06@example.com", "phone": "0901111045"},
        "stats": {"total_services": 6200, "avg_rating": 3.75, "retention_rate": 0.35, "complaint_rate": 0.08, "on_time_rate": 0.76, "avg_actual_processing_minutes": 14},
        "in_service": 4, "waiting": 3, "wait_minutes": 22,
    },
    {
        "slug": "bai-do-q7-07",
        "name": "Hầm đỗ xe Cao Lo Q7",
        "district": "Quận 7", "street": "77 Cao Lo", "ward": "Phường Tân Phú",
        "lat": 10.7267, "lng": 106.7201,
        "tier": 3, "tier_score": 71.0, "total_bays": 5,
        "description": "Bãi trong hầm, kiểm soát ra vào bằng thẻ, bảo vệ trực theo ca. Khu vực Quận 7.",
        "amenities": ["covered", "security_24h", "cctv", "ev_charging"],
        "services": ["park_hourly", "park_overnight", "park_daily", "park_monthly"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 75, "process_score": 70, "staff_score": 72, "capacity_score": 68, "reliability_score": 70},
        "owner": {"username": "owner_q7_07", "name": "Lê Trung Kiên", "email": "owner.q7.07@example.com", "phone": "0901111046"},
        "stats": {"total_services": 1160, "avg_rating": 4.35, "retention_rate": 0.54, "complaint_rate": 0.04, "on_time_rate": 0.85, "avg_actual_processing_minutes": 30},
        "in_service": 2, "waiting": 1, "wait_minutes": 12,
    },
]

# ─────────────────────────────────────────────────────────────────
# CUSTOMERS — 6 khách hàng đa dạng
# ─────────────────────────────────────────────────────────────────

CUSTOMERS_DATA = [
    {
        "username": "customer_an",
        "name": "Nguyễn Văn An",
        "email": "an@gmail.com", "phone": "0912345678",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51K-123.45", "brand": "VinFast", "model": "VF8",         "year": 2023, "color": "Đen",   "vehicle_type": "premium", "body_type": "suv",   "size_class": "large",  "is_default": True},
            {"license_plate": "51A-999.99", "brand": "Mercedes-Benz", "model": "C300",  "year": 2020, "color": "Trắng", "vehicle_type": "luxury",  "body_type": "sedan", "size_class": "large",  "is_default": False},
        ]
    },
    {
        "username": "customer_binh",
        "name": "Trần Thị Bình",
        "email": "binh@gmail.com", "phone": "0987654321",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51B-444.44", "brand": "Toyota",  "model": "Camry",  "year": 2021, "color": "Bạc",   "vehicle_type": "standard", "body_type": "sedan", "size_class": "medium", "is_default": True},
            {"license_plate": "51C-777.77", "brand": "Honda",   "model": "CR-V",   "year": 2022, "color": "Xanh",  "vehicle_type": "standard", "body_type": "suv",   "size_class": "medium", "is_default": False},
        ]
    },
    {
        "username": "customer_cuong",
        "name": "Lê Minh Cường",
        "email": "cuong@gmail.com", "phone": "0977888999",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51S-007.01", "brand": "Tesla",      "model": "Model S",  "year": 2023, "color": "Đỏ",   "vehicle_type": "luxury",  "body_type": "sedan", "size_class": "large",  "is_default": True},
            {"license_plate": "51F-321.00", "brand": "BMW",        "model": "M5",       "year": 2019, "color": "Trắng","vehicle_type": "luxury",  "body_type": "sedan", "size_class": "large",  "is_default": False},
            {"license_plate": "51F-000.22", "brand": "Kia",        "model": "K5",       "year": 2023, "color": "Xám",  "vehicle_type": "standard","body_type": "sedan", "size_class": "medium", "is_default": False},
        ]
    },
    {
        "username": "customer_dung",
        "name": "Phạm Anh Dũng",
        "email": "dung.pham@gmail.com", "phone": "0909123456",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51G-888.88", "brand": "Ford",     "model": "Explorer",  "year": 2022, "color": "Đen",  "vehicle_type": "premium", "body_type": "suv",   "size_class": "large",  "is_default": True},
            {"license_plate": "51H-555.55", "brand": "Hyundai",  "model": "Santa Fe",  "year": 2021, "color": "Trắng","vehicle_type": "standard","body_type": "suv",   "size_class": "large",  "is_default": False},
        ]
    },
    {
        "username": "customer_mai",
        "name": "Ngô Thị Mai",
        "email": "mai.ngo@gmail.com", "phone": "0918765432",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51D-246.81", "brand": "Mazda",    "model": "CX-5",     "year": 2022, "color": "Đỏ",    "vehicle_type": "standard","body_type": "suv",   "size_class": "medium", "is_default": True},
            {"license_plate": "51E-135.79", "brand": "Suzuki",   "model": "Ertiga",   "year": 2020, "color": "Bạc",   "vehicle_type": "standard","body_type": "mpv",   "size_class": "medium", "is_default": False},
        ]
    },
    {
        "username": "customer_hieu",
        "name": "Võ Trung Hiếu",
        "email": "hieu.vo@gmail.com", "phone": "0933456789",
        "password": "Customer@2026",
        "vehicles": [
            {"license_plate": "51P-168.89", "brand": "Lamborghini", "model": "Urus",  "year": 2023, "color": "Vàng",  "vehicle_type": "super",   "body_type": "suv",   "size_class": "large",  "is_default": True},
            {"license_plate": "51R-911.00", "brand": "Porsche",     "model": "911",   "year": 2022, "color": "Bạc",   "vehicle_type": "super",   "body_type": "coupe", "size_class": "medium", "is_default": False},
        ]
    },
]

# ── Price map theo tier ─────────────────────────────────────────
SERVICE_PRICE_MAP = {
    # Giá mẫu theo cấp bãi, đơn vị đồng. Duration tính bằng phút.
    "park_hourly":    {"tier1": 15000,   "tier2": 20000,   "tier3": 25000,   "tier4": 30000,   "duration": 60},
    "park_overnight": {"tier1": 50000,   "tier2": 70000,   "tier3": 90000,   "tier4": 120000,  "duration": 720},
    "park_daily":     {"tier1": 100000,  "tier2": 150000,  "tier3": 200000,  "tier4": 250000,  "duration": 1440},
    "park_monthly":   {"tier1": 1000000, "tier2": 1500000, "tier3": 2200000, "tier4": 3000000, "duration": 43200},
}

VEHICLE_TIER_MIN = {"standard": 1, "premium": 2, "luxury": 3, "super": 4}

# ── Feedback pool ───────────────────────────────────────────────
POSITIVE_COMMENTS = [
    "Vào ra nhanh, đúng chỗ đã giữ.",
    "Bảo vệ hướng dẫn tận tình.",
    "Bãi sạch, có mái che, sẽ gửi lại.",
    "Đi bộ tới nơi làm việc chỉ vài phút.",
    "Giá rõ ràng, không phát sinh.",
    "",  # để trống cũng hợp lệ
]
NEGATIVE_COMMENTS = [
    "Chờ ở cổng khá lâu.",
    "Lối vào hẹp, khó quay đầu.",
    "Tới nơi thì chỗ đã có xe khác đỗ.",
    "Giá cao hơn mức mong đợi.",
]


# ─────────────────────────────────────────────────────────────────
# SEED FUNCTIONS
# ─────────────────────────────────────────────────────────────────

async def reset_collections():
    from app.api.tenant.tenant_models import TenantModel
    from app.api.user.user_models import UserModel
    from app.api.garage.garage_models import GarageModel
    from app.api.garage_service.garage_service_models import GarageServiceModel
    from app.api.vehicle.vehicle_models import VehicleModel
    from app.api.booking.booking_models import BookingModel
    from app.api.capacity.capacity_models import CapacitySnapshotModel

    print("\n🗑️  Resetting collections (giữ lại super_admin)...")
    await UserModel.collection.delete_many({"role": {"$ne": "super_admin"}})
    await TenantModel.collection.delete_many({"slug": {"$ne": "super_admin"}})
    await GarageModel.collection.delete_many({})
    await GarageServiceModel.collection.delete_many({})
    await VehicleModel.collection.delete_many({})
    await BookingModel.collection.delete_many({})
    await CapacitySnapshotModel.collection.delete_many({})
    print("   Done")


async def seed_garages_and_owners():
    from app.api.tenant.tenant_models import TenantModel
    from app.api.user.user_models import UserModel
    from app.api.garage.garage_models import GarageModel
    from app.api.auth.auth_utils import hash_password

    print(f"\n🏢 Seeding {len(GARAGES_DATA)} garages & owners...")
    garage_docs = {}

    for g in GARAGES_DATA:
        slug = g["slug"]
        now = now_utc()

        existing_tenant = await TenantModel.collection.find_one({"slug": slug})
        if existing_tenant:
            garage_doc = await GarageModel.collection.find_one({"slug": slug})
            if garage_doc:
                garage_docs[slug] = garage_doc
            continue

        # Tenant
        tenant_doc = TenantModel(
            tenant_id=slug,
            name=g["name"],
            slug=slug,
            type="garage",
            status="active",
            contact={"phone": g["owner"]["phone"], "email": g["owner"]["email"]},
            subscription_plan="pro" if g["tier"] >= 3 else "basic",
            settings={"timezone": "Asia/Ho_Chi_Minh", "currency": "VND", "language": "vi"},
            created_at=now, updated_at=now,
            created_by="seed", updated_by="seed",
        )
        await tenant_doc.commit()

        # Owner
        owner = g["owner"]
        user_doc = UserModel(
            tenant_id=slug,
            username=owner["username"],
            email=owner["email"],
            phone=owner["phone"],
            password_hash=hash_password("GarageOwner@2026"),
            name=owner["name"],
            role="garage_owner",
            is_active=True,
            created_at=now, updated_at=now,
            created_by="seed", updated_by="seed",
        )
        await user_doc.commit()
        await TenantModel.collection.update_one(
            {"_id": tenant_doc.pk},
            {"$set": {"owner_user_id": str(user_doc.pk)}}
        )

        # Garage
        garage = GarageModel(
            tenant_id=slug,
            name=g["name"],
            slug=slug,
            location={"type": "Point", "coordinates": [g["lng"], g["lat"]]},
            address={
                "street": g["street"],
                "ward": g.get("ward", ""),
                "district": g["district"],
                "city": "TP Hồ Chí Minh",
                "province": "TP Hồ Chí Minh",
            },
            tier=g["tier"],
            tier_score=g["tier_score"],
            tier_assessment={
                **g["assessment"],
                "last_assessed_at": days_ago(30),
                "assessed_by": "system",
            },
            capacity={
                "total_bays": g["total_bays"],
                "max_vehicles_per_hour": g["total_bays"] * 2,
                "avg_processing_time_minutes": g["stats"].get("avg_actual_processing_minutes", 30),
            },
            operating_hours={
                "monday":    {"open": "07:00", "close": "20:00"},
                "tuesday":   {"open": "07:00", "close": "20:00"},
                "wednesday": {"open": "07:00", "close": "20:00"},
                "thursday":  {"open": "07:00", "close": "20:00"},
                "friday":    {"open": "07:00", "close": "21:00"},
                "saturday":  {"open": "07:00", "close": "21:00"},
                "sunday":    {"open": "08:00", "close": "18:00"},
            },
            services_offered=g["services"],
            vehicle_types_accepted=g["vehicle_types"],
            amenities=g["amenities"],
            description=g["description"],
            status="active",
            is_verified=g["tier"] >= 3,
            is_accepting_bookings=True,
            current_load={
                "vehicles_in_service": g["in_service"],
                "vehicles_waiting": g["waiting"],
                "estimated_wait_minutes": g["wait_minutes"],
                "last_updated": now,
            },
            stats=g["stats"],
            created_at=days_ago(random.randint(180, 365)),
            updated_at=now,
            created_by="seed", updated_by="seed",
        )
        await garage.commit()
        garage_doc = await GarageModel.collection.find_one({"_id": garage.pk})
        garage_docs[slug] = garage_doc
        print(f"   [{g['district']}] {g['name']} — Tier {g['tier']}")

    return garage_docs


async def seed_garage_services(garage_docs: dict):
    from app.api.garage_service.garage_service_models import GarageServiceModel

    print("\n🛠️  Seeding garage services...")
    for gdata in GARAGES_DATA:
        slug = gdata["slug"]
        garage = garage_docs.get(slug)
        if not garage:
            continue

        garage_id = garage["_id"]
        tier_key = f"tier{gdata['tier']}"
        now = now_utc()

        for svc_code in gdata["services"]:
            existing = await GarageServiceModel.collection.find_one({
                "garage_id": garage_id, "service_type_code": svc_code
            })
            if existing:
                continue

            price_info = SERVICE_PRICE_MAP.get(svc_code, {})
            price = price_info.get(tier_key) or price_info.get("tier1", 100000)
            # Add slight price variation per garage (+/-10%)
            price = int(price * random.uniform(0.9, 1.1))
            duration = price_info.get("duration", 30)

            await GarageServiceModel.collection.insert_one({
                "tenant_id": slug,
                "garage_id": garage_id,
                "service_type_code": svc_code,
                "price": price,
                "estimated_duration_minutes": duration,
                "is_available": True,
                "created_at": now, "updated_at": now,
                "created_by": "seed", "updated_by": "seed",
            })

    total = await GarageServiceModel.collection.count_documents({})
    print(f"   {total} service offerings seeded")


async def seed_customers_and_vehicles():
    from app.api.user.user_models import UserModel
    from app.api.vehicle.vehicle_models import VehicleModel
    from app.api.auth.auth_utils import hash_password

    print(f"\n👥 Seeding {len(CUSTOMERS_DATA)} customers & vehicles...")
    customer_docs = {}

    for c in CUSTOMERS_DATA:
        now = now_utc()
        existing = await UserModel.collection.find_one({"username": c["username"]})
        if existing:
            vehicles = await VehicleModel.collection.find(
                {"owner_user_id": str(existing["_id"])}
            ).to_list(10)
            customer_docs[c["username"]] = {"user": existing, "vehicles": vehicles}
            continue

        user = UserModel(
            tenant_id="platform",
            username=c["username"],
            email=c["email"],
            phone=c["phone"],
            password_hash=hash_password(c["password"]),
            name=c["name"],
            role="customer",
            is_active=True,
            created_at=days_ago(random.randint(60, 180)),
            updated_at=now,
            created_by="seed", updated_by="seed",
        )
        await user.commit()
        user_doc = await UserModel.collection.find_one({"_id": user.pk})
        user_id = str(user.pk)

        vehicles = []
        for v in c["vehicles"]:
            vehicle = VehicleModel(
                tenant_id="platform",
                owner_user_id=user_id,
                license_plate=v["license_plate"],
                brand=v["brand"],
                model=v["model"],
                year=v["year"],
                color=v["color"],
                vehicle_type=v["vehicle_type"],
                body_type=v["body_type"],
                size_class=v["size_class"],
                minimum_garage_tier=VEHICLE_TIER_MIN[v["vehicle_type"]],
                is_default=v["is_default"],
                is_active=True,
                created_at=days_ago(random.randint(60, 180)),
                updated_at=now,
                created_by="seed", updated_by="seed",
            )
            await vehicle.commit()
            vdoc = await VehicleModel.collection.find_one({"_id": vehicle.pk})
            vehicles.append(vdoc)

        customer_docs[c["username"]] = {"user": user_doc, "vehicles": vehicles}
        print(f"   {c['name']} — {len(vehicles)} vehicles")

    return customer_docs


async def seed_bookings(garage_docs: dict, customer_docs: dict):
    """
    Tạo ~120 bookings trải đều 90 ngày qua:
    - Lịch sử đa dạng status để fuel analytics
    - Hôm nay có bookings active (in_service, confirmed) cho dashboard demo
    - Đảm bảo mỗi garage có ít nhất 3 bookings
    """
    from app.api.booking.booking_models import BookingModel

    # Kiểm tra đã có booking chưa
    existing_count = await BookingModel.collection.count_documents({})
    if existing_count > 10:
        print(f"\n📅 Bookings already exist ({existing_count}), skipping")
        return

    print("\n📅 Seeding bookings (~120 bookings over 90 days)...")

    garage_slugs = list(garage_docs.keys())
    customer_list = list(customer_docs.values())

    def _get_gdata(slug):
        return next((g for g in GARAGES_DATA if g["slug"] == slug), None)

    def _pick_vehicle(cdata, garage_tier):
        eligible = [
            v for v in cdata["vehicles"]
            if VEHICLE_TIER_MIN.get(v.get("vehicle_type", "standard"), 1) <= garage_tier
        ]
        return random.choice(eligible) if eligible else cdata["vehicles"][0]

    def _pick_service(gdata):
        svcs = gdata["services"]
        # Trọng số: gửi theo giờ nhiều nhất, gói tháng ít nhất
        weights = []
        for s in svcs:
            if "hourly" in s:       weights.append(60)
            elif "overnight" in s:  weights.append(20)
            elif "daily" in s:      weights.append(12)
            else:                   weights.append(8)
        return random.choices(svcs, weights=weights)[0]

    def _build_timestamps(status, req_time, svc_duration):
        ts = {"created_at": req_time - timedelta(hours=random.uniform(1, 24))}
        if status not in ("pending", "expired"):
            ts["confirmed_at"] = ts["created_at"] + timedelta(minutes=random.randint(5, 30))
        if status in ("customer_arriving", "customer_arrived", "in_service", "completed",
                      "no_show", "cancelled_by_customer"):
            ts["customer_departed_at"] = req_time - timedelta(minutes=random.randint(20, 60))
        if status in ("customer_arrived", "in_service", "completed"):
            ts["customer_arrived_at"] = req_time + timedelta(minutes=random.randint(-5, 15))
        if status in ("in_service", "completed"):
            ts["service_started_at"] = ts["customer_arrived_at"] + timedelta(minutes=random.randint(2, 8))
        if status == "completed":
            ts["service_completed_at"] = ts["service_started_at"] + timedelta(
                minutes=svc_duration + random.randint(-5, 15)
            )
        if status in ("cancelled_by_customer", "cancelled_by_garage", "no_show"):
            anchor = ts.get("confirmed_at") or ts["created_at"]
            ts["cancelled_at"] = anchor + timedelta(hours=random.uniform(0.5, 6))
        return ts

    seq = 1
    total_inserted = 0

    # ── 1. Ensure every garage has at least 3 completed historical bookings ──
    for slug in garage_slugs:
        garage = garage_docs[slug]
        gdata = _get_gdata(slug)
        if not gdata:
            continue
        for _ in range(random.randint(3, 6)):
            cdata = random.choice(customer_list)
            vehicle = _pick_vehicle(cdata, gdata["tier"])
            svc_code = _pick_service(gdata)
            price_info = SERVICE_PRICE_MAP.get(svc_code, {})
            tier_key = f"tier{gdata['tier']}"
            price = int((price_info.get(tier_key) or price_info.get("tier1", 100000)) * random.uniform(0.9, 1.1))
            duration = price_info.get("duration", 30)

            req_time = rand_dt(days_back_max=80, hour_min=8, hour_max=18)
            ts = _build_timestamps("completed", req_time, duration)

            rating = random.choices([3, 4, 4, 5, 5, 5], k=1)[0]
            comment = random.choice(POSITIVE_COMMENTS if rating >= 4 else NEGATIVE_COMMENTS)

            doc = {
                "tenant_id": slug,
                "booking_code": gen_booking_code(seq),
                "customer_id": cdata["user"]["_id"],
                "garage_id": garage["_id"],
                "vehicle_id": vehicle["_id"],
                "service_type_code": svc_code,
                "price": price,
                "requested_time": req_time,
                "estimated_arrival": req_time,
                "status": "completed",
                "timestamps": ts,
                "matching_context": {
                    "match_score": round(random.uniform(65, 98), 1),
                    "estimated_travel_minutes": random.randint(5, 35),
                    "was_top_recommendation": random.choice([True, True, False]),
                },
                "feedback": {"rating": rating, "quick_feedback": "thumbs_up" if rating >= 4 else "thumbs_down", "comment": comment},
                "cancellation_reason": "",
                "cancelled_by": "",
                "created_at": ts["created_at"],
                "updated_at": now_utc(),
                "created_by": "seed", "updated_by": "seed",
            }
            exists = await BookingModel.collection.find_one({"booking_code": doc["booking_code"]})
            if not exists:
                await BookingModel.collection.insert_one(doc)
                total_inserted += 1
            seq += 1

    # ── 2. Bulk historical bookings (90 days) — diverse statuses ──
    STATUS_WEIGHTS = {
        "completed": 62,
        "cancelled_by_customer": 12,
        "cancelled_by_garage": 5,
        "no_show": 8,
        "expired": 3,
        "interrupted": 2,
    }
    statuses_pool = []
    for s, w in STATUS_WEIGHTS.items():
        statuses_pool.extend([s] * w)

    for day_offset in range(3, 90):
        day_date = now_utc() - timedelta(days=day_offset)
        dow = day_date.weekday()
        # More bookings on weekends + peak tiers
        daily_count = random.randint(2, 5) if dow >= 5 else random.randint(1, 3)

        for _ in range(daily_count):
            slug = random.choice(garage_slugs)
            garage = garage_docs[slug]
            gdata = _get_gdata(slug)
            if not gdata:
                continue

            cdata = random.choice(customer_list)
            vehicle = _pick_vehicle(cdata, gdata["tier"])
            svc_code = _pick_service(gdata)
            price_info = SERVICE_PRICE_MAP.get(svc_code, {})
            tier_key = f"tier{gdata['tier']}"
            price = int((price_info.get(tier_key) or price_info.get("tier1", 100000)) * random.uniform(0.9, 1.1))
            duration = price_info.get("duration", 30)

            req_hour = random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
            req_time = day_date.replace(hour=req_hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)

            status = random.choice(statuses_pool)
            ts = _build_timestamps(status, req_time, duration)

            feedback = {}
            if status == "completed":
                rating = random.choices([3, 4, 4, 5, 5, 5], k=1)[0]
                if random.random() < 0.65:  # 65% leave feedback
                    comment = random.choice(POSITIVE_COMMENTS if rating >= 4 else NEGATIVE_COMMENTS)
                    feedback = {"rating": rating, "quick_feedback": "thumbs_up" if rating >= 4 else "thumbs_down", "comment": comment}

            doc = {
                "tenant_id": slug,
                "booking_code": gen_booking_code(seq),
                "customer_id": cdata["user"]["_id"],
                "garage_id": garage["_id"],
                "vehicle_id": vehicle["_id"],
                "service_type_code": svc_code,
                "price": price,
                "requested_time": req_time,
                "estimated_arrival": req_time,
                "status": status,
                "timestamps": ts,
                "matching_context": {
                    "match_score": round(random.uniform(60, 97), 1),
                    "estimated_travel_minutes": random.randint(5, 40),
                    "was_top_recommendation": random.choice([True, False]),
                },
                "feedback": feedback,
                "cancellation_reason": "Bận đột xuất" if "customer" in status else "Gara hết slot" if "garage" in status else "",
                "cancelled_by": "customer" if "cancelled_by_customer" in status else "garage" if "cancelled_by_garage" in status else "",
                "created_at": ts["created_at"],
                "updated_at": now_utc(),
                "created_by": "seed", "updated_by": "seed",
            }
            exists = await BookingModel.collection.find_one({"booking_code": doc["booking_code"]})
            if not exists:
                await BookingModel.collection.insert_one(doc)
                total_inserted += 1
            seq += 1

    # ── 3. Today's active bookings — cho dashboard demo ──
    today_garages = garage_slugs[:6]  # Lấy 6 garage đầu (Q1 + Q3) có nhiều activity nhất
    active_statuses = ["confirmed", "in_service", "pending", "customer_arriving", "customer_arrived"]

    for i, slug in enumerate(today_garages):
        garage = garage_docs[slug]
        gdata = _get_gdata(slug)
        if not gdata:
            continue
        cdata = random.choice(customer_list)
        vehicle = _pick_vehicle(cdata, gdata["tier"])
        svc_code = _pick_service(gdata)
        price_info = SERVICE_PRICE_MAP.get(svc_code, {})
        tier_key = f"tier{gdata['tier']}"
        price = int((price_info.get(tier_key) or price_info.get("tier1", 100000)))
        duration = price_info.get("duration", 30)

        now = now_utc()
        req_time = now + timedelta(hours=random.uniform(-1, 3))
        req_time = req_time.replace(minute=0, second=0, microsecond=0)
        status = active_statuses[i % len(active_statuses)]
        ts = _build_timestamps(status, req_time, duration)
        ts["created_at"] = now - timedelta(hours=random.uniform(1, 8))

        doc = {
            "tenant_id": slug,
            "booking_code": gen_booking_code(seq),
            "customer_id": cdata["user"]["_id"],
            "garage_id": garage["_id"],
            "vehicle_id": vehicle["_id"],
            "service_type_code": svc_code,
            "price": price,
            "requested_time": req_time,
            "estimated_arrival": req_time,
            "status": status,
            "timestamps": ts,
            "matching_context": {"match_score": round(random.uniform(75, 98), 1), "estimated_travel_minutes": random.randint(5, 20), "was_top_recommendation": True},
            "feedback": {},
            "cancellation_reason": "",
            "cancelled_by": "",
            "created_at": ts["created_at"],
            "updated_at": now,
            "created_by": "seed", "updated_by": "seed",
        }
        exists = await BookingModel.collection.find_one({"booking_code": doc["booking_code"]})
        if not exists:
            await BookingModel.collection.insert_one(doc)
            total_inserted += 1
        seq += 1

    total = await BookingModel.collection.count_documents({})
    print(f"   {total_inserted} bookings inserted — {total} total in DB")


async def seed_capacity_snapshots(garage_docs: dict):
    """4 tuần dữ liệu giờ cho capacity chart. Thêm cả snapshots hôm nay."""
    from app.api.capacity.capacity_models import CapacitySnapshotModel

    print("\n📊 Seeding capacity snapshots (4 tuần + hôm nay)...")

    # Typical hourly load pattern (ratio 0.0–1.0)
    HOURLY_PATTERN = {
        7: 0.12, 8: 0.30, 9: 0.52, 10: 0.68, 11: 0.82,
        12: 0.93, 13: 0.88, 14: 0.82, 15: 0.72, 16: 0.65,
        17: 0.58, 18: 0.45, 19: 0.30, 20: 0.15,
    }

    total_inserted = 0
    now = now_utc()

    for gdata in GARAGES_DATA:
        slug = gdata["slug"]
        garage = garage_docs.get(slug)
        if not garage:
            continue

        garage_id = garage["_id"]
        total_bays = gdata["total_bays"]
        tier = gdata["tier"]

        existing_count = await CapacitySnapshotModel.collection.count_documents({"garage_id": garage_id})
        if existing_count > 100:
            continue

        snapshot_count = 0
        # 28 ngày qua (kể cả hôm nay = 29 ngày)
        for day_offset in range(28, -1, -1):
            snap_date = (now - timedelta(days=day_offset)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            dow = snap_date.weekday()
            is_weekend = dow >= 5

            for hour, base_load in HOURLY_PATTERN.items():
                # Noise + weekend boost + tier boost
                noise = random.uniform(-0.08, 0.08)
                weekend_boost = 0.15 if is_weekend else 0.0
                tier_factor = 1.0 + (tier - 1) * 0.06  # tier 4 → 1.18x busier
                lunch_boost = 0.1 if 11 <= hour <= 13 else 0.0

                load_ratio = min(1.0, max(0.0,
                    (base_load + noise + weekend_boost + lunch_boost) * tier_factor
                ))
                in_svc = min(total_bays, round(load_ratio * total_bays))
                overflow = max(0.0, load_ratio * total_bays - total_bays)
                waiting = min(int(overflow) + (1 if overflow > 0.5 else 0), total_bays)
                wait_min = int(waiting * 20 / max(total_bays, 1)) if waiting else 0
                avail = max(0, total_bays - in_svc)

                snap_dt = snap_date.replace(hour=hour)

                # Chỉ insert nếu giờ đó đã qua (hoặc ngày qua)
                if day_offset > 0 or snap_dt <= now:
                    await CapacitySnapshotModel.collection.insert_one({
                        "tenant_id": slug,
                        "garage_id": garage_id,
                        "timestamp": snap_dt,
                        "vehicles_in_service": in_svc,
                        "vehicles_waiting": waiting,
                        "available_bays": avail,
                        "estimated_wait_minutes": wait_min,
                        "staff_on_duty": max(1, round(total_bays * 0.8)),
                        "hour_of_day": hour,
                        "day_of_week": dow,
                        "created_at": snap_dt,
                        "updated_at": snap_dt,
                        "created_by": "seed", "updated_by": "seed",
                    })
                    snapshot_count += 1

        total_inserted += snapshot_count

    print(f"   {total_inserted} capacity snapshots seeded")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

async def main(reset: bool = False):
    from app.db.mongo import init_mongo

    print("=" * 65)
    print("  Seed Data: 30 bai do xe tai TP.HCM (Q1 Q3 Q5 Q7)")
    print("=" * 65)

    init_mongo()

    if reset:
        await reset_collections()

    from app.api.service_type.service_type_utils import seed_default_service_types
    await seed_default_service_types()
    print("\nService types ready")

    garage_docs   = await seed_garages_and_owners()
    await seed_garage_services(garage_docs)
    customer_docs = await seed_customers_and_vehicles()
    await seed_bookings(garage_docs, customer_docs)
    await seed_capacity_snapshots(garage_docs)

    # Summary
    from app.api.user.user_models import UserModel
    from app.api.garage.garage_models import GarageModel
    from app.api.vehicle.vehicle_models import VehicleModel
    from app.api.booking.booking_models import BookingModel
    from app.api.garage_service.garage_service_models import GarageServiceModel
    from app.api.capacity.capacity_models import CapacitySnapshotModel
    from app.api.tenant.tenant_models import TenantModel

    total_snaps = await CapacitySnapshotModel.collection.count_documents({})
    total_bookings = await BookingModel.collection.count_documents({})
    total_garages = await GarageModel.collection.count_documents({})
    total_users = await UserModel.collection.count_documents({})

    print("\n" + "=" * 65)
    print("  📦 Database Summary")
    print("=" * 65)
    print(f"  Tenants       : {await TenantModel.collection.count_documents({})}")
    print(f"  Garages       : {total_garages} ({await GarageModel.collection.count_documents({'tier': 4})} Elite, {await GarageModel.collection.count_documents({'tier': 3})} Pro, {await GarageModel.collection.count_documents({'tier': 2})} Std, {await GarageModel.collection.count_documents({'tier': 1})} Basic)")
    print(f"  Users         : {total_users} ({await UserModel.collection.count_documents({'role': 'garage_owner'})} owners + {await UserModel.collection.count_documents({'role': 'customer'})} customers)")
    print(f"  Svc Offerings : {await GarageServiceModel.collection.count_documents({})}")
    print(f"  Vehicles      : {await VehicleModel.collection.count_documents({})}")
    print(f"  Bookings      : {total_bookings} ({await BookingModel.collection.count_documents({'status': 'completed'})} completed)")
    print(f"  Cap Snapshots : {total_snaps}")

    print("\n" + "=" * 65)
    print("  Tai khoan thu nghiem")
    print("=" * 65)
    print("  Super Admin   : xem SUPER_ADMIN_USERNAME va SUPER_ADMIN_PASSWORD trong .env")
    print("  Customers     : customer_an, customer_binh, customer_cuong,")
    print("                  customer_dung, customer_mai, customer_hieu")
    print("                  Password: Customer@2026")
    print("  Chu bai        : owner_q1_01 ... owner_q7_08")
    print("                  Password: GarageOwner@2026")
    print("\n  Thu cong chu bai:")
    print("  Login: owner_q1_01 / GarageOwner@2026")
    print("  GET /garage-portal/dashboard/overview")
    print("=" * 65)
    print("\n  Seeding completed.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed du lieu mau")
    parser.add_argument("--reset", action="store_true", help="Xoá data cũ trước khi seed")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
