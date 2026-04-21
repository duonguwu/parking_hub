#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WashMind Seed Data Script
=========================
Tạo dữ liệu mock phong phú cho toàn bộ hệ thống.

Collections được seed:
  - tenants         (30 garages)
  - users           (30 garage owners + 6 customers)
  - garages         (30 điểm rửa xe: Q1, Q3, Q5, Q7 — tọa độ thực HCMC)
  - garage_services (mỗi garage 2-5 services)
  - vehicles        (2-3 xe/customer)
  - bookings        (~120 bookings phân bổ 90 ngày qua)
  - capacity_snapshots (4 tuần dữ liệu giờ để fuel charts)

Usage:
  cd /home/duongn/duongn/washmind/backend
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
# GARAGE DATA — 30 điểm rửa xe tại Q1, Q3, Q5, Q7
# ─────────────────────────────────────────────────────────────────
# tier 1=Basic, 2=Standard, 3=Pro, 4=Elite
# Tất cả tọa độ là GPS thực tế gần đúng tại HCMC

GARAGES_DATA = [

    # ═══════════════════════════════════════════════════════════
    # QUẬN 1  (8 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "aquaglide-elite-q1",
        "name": "AquaGlide Elite",
        "district": "Quận 1", "street": "25 Nguyễn Huệ", "ward": "Phường Bến Nghé",
        "lat": 10.7769, "lng": 106.7009,
        "tier": 4, "tier_score": 91.5, "total_bays": 6,
        "description": "Trung tâm chăm sóc xe cao cấp tại trung tâm Q1. Chuyên phủ ceramic nano, detailing chuyên sâu.",
        "amenities": ["wifi", "coffee", "ev_charging", "waiting_lounge", "tv"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 93, "process_score": 90, "staff_score": 88, "capacity_score": 95, "reliability_score": 91},
        "owner": {"username": "aquaglide_owner", "name": "Trần Minh Khoa", "email": "khoa@aquaglide.vn", "phone": "0901111001"},
        "stats": {"total_services": 3250, "avg_rating": 4.85, "retention_rate": 0.72, "complaint_rate": 0.01, "on_time_rate": 0.94, "avg_actual_processing_minutes": 42},
        "in_service": 4, "waiting": 2, "wait_minutes": 10,
    },
    {
        "slug": "shinelab-q1",
        "name": "ShineLab Studio",
        "district": "Quận 1", "street": "47 Lê Lợi", "ward": "Phường Bến Thành",
        "lat": 10.7750, "lng": 106.7003,
        "tier": 4, "tier_score": 87.2, "total_bays": 5,
        "description": "Studio detailing chuyên nghiệp, ứng dụng công nghệ sơn xe nhập khẩu Đức.",
        "amenities": ["wifi", "coffee", "waiting_lounge", "tv"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 91, "process_score": 85, "staff_score": 86, "capacity_score": 84, "reliability_score": 90},
        "owner": {"username": "shinelab_owner", "name": "Nguyễn Bảo Long", "email": "long@shinelab.vn", "phone": "0901111011"},
        "stats": {"total_services": 2780, "avg_rating": 4.75, "retention_rate": 0.68, "complaint_rate": 0.02, "on_time_rate": 0.92, "avg_actual_processing_minutes": 50},
        "in_service": 3, "waiting": 1, "wait_minutes": 8,
    },
    {
        "slug": "autospa-premium-q1",
        "name": "AutoSpa Premium Q1",
        "district": "Quận 1", "street": "118 Nam Kỳ Khởi Nghĩa", "ward": "Phường Bến Thành",
        "lat": 10.7820, "lng": 106.6972,
        "tier": 3, "tier_score": 74.8, "total_bays": 5,
        "description": "Gara rửa xe cao cấp, phục vụ nhanh chóng ngay trung tâm. Nhận xe sang.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 78, "process_score": 72, "staff_score": 75, "capacity_score": 80, "reliability_score": 69},
        "owner": {"username": "autospa_q1_owner", "name": "Lê Hoàng Nam", "email": "nam@autospa.vn", "phone": "0901111012"},
        "stats": {"total_services": 1920, "avg_rating": 4.5, "retention_rate": 0.58, "complaint_rate": 0.03, "on_time_rate": 0.87, "avg_actual_processing_minutes": 35},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },
    {
        "slug": "nanoshield-q1",
        "name": "NanoShield Detailing",
        "district": "Quận 1", "street": "15 Đinh Tiên Hoàng", "ward": "Phường Đakao",
        "lat": 10.7837, "lng": 106.7028,
        "tier": 4, "tier_score": 89.0, "total_bays": 4,
        "description": "Chuyên gia phủ nano ceramic. Bảo hành 3-5 năm. Nhận xe VIP tận nơi.",
        "amenities": ["wifi", "coffee", "ev_charging", "waiting_lounge", "tv", "concierge"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 95, "process_score": 88, "staff_score": 90, "capacity_score": 80, "reliability_score": 92},
        "owner": {"username": "nanoshield_owner", "name": "Phạm Anh Tuấn", "email": "tuan@nanoshield.vn", "phone": "0901111013"},
        "stats": {"total_services": 1450, "avg_rating": 4.92, "retention_rate": 0.80, "complaint_rate": 0.005, "on_time_rate": 0.96, "avg_actual_processing_minutes": 120},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "citywash-pro-q1",
        "name": "CityWash Pro",
        "district": "Quận 1", "street": "88 Nguyễn Du", "ward": "Phường Bến Nghé",
        "lat": 10.7761, "lng": 106.6984,
        "tier": 3, "tier_score": 70.5, "total_bays": 6,
        "description": "Rửa xe chuyên nghiệp phục vụ dân văn phòng Q1. Nhận đặt lịch online.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 70, "staff_score": 72, "capacity_score": 78, "reliability_score": 60},
        "owner": {"username": "citywash_owner", "name": "Trần Thị Thu", "email": "thu@citywash.vn", "phone": "0901111014"},
        "stats": {"total_services": 2100, "avg_rating": 4.3, "retention_rate": 0.52, "complaint_rate": 0.04, "on_time_rate": 0.85, "avg_actual_processing_minutes": 28},
        "in_service": 3, "waiting": 2, "wait_minutes": 18,
    },
    {
        "slug": "glosslab-q1",
        "name": "GlossLab Central",
        "district": "Quận 1", "street": "22 Hai Bà Trưng", "ward": "Phường Đakao",
        "lat": 10.7815, "lng": 106.7012,
        "tier": 3, "tier_score": 75.3, "total_bays": 4,
        "description": "Tập trung vào dịch vụ interior và detailing cao cấp. Khu vực Dakao.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 80, "process_score": 75, "staff_score": 78, "capacity_score": 68, "reliability_score": 75},
        "owner": {"username": "glosslab_owner", "name": "Vũ Đình Hưng", "email": "hung@glosslab.vn", "phone": "0901111015"},
        "stats": {"total_services": 1680, "avg_rating": 4.55, "retention_rate": 0.60, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 55},
        "in_service": 2, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "speedwash-q1",
        "name": "SpeedWash Express Q1",
        "district": "Quận 1", "street": "233 Lý Tự Trọng", "ward": "Phường Cầu Kho",
        "lat": 10.7760, "lng": 106.6996,
        "tier": 2, "tier_score": 55.0, "total_bays": 8,
        "description": "Rửa xe nhanh, giá rẻ. Phục vụ xe tiêu chuẩn và premium. Hệ thống tự động.",
        "amenities": ["wifi"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 58, "process_score": 58, "staff_score": 52, "capacity_score": 60, "reliability_score": 47},
        "owner": {"username": "speedwash_q1_owner", "name": "Đặng Văn Sơn", "email": "son@speedwash.vn", "phone": "0901111016"},
        "stats": {"total_services": 4200, "avg_rating": 3.9, "retention_rate": 0.40, "complaint_rate": 0.06, "on_time_rate": 0.78, "avg_actual_processing_minutes": 18},
        "in_service": 5, "waiting": 3, "wait_minutes": 25,
    },
    {
        "slug": "ecoshinex-q1",
        "name": "EcoShine Central",
        "district": "Quận 1", "street": "166 Phạm Ngũ Lão", "ward": "Phường Phạm Ngũ Lão",
        "lat": 10.7689, "lng": 106.6965,
        "tier": 2, "tier_score": 58.5, "total_bays": 5,
        "description": "Gara rửa xe thân thiện môi trường, dùng sản phẩm sinh học không độc hại.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 62, "process_score": 58, "staff_score": 60, "capacity_score": 55, "reliability_score": 57},
        "owner": {"username": "ecoshine_q1_owner", "name": "Bùi Thị Lan Anh", "email": "lananh@ecoshine.vn", "phone": "0901111017"},
        "stats": {"total_services": 1350, "avg_rating": 4.1, "retention_rate": 0.45, "complaint_rate": 0.05, "on_time_rate": 0.82, "avg_actual_processing_minutes": 25},
        "in_service": 2, "waiting": 1, "wait_minutes": 20,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 3  (7 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "thedetailer-lab-q3",
        "name": "The Detailer's Lab",
        "district": "Quận 3", "street": "78 Võ Văn Tần", "ward": "Phường 6",
        "lat": 10.7834, "lng": 106.6856,
        "tier": 4, "tier_score": 88.0, "total_bays": 4,
        "description": "Garage detailing chuyên nghiệp nhất Q3. Trang thiết bị nhập khẩu châu Âu.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 90, "process_score": 88, "staff_score": 85, "capacity_score": 82, "reliability_score": 95},
        "owner": {"username": "detailer_lab_owner", "name": "Lê Thị Hà", "email": "ha@detailerlab.vn", "phone": "0901111002"},
        "stats": {"total_services": 2100, "avg_rating": 4.72, "retention_rate": 0.68, "complaint_rate": 0.02, "on_time_rate": 0.91, "avg_actual_processing_minutes": 65},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "masterdetail-q3",
        "name": "MasterDetail Studio",
        "district": "Quận 3", "street": "44 Bà Huyện Thanh Quan", "ward": "Phường 9",
        "lat": 10.7820, "lng": 106.6851,
        "tier": 4, "tier_score": 85.5, "total_bays": 3,
        "description": "Xưởng detailing nghệ thuật. Chuyên phục hồi sơn và dán PPF cho siêu xe.",
        "amenities": ["wifi", "coffee", "waiting_lounge", "tv"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 88, "process_score": 86, "staff_score": 84, "capacity_score": 78, "reliability_score": 90},
        "owner": {"username": "masterdetail_owner", "name": "Nguyễn Tiến Đạt", "email": "dat@masterdetail.vn", "phone": "0901111021"},
        "stats": {"total_services": 980, "avg_rating": 4.80, "retention_rate": 0.75, "complaint_rate": 0.01, "on_time_rate": 0.93, "avg_actual_processing_minutes": 90},
        "in_service": 1, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "luxwash-studio-q3",
        "name": "LuxWash Studio",
        "district": "Quận 3", "street": "35 Trần Cao Vân", "ward": "Phường 8",
        "lat": 10.7876, "lng": 106.6862,
        "tier": 3, "tier_score": 73.2, "total_bays": 5,
        "description": "Rửa xe và chăm sóc nội thất cao cấp. Dịch vụ lấy & trả xe tận nơi.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 76, "process_score": 73, "staff_score": 72, "capacity_score": 75, "reliability_score": 70},
        "owner": {"username": "luxwash_q3_owner", "name": "Hoàng Thị Minh", "email": "minh@luxwash.vn", "phone": "0901111022"},
        "stats": {"total_services": 1560, "avg_rating": 4.4, "retention_rate": 0.55, "complaint_rate": 0.04, "on_time_rate": 0.86, "avg_actual_processing_minutes": 40},
        "in_service": 2, "waiting": 1, "wait_minutes": 14,
    },
    {
        "slug": "premiumcare-q3",
        "name": "PremiumCare Q3",
        "district": "Quận 3", "street": "156 Cách Mạng Tháng 8", "ward": "Phường 10",
        "lat": 10.7843, "lng": 106.6901,
        "tier": 3, "tier_score": 69.5, "total_bays": 6,
        "description": "Phục vụ nhanh, đội ngũ chuyên nghiệp. Nhận nhiều loại xe, giờ mở rộng.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 68, "staff_score": 70, "capacity_score": 74, "reliability_score": 63},
        "owner": {"username": "premiumcare_q3_owner", "name": "Trần Văn Hải", "email": "hai@premiumcare.vn", "phone": "0901111023"},
        "stats": {"total_services": 2350, "avg_rating": 4.2, "retention_rate": 0.50, "complaint_rate": 0.05, "on_time_rate": 0.84, "avg_actual_processing_minutes": 30},
        "in_service": 3, "waiting": 2, "wait_minutes": 20,
    },
    {
        "slug": "purewash-hub-q3",
        "name": "PureWash Hub",
        "district": "Quận 3", "street": "67 Lý Chính Thắng", "ward": "Phường 8",
        "lat": 10.7889, "lng": 106.6875,
        "tier": 3, "tier_score": 72.8, "total_bays": 4,
        "description": "Rửa xe sạch sẽ, sản phẩm xanh không hóa chất mạnh. Thân thiện cho xe sơn mới.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 75, "process_score": 72, "staff_score": 74, "capacity_score": 70, "reliability_score": 72},
        "owner": {"username": "purewash_q3_owner", "name": "Lê Ngọc Bích", "email": "bich@purewash.vn", "phone": "0901111024"},
        "stats": {"total_services": 1230, "avg_rating": 4.45, "retention_rate": 0.57, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 38},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "cleanpro-q3",
        "name": "CleanPro Service",
        "district": "Quận 3", "street": "92 Nam Kỳ Khởi Nghĩa", "ward": "Phường 7",
        "lat": 10.7862, "lng": 106.6844,
        "tier": 2, "tier_score": 58.0, "total_bays": 6,
        "description": "Gara rửa xe giá tốt, phục vụ khách hàng bình dân. Gần nhiều tòa nhà văn phòng.",
        "amenities": ["wifi"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 60, "process_score": 57, "staff_score": 60, "capacity_score": 58, "reliability_score": 55},
        "owner": {"username": "cleanpro_q3_owner", "name": "Phạm Văn Tùng", "email": "tung@cleanpro.vn", "phone": "0901111025"},
        "stats": {"total_services": 3100, "avg_rating": 3.9, "retention_rate": 0.38, "complaint_rate": 0.07, "on_time_rate": 0.77, "avg_actual_processing_minutes": 20},
        "in_service": 4, "waiting": 2, "wait_minutes": 22,
    },
    {
        "slug": "swiftwash-q3",
        "name": "SwiftWash Q3",
        "district": "Quận 3", "street": "211 Điện Biên Phủ", "ward": "Phường 6",
        "lat": 10.7907, "lng": 106.6922,
        "tier": 2, "tier_score": 52.3, "total_bays": 8,
        "description": "Hệ thống rửa xe tự động thế hệ mới. Nhanh — 15 phút/xe. Hoạt động 7am–10pm.",
        "amenities": [],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 55, "process_score": 55, "staff_score": 48, "capacity_score": 60, "reliability_score": 43},
        "owner": {"username": "swiftwash_q3_owner", "name": "Ngô Văn Dũng", "email": "dung@swiftwash.vn", "phone": "0901111026"},
        "stats": {"total_services": 5800, "avg_rating": 3.7, "retention_rate": 0.35, "complaint_rate": 0.08, "on_time_rate": 0.75, "avg_actual_processing_minutes": 16},
        "in_service": 5, "waiting": 3, "wait_minutes": 28,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 5  (8 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "dragondetail-q5",
        "name": "Dragon Detail Q5",
        "district": "Quận 5", "street": "200 Hùng Vương", "ward": "Phường 9",
        "lat": 10.7540, "lng": 106.6773,
        "tier": 4, "tier_score": 84.0, "total_bays": 4,
        "description": "Xưởng detailing hàng đầu Q5, phục vụ cộng đồng người Hoa. Uy tín 10 năm.",
        "amenities": ["wifi", "coffee", "waiting_lounge", "tv"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["standard", "premium", "luxury", "super"],
        "assessment": {"equipment_score": 87, "process_score": 84, "staff_score": 82, "capacity_score": 80, "reliability_score": 87},
        "owner": {"username": "dragon_detail_owner", "name": "Trần Minh Quang", "email": "quang@dragondetail.vn", "phone": "0901111031"},
        "stats": {"total_services": 1850, "avg_rating": 4.7, "retention_rate": 0.70, "complaint_rate": 0.02, "on_time_rate": 0.90, "avg_actual_processing_minutes": 70},
        "in_service": 2, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "phoenixwash-q5",
        "name": "PhoenixWash Q5",
        "district": "Quận 5", "street": "55 An Dương Vương", "ward": "Phường 8",
        "lat": 10.7531, "lng": 106.6737,
        "tier": 3, "tier_score": 76.0, "total_bays": 5,
        "description": "Rửa xe và chăm sóc toàn diện. Chuyên phục vụ xe gia đình tại Q5.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 79, "process_score": 76, "staff_score": 78, "capacity_score": 74, "reliability_score": 73},
        "owner": {"username": "phoenixwash_owner", "name": "Lý Thị Phượng", "email": "phuong@phoenixwash.vn", "phone": "0901111032"},
        "stats": {"total_services": 1640, "avg_rating": 4.5, "retention_rate": 0.58, "complaint_rate": 0.03, "on_time_rate": 0.87, "avg_actual_processing_minutes": 38},
        "in_service": 2, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "silvercare-q5",
        "name": "SilverCare Detailing",
        "district": "Quận 5", "street": "145 Phan Văn Khỏe", "ward": "Phường 12",
        "lat": 10.7519, "lng": 106.6751,
        "tier": 3, "tier_score": 70.2, "total_bays": 4,
        "description": "Chuyên chăm sóc nội thất xe ô tô. Khu vực gần cầu Chữ Y.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 73, "process_score": 70, "staff_score": 70, "capacity_score": 68, "reliability_score": 70},
        "owner": {"username": "silvercare_owner", "name": "Trương Văn Bảo", "email": "bao@silvercare.vn", "phone": "0901111033"},
        "stats": {"total_services": 1280, "avg_rating": 4.3, "retention_rate": 0.52, "complaint_rate": 0.04, "on_time_rate": 0.85, "avg_actual_processing_minutes": 35},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },
    {
        "slug": "vinhlong-autocare-q5",
        "name": "VinhLong Auto Care",
        "district": "Quận 5", "street": "128 Trần Hưng Đạo B", "ward": "Phường 7",
        "lat": 10.7556, "lng": 106.6818,
        "tier": 3, "tier_score": 68.5, "total_bays": 6,
        "description": "Gara lâu đời tại Q5. Phục vụ gia đình và kinh doanh. Giá cả phải chăng.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 70, "process_score": 68, "staff_score": 68, "capacity_score": 72, "reliability_score": 65},
        "owner": {"username": "vinhlong_owner", "name": "Nguyễn Thị Vân", "email": "van@vinhlong.vn", "phone": "0901111034"},
        "stats": {"total_services": 3200, "avg_rating": 4.2, "retention_rate": 0.48, "complaint_rate": 0.05, "on_time_rate": 0.83, "avg_actual_processing_minutes": 30},
        "in_service": 3, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "asiawash-pro-q5",
        "name": "AsiaWash Pro",
        "district": "Quận 5", "street": "33 Châu Văn Liêm", "ward": "Phường 14",
        "lat": 10.7508, "lng": 106.6763,
        "tier": 2, "tier_score": 60.0, "total_bays": 5,
        "description": "Chuỗi rửa xe châu Á hiện đại, máy móc tự động nhập khẩu Nhật Bản.",
        "amenities": ["wifi"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 65, "process_score": 62, "staff_score": 58, "capacity_score": 60, "reliability_score": 55},
        "owner": {"username": "asiawash_owner", "name": "Đinh Hữu Phú", "email": "phu@asiawash.vn", "phone": "0901111035"},
        "stats": {"total_services": 4500, "avg_rating": 4.0, "retention_rate": 0.42, "complaint_rate": 0.05, "on_time_rate": 0.80, "avg_actual_processing_minutes": 18},
        "in_service": 3, "waiting": 2, "wait_minutes": 18,
    },
    {
        "slug": "goldwash-q5",
        "name": "GoldWash Center",
        "district": "Quận 5", "street": "77 Ngô Quyền", "ward": "Phường 6",
        "lat": 10.7552, "lng": 106.6784,
        "tier": 2, "tier_score": 55.5, "total_bays": 6,
        "description": "Trung tâm rửa xe 2 tầng. Tầng 1 xe máy, tầng 2 ô tô. Đậu xe miễn phí.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 58, "process_score": 55, "staff_score": 56, "capacity_score": 58, "reliability_score": 50},
        "owner": {"username": "goldwash_owner", "name": "Lưu Thị Kim", "email": "kim@goldwash.vn", "phone": "0901111036"},
        "stats": {"total_services": 5200, "avg_rating": 3.8, "retention_rate": 0.38, "complaint_rate": 0.07, "on_time_rate": 0.76, "avg_actual_processing_minutes": 20},
        "in_service": 4, "waiting": 3, "wait_minutes": 25,
    },
    {
        "slug": "fastclean-q5",
        "name": "FastClean Q5",
        "district": "Quận 5", "street": "88 Nguyễn Trãi", "ward": "Phường 3",
        "lat": 10.7578, "lng": 106.6826,
        "tier": 1, "tier_score": 38.0, "total_bays": 10,
        "description": "Rửa xe siêu nhanh, siêu rẻ. Không cần đặt trước. Phục vụ 300+ xe/ngày.",
        "amenities": [],
        "services": ["wash_basic"],
        "vehicle_types": ["standard"],
        "assessment": {"equipment_score": 40, "process_score": 42, "staff_score": 35, "capacity_score": 45, "reliability_score": 28},
        "owner": {"username": "fastclean_q5_owner", "name": "Nguyễn Văn Mạnh", "email": "manh@fastclean.vn", "phone": "0901111037"},
        "stats": {"total_services": 8900, "avg_rating": 3.2, "retention_rate": 0.28, "complaint_rate": 0.12, "on_time_rate": 0.68, "avg_actual_processing_minutes": 12},
        "in_service": 7, "waiting": 5, "wait_minutes": 30,
    },
    {
        "slug": "ecowash-q5",
        "name": "EcoWash Q5",
        "district": "Quận 5", "street": "222 Lê Hồng Phong", "ward": "Phường 4",
        "lat": 10.7499, "lng": 106.6748,
        "tier": 2, "tier_score": 57.8, "total_bays": 4,
        "description": "Rửa xe sinh thái, tiết kiệm nước, không hóa chất độc hại. Thân thiện môi trường.",
        "amenities": ["wifi"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 60, "process_score": 58, "staff_score": 60, "capacity_score": 52, "reliability_score": 58},
        "owner": {"username": "ecowash_q5_owner", "name": "Hứa Thị Ngọc", "email": "ngoc@ecowash5.vn", "phone": "0901111038"},
        "stats": {"total_services": 1800, "avg_rating": 4.05, "retention_rate": 0.45, "complaint_rate": 0.04, "on_time_rate": 0.82, "avg_actual_processing_minutes": 22},
        "in_service": 2, "waiting": 1, "wait_minutes": 15,
    },

    # ═══════════════════════════════════════════════════════════
    # QUẬN 7  (7 garages)
    # ═══════════════════════════════════════════════════════════
    {
        "slug": "ecowash-d7",
        "name": "EcoWash Quận 7",
        "district": "Quận 7", "street": "120 Nguyễn Thị Thập", "ward": "Phường Tân Phú",
        "lat": 10.7325, "lng": 106.7155,
        "tier": 3, "tier_score": 72.0, "total_bays": 5,
        "description": "Gara rửa xe sinh thái, dùng nước tái chế. Thân thiện môi trường tại Phú Mỹ Hưng.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 72, "process_score": 70, "staff_score": 75, "capacity_score": 80, "reliability_score": 63},
        "owner": {"username": "ecowash_owner", "name": "Nguyễn Văn Bình", "email": "binh@ecowash.vn", "phone": "0901111003"},
        "stats": {"total_services": 1580, "avg_rating": 4.3, "retention_rate": 0.55, "complaint_rate": 0.04, "on_time_rate": 0.86, "avg_actual_processing_minutes": 32},
        "in_service": 3, "waiting": 2, "wait_minutes": 15,
    },
    {
        "slug": "phumy-wash-premium-q7",
        "name": "PhuMy Wash Premium",
        "district": "Quận 7", "street": "45 Huỳnh Tấn Phát", "ward": "Phường Bình Thuận",
        "lat": 10.7231, "lng": 106.7222,
        "tier": 4, "tier_score": 88.5, "total_bays": 5,
        "description": "Trung tâm chăm sóc xe cao cấp tại Phú Mỹ Hưng. Phục vụ cư dân biệt thự, căn hộ hạng sang.",
        "amenities": ["wifi", "coffee", "ev_charging", "waiting_lounge", "tv", "concierge"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["premium", "luxury", "super"],
        "assessment": {"equipment_score": 91, "process_score": 88, "staff_score": 87, "capacity_score": 85, "reliability_score": 91},
        "owner": {"username": "phumy_wash_owner", "name": "Hoàng Minh Trí", "email": "tri@phumywash.vn", "phone": "0901111041"},
        "stats": {"total_services": 2250, "avg_rating": 4.88, "retention_rate": 0.78, "complaint_rate": 0.01, "on_time_rate": 0.95, "avg_actual_processing_minutes": 75},
        "in_service": 3, "waiting": 1, "wait_minutes": 12,
    },
    {
        "slug": "sunrise-autocare-q7",
        "name": "Sunrise AutoCare Q7",
        "district": "Quận 7", "street": "88 Nguyễn Văn Linh", "ward": "Phường Tân Hưng",
        "lat": 10.7289, "lng": 106.7178,
        "tier": 3, "tier_score": 74.5, "total_bays": 6,
        "description": "Gara toàn diện, phục vụ cả xe gia đình lẫn xe sang tại khu Nam Sài Gòn.",
        "amenities": ["wifi", "coffee", "waiting_lounge"],
        "services": ["wash_basic", "wash_premium", "interior", "detailing"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 78, "process_score": 74, "staff_score": 76, "capacity_score": 75, "reliability_score": 69},
        "owner": {"username": "sunrise_q7_owner", "name": "Phạm Thị Xuân", "email": "xuan@sunrisecar.vn", "phone": "0901111042"},
        "stats": {"total_services": 1890, "avg_rating": 4.45, "retention_rate": 0.60, "complaint_rate": 0.03, "on_time_rate": 0.88, "avg_actual_processing_minutes": 40},
        "in_service": 3, "waiting": 1, "wait_minutes": 10,
    },
    {
        "slug": "pmh-detailing-q7",
        "name": "PMH Detailing Studio",
        "district": "Quận 7", "street": "200 Nguyễn Hữu Thọ", "ward": "Phường Tân Hưng",
        "lat": 10.7312, "lng": 106.7195,
        "tier": 4, "tier_score": 90.2, "total_bays": 4,
        "description": "Studio detailing đẳng cấp PMH. Sử dụng sản phẩm Gtechniq, Carpro. Đặt lịch 2 tuần trước.",
        "amenities": ["wifi", "coffee", "ev_charging", "waiting_lounge", "tv"],
        "services": ["wash_premium", "interior", "detailing", "coating"],
        "vehicle_types": ["luxury", "super"],
        "assessment": {"equipment_score": 94, "process_score": 91, "staff_score": 89, "capacity_score": 84, "reliability_score": 93},
        "owner": {"username": "pmh_detail_owner", "name": "Vũ Thanh Hùng", "email": "hung@pmhdetail.vn", "phone": "0901111043"},
        "stats": {"total_services": 820, "avg_rating": 4.95, "retention_rate": 0.85, "complaint_rate": 0.005, "on_time_rate": 0.97, "avg_actual_processing_minutes": 180},
        "in_service": 2, "waiting": 0, "wait_minutes": 0,
    },
    {
        "slug": "greencar-q7",
        "name": "GreenCar Q7",
        "district": "Quận 7", "street": "33 Đào Trí", "ward": "Phường Phú Thuận",
        "lat": 10.7198, "lng": 106.7245,
        "tier": 2, "tier_score": 58.2, "total_bays": 5,
        "description": "Rửa xe hơi giá tốt, khu dân cư Phú Thuận. Có chỗ ngồi chờ thoải mái.",
        "amenities": ["wifi", "coffee"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 62, "process_score": 58, "staff_score": 60, "capacity_score": 57, "reliability_score": 54},
        "owner": {"username": "greencar_q7_owner", "name": "Đỗ Văn Quý", "email": "quy@greencar.vn", "phone": "0901111044"},
        "stats": {"total_services": 1420, "avg_rating": 3.95, "retention_rate": 0.40, "complaint_rate": 0.06, "on_time_rate": 0.80, "avg_actual_processing_minutes": 22},
        "in_service": 2, "waiting": 1, "wait_minutes": 18,
    },
    {
        "slug": "quickwash-q7",
        "name": "QuickWash Express Q7",
        "district": "Quận 7", "street": "156 Lê Văn Lương", "ward": "Phường Tân Quy",
        "lat": 10.7352, "lng": 106.7162,
        "tier": 2, "tier_score": 53.8, "total_bays": 8,
        "description": "Hệ thống rửa xe nhanh phục vụ văn phòng khu Tân Quy. Mở cửa từ 6am.",
        "amenities": ["wifi"],
        "services": ["wash_basic", "wash_premium"],
        "vehicle_types": ["standard", "premium"],
        "assessment": {"equipment_score": 56, "process_score": 54, "staff_score": 52, "capacity_score": 60, "reliability_score": 46},
        "owner": {"username": "quickwash_q7_owner", "name": "Tạ Thị Hồng", "email": "hong@quickwash7.vn", "phone": "0901111045"},
        "stats": {"total_services": 6200, "avg_rating": 3.75, "retention_rate": 0.35, "complaint_rate": 0.08, "on_time_rate": 0.76, "avg_actual_processing_minutes": 14},
        "in_service": 4, "waiting": 3, "wait_minutes": 22,
    },
    {
        "slug": "skywash-q7",
        "name": "SkyWash Tower Q7",
        "district": "Quận 7", "street": "77 Cao Lo", "ward": "Phường Tân Phú",
        "lat": 10.7267, "lng": 106.7201,
        "tier": 3, "tier_score": 71.0, "total_bays": 5,
        "description": "Rửa xe trên tòa nhà cao tầng, nhìn ra sông Sài Gòn. Trải nghiệm độc đáo.",
        "amenities": ["wifi", "coffee", "waiting_lounge", "tv"],
        "services": ["wash_basic", "wash_premium", "interior"],
        "vehicle_types": ["standard", "premium", "luxury"],
        "assessment": {"equipment_score": 75, "process_score": 70, "staff_score": 72, "capacity_score": 68, "reliability_score": 70},
        "owner": {"username": "skywash_owner", "name": "Lê Trung Kiên", "email": "kien@skywash.vn", "phone": "0901111046"},
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
    "wash_basic":   {"tier1": 60000,   "tier2": 80000,   "tier3": 100000,  "tier4": 120000,  "duration": 20},
    "wash_premium": {"tier1": 120000,  "tier2": 150000,  "tier3": 200000,  "tier4": 250000,  "duration": 35},
    "interior":     {"tier1": None,    "tier2": 220000,  "tier3": 320000,  "tier4": 450000,  "duration": 60},
    "detailing":    {"tier1": None,    "tier2": None,    "tier3": 800000,  "tier4": 1200000, "duration": 180},
    "coating":      {"tier1": None,    "tier2": None,    "tier3": None,    "tier4": 4500000, "duration": 480},
}

VEHICLE_TIER_MIN = {"standard": 1, "premium": 2, "luxury": 3, "super": 4}

# ── Feedback pool ───────────────────────────────────────────────
POSITIVE_COMMENTS = [
    "Rất hài lòng, xe sáng bóng hẳn!",
    "Phục vụ chuyên nghiệp, đúng giờ.",
    "Sẽ quay lại lần sau.",
    "Đội ngũ thân thiện, làm việc tỉ mỉ.",
    "Xứng đáng với giá tiền.",
    "Xe sạch boong, nội thất thơm tho.",
    "Nhanh và chất lượng!",
    "",  # empty comment also ok
]
NEGATIVE_COMMENTS = [
    "Chờ khá lâu, cần cải thiện.",
    "Bình thường, không có gì nổi bật.",
    "Rửa xong vẫn còn vết bẩn ở bánh xe.",
    "Giá hơi cao so với chất lượng.",
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
    print("   ✅ Done")


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
        print(f"   ✅ [{g['district']}] {g['name']} — Tier {g['tier']}")

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
    print(f"   ✅ {total} service offerings seeded")


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
        print(f"   ✅ {c['name']} — {len(vehicles)} vehicles")

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
        # Weighted: basic > premium > interior > detailing > coating
        weights = []
        for s in svcs:
            if "basic" in s:        weights.append(40)
            elif "premium" in s:    weights.append(30)
            elif "interior" in s:   weights.append(18)
            elif "detailing" in s:  weights.append(9)
            else:                   weights.append(3)
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
    print(f"   ✅ {total_inserted} bookings inserted — {total} total in DB")


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

    print(f"   ✅ {total_inserted} capacity snapshots seeded")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

async def main(reset: bool = False):
    from app.db.mongo import init_mongo

    print("=" * 65)
    print("  🌱 WashMind Seed Data — 30 Garages HCMC (Q1 Q3 Q5 Q7)")
    print("=" * 65)

    init_mongo()

    if reset:
        await reset_collections()

    from app.api.service_type.service_type_utils import seed_default_service_types
    await seed_default_service_types()
    print("\n✅ Service types ready")

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
    print("  🔐 Test Credentials")
    print("=" * 65)
    print("  Super Admin   : admin / WashMind@2026!")
    print("  Customers     : customer_an, customer_binh, customer_cuong,")
    print("                  customer_dung, customer_mai, customer_hieu")
    print("                  Password: Customer@2026")
    print("  Garage Owners : aquaglide_owner, shinelab_owner, detailer_lab_owner,")
    print("                  phumy_wash_owner, pmh_detail_owner, ...")
    print("                  Password: GarageOwner@2026")
    print("\n  Garage Portal test (Q1 Elite):")
    print("  → Login: aquaglide_owner / GarageOwner@2026")
    print("  → GET /api/v1/garage/dashboard/overview")
    print("=" * 65)
    print("\n  ✅ Seeding completed!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WashMind Seed Data")
    parser.add_argument("--reset", action="store_true", help="Xoá data cũ trước khi seed")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
