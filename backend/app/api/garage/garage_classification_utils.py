# -*- coding: utf-8 -*-
"""
Phân loại bãi đỗ: loại hình, cấp tích hợp, hạng sao (checklist kiểm định), huy hiệu.
Nguồn tiêu chí: docs/02_business-operations/05_Onboarding_Playbook.md mục 4.
"""
from typing import Dict, List, Optional

LOT_TYPES: Dict[str, str] = {
    "parking_building": "Nhà xe chuyên dụng",
    "office_basement": "Hầm toà nhà văn phòng",
    "apartment_basement": "Hầm chung cư",
    "covered_garage": "Nhà xe có mái",
    "outdoor_commercial": "Bãi ngoài trời",
    "transit_hub": "Đầu mối giao thông",
    "street": "Lòng đường / công cộng",
    "residential": "Chỗ nhỏ hộ dân",
}

INTEGRATION_LEVELS: Dict[int, Dict[str, str]] = {
    1: {"name": "Danh mục", "desc": "Chỉ hiển thị, chưa có dữ liệu chỗ trống"},
    2: {"name": "Có cập nhật", "desc": "Bãi tự cập nhật chỗ trống, đặt chỗ cần bãi xác nhận"},
    3: {"name": "Kết nối cảm nhận", "desc": "Dữ liệu chỗ trống tự động, giữ chỗ tự xác nhận"},
    4: {"name": "Kết nối đầy đủ", "desc": "Tích hợp đầy đủ, ưu tiên xếp hạng"},
}

# Checklist kiểm định — 100 điểm. Mỗi mục: (key, nhóm, điểm, mô tả)
GRADE_CHECKLIST: List[Dict] = [
    # Kết cấu — 25
    {"key": "purpose_built", "group": "structure", "points": 10, "label": "Công trình xây chuyên để đỗ xe"},
    {"key": "paved_surface", "group": "structure", "points": 8, "label": "Mặt sàn bê tông / nhựa"},
    {"key": "marked_bays", "group": "structure", "points": 7, "label": "Kẻ vạch ô đỗ rõ ràng"},
    # An ninh — 25
    {"key": "guard_24h", "group": "security", "points": 10, "label": "Bảo vệ 24/7"},
    {"key": "cctv_full", "group": "security", "points": 10, "label": "Camera phủ toàn bãi"},
    {"key": "barrier", "group": "security", "points": 5, "label": "Barrier / thẻ kiểm soát ra vào"},
    # Che chắn & môi trường — 15
    {"key": "covered", "group": "environment", "points": 7, "label": "Hầm hoặc mái che toàn phần"},
    {"key": "no_flood", "group": "environment", "points": 5, "label": "Không có tiền sử ngập"},
    {"key": "night_lighting", "group": "environment", "points": 3, "label": "Chiếu sáng ban đêm tốt"},
    # Tiếp cận — 15
    {"key": "wide_entrance", "group": "access", "points": 5, "label": "Lối vào rộng, dốc an toàn"},
    {"key": "clearance_2m", "group": "access", "points": 5, "label": "Chiều cao thông thuỷ ≥ 2,0 m"},
    {"key": "no_stacking", "group": "access", "points": 5, "label": "Không đỗ chồng, tự lấy xe được"},
    # PCCC — 10
    {"key": "extinguishers", "group": "fire_safety", "points": 4, "label": "Bình chữa cháy đạt chuẩn"},
    {"key": "fire_alarm", "group": "fire_safety", "points": 4, "label": "Hệ thống báo cháy"},
    {"key": "ev_zone", "group": "fire_safety", "points": 2, "label": "Khu sạc xe điện tách riêng"},
    # Tiện ích — 10
    {"key": "ev_charger", "group": "amenities", "points": 4, "label": "Có trụ sạc xe điện"},
    {"key": "restroom", "group": "amenities", "points": 3, "label": "Nhà vệ sinh"},
    {"key": "waiting_area", "group": "amenities", "points": 3, "label": "Khu chờ / rửa xe"},
]

GRADE_GROUPS: Dict[str, str] = {
    "structure": "Kết cấu",
    "security": "An ninh",
    "environment": "Che chắn & môi trường",
    "access": "Tiếp cận",
    "fire_safety": "An toàn PCCC",
    "amenities": "Tiện ích",
}

_CHECKLIST_KEYS = {c["key"] for c in GRADE_CHECKLIST}


def compute_grade(items: Optional[Dict[str, bool]]) -> Dict:
    """items {key: bool} → {score, grade, groups{group: {score, max}}}."""
    items = items or {}
    groups: Dict[str, Dict[str, int]] = {g: {"score": 0, "max": 0} for g in GRADE_GROUPS}
    score = 0
    for c in GRADE_CHECKLIST:
        groups[c["group"]]["max"] += c["points"]
        if items.get(c["key"]):
            groups[c["group"]]["score"] += c["points"]
            score += c["points"]
    return {"score": score, "grade": grade_from_score(score), "groups": groups}


def grade_from_score(score: int) -> int:
    if score >= 85:
        return 5
    if score >= 70:
        return 4
    if score >= 55:
        return 3
    if score >= 40:
        return 2
    return 1


def sanitize_checklist(items: Optional[Dict]) -> Dict[str, bool]:
    return {k: bool(v) for k, v in (items or {}).items() if k in _CHECKLIST_KEYS}


def suggest_checklist(garage: dict) -> Dict[str, bool]:
    """Gợi ý checklist từ thuộc tính chủ bãi khai — admin xác nhận lại khi kiểm định."""
    a = garage.get("attributes") or {}
    lot_type = garage.get("lot_type", "")
    ev = (a.get("ev_chargers") or {}).get("count", 0) or 0
    return {
        "purpose_built": lot_type in ("parking_building", "transit_hub"),
        "paved_surface": a.get("surface", "concrete") in ("concrete", "asphalt"),
        "marked_bays": lot_type not in ("street", "residential"),
        "guard_24h": a.get("guard") == "24h",
        "cctv_full": a.get("cctv") == "full",
        "barrier": lot_type in ("parking_building", "office_basement", "apartment_basement", "transit_hub"),
        "covered": a.get("cover") in ("basement", "full_roof"),
        "no_flood": a.get("flood_risk", "none") == "none",
        "night_lighting": a.get("lighting", "basic") == "good",
        "wide_entrance": a.get("parking_style") != "stacked",
        "clearance_2m": float(a.get("max_height_m") or 0) >= 2.0 or a.get("cover") == "open",
        "no_stacking": a.get("parking_style", "self") != "stacked",
        "extinguishers": bool(a.get("fire_safety")),
        "fire_alarm": bool(a.get("fire_safety")) and lot_type in ("parking_building", "office_basement", "apartment_basement"),
        "ev_zone": ev > 0 and lot_type in ("parking_building", "office_basement"),
        "ev_charger": ev > 0,
        "restroom": bool(a.get("restroom")),
        "waiting_area": "car_wash" in (garage.get("services_offered") or []),
    }


def compute_badges(garage: dict) -> List[Dict[str, str]]:
    """Huy hiệu tự động hiển thị cạnh tên bãi."""
    badges = []
    a = garage.get("attributes") or {}
    items = (garage.get("grade_assessment") or {}).get("items") or {}
    level = int(garage.get("integration_level") or 1)
    stats = garage.get("stats") or {}

    if garage.get("is_verified"):
        badges.append({"key": "verified", "label": "Đã kiểm định"})
    if garage.get("lot_type") == "parking_building":
        badges.append({"key": "purpose_built", "label": "Bãi chuyên dụng"})
    if level == 4 or (items.get("extinguishers") and items.get("fire_alarm")):
        badges.append({"key": "fire_safe", "label": "An toàn PCCC"})
    if level >= 3:
        badges.append({"key": "realtime", "label": "Thời gian thực"})
    if ((a.get("ev_chargers") or {}).get("count") or 0) > 0:
        badges.append({"key": "ev", "label": "Có sạc EV"})
    if float(stats.get("fulfillment_rate") or 0) >= 0.98 and int(stats.get("total_sessions") or 0) >= 20:
        badges.append({"key": "reliable", "label": "Giữ đúng chỗ ≥ 98%"})
    return badges
