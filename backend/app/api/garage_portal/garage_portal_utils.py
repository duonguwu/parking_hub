# -*- coding: utf-8 -*-
"""
Garage Owner Portal — Business logic helpers.

All data is scoped to the current user's tenant garage.
Reuses existing models/utils; no duplication with core operations.
"""
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException

from app.api.booking.booking_models import BookingModel
from app.api.capacity.capacity_models import CapacitySnapshotModel
from app.api.garage.garage_models import GarageModel
from app.api.garage_service.garage_service_models import GarageServiceModel
from app.api.garage_service.garage_service_utils import format_garage_service, upsert_garage_service
from app.api.service_type.service_type_models import ServiceTypeModel
from app.api.user.user_models import UserModel
from app.api.vehicle.vehicle_models import VehicleModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)

# ── Icon mapping for service types ───────────────────────────────
_ICON_MAP = {
    "park_hourly": "clock",
    "park_overnight": "moon",
    "park_daily": "calendar-days",
    "park_monthly": "credit-card",
}

# ── Tier labels ──────────────────────────────────────────────────
_TIER_NAMES = {1: "Basic", 2: "Standard", 3: "Pro", 4: "Elite"}

# ── Tier next-level requirements ────────────────────────────────
_TIER_REQUIREMENTS = {
    2: {"avg_rating": 3.5, "training_certs": 3},
    3: {"avg_rating": 4.2, "training_certs": 5},
    4: {"avg_rating": 4.7, "training_certs": 8},
}


def _parse_range_days(range_str: str) -> int:
    return {"7D": 7, "30D": 30, "90D": 90, "1Y": 365}.get((range_str or "30D").upper(), 30)


# ── Garage Resolution ────────────────────────────────────────────

async def get_garage_for_user(current_user: dict, garage_id_override: Optional[str] = None) -> dict:
    """Resolve the garage document for the authenticated user.

    For super_admin: garage_id_override is required.
    For tenant roles: find first active garage by tenant_id.
    """
    if garage_id_override:
        oid = convert_mongo_object_id(garage_id_override)
        if not oid:
            raise HTTPException(status_code=400, detail="Invalid garage_id")
        garage = await GarageModel.collection.find_one({"_id": oid})
        if not garage:
            raise HTTPException(status_code=404, detail="Garage not found")
        if (current_user.get("tenant_id") != "super_admin" and
                garage.get("tenant_id") != current_user.get("tenant_id")):
            raise HTTPException(status_code=403, detail="Access denied")
        return garage

    tenant_id = current_user.get("tenant_id")
    if not tenant_id or tenant_id == "super_admin":
        raise HTTPException(status_code=400, detail="Provide garage_id for super_admin access")

    garage = await GarageModel.collection.find_one({"tenant_id": tenant_id, "status": "active"})
    if not garage:
        raise HTTPException(status_code=404, detail="No active garage found for your account")
    return garage


# ── Dashboard Overview ───────────────────────────────────────────

async def get_dashboard_overview(garage: dict) -> dict:
    garage_oid = garage["_id"]
    now = get_current_time()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    yesterday_start = today_start - timedelta(days=1)
    cancelled_statuses = ["cancelled_by_customer", "cancelled_by_garage", "expired", "no_show"]

    # Today's cars (non-cancelled)
    todays_count = await BookingModel.collection.count_documents({
        "garage_id": garage_oid,
        "created_at": {"$gte": today_start, "$lt": today_end},
        "status": {"$nin": cancelled_statuses},
    })
    yesterday_count = await BookingModel.collection.count_documents({
        "garage_id": garage_oid,
        "created_at": {"$gte": yesterday_start, "$lt": today_start},
        "status": {"$nin": cancelled_statuses},
    })

    total_bays = int((garage.get("capacity") or {}).get("total_bays", 2))
    daily_capacity = max(total_bays * 8, 1)
    capacity_pct = min(100, int((todays_count / daily_capacity) * 100))
    if yesterday_count > 0:
        delta = int(((todays_count - yesterday_count) / yesterday_count) * 100)
        car_trend = f"+{delta}%" if delta >= 0 else f"{delta}%"
    else:
        car_trend = "+0%"

    # Revenue today (completed)
    today_completed = await BookingModel.collection.find({
        "garage_id": garage_oid,
        "status": "completed",
        "timestamps.service_completed_at": {"$gte": today_start, "$lt": today_end},
    }).to_list(length=None)
    revenue_today = sum(int(b.get("price", 0)) for b in today_completed)

    yesterday_completed = await BookingModel.collection.find({
        "garage_id": garage_oid,
        "status": "completed",
        "timestamps.service_completed_at": {"$gte": yesterday_start, "$lt": today_start},
    }).to_list(length=None)
    revenue_yesterday = sum(int(b.get("price", 0)) for b in yesterday_completed)
    revenue_trend = "UP" if revenue_today >= revenue_yesterday else "DOWN"

    # Revenue sparkline (last 5 days including today)
    sparkline = []
    for i in range(4, -1, -1):
        ds = today_start - timedelta(days=i)
        de = ds + timedelta(days=1)
        day_docs = await BookingModel.collection.find({
            "garage_id": garage_oid,
            "status": "completed",
            "timestamps.service_completed_at": {"$gte": ds, "$lt": de},
        }).to_list(length=None)
        sparkline.append(sum(int(b.get("price", 0)) for b in day_docs))

    # Match score from garage stats
    stats = garage.get("stats") or {}
    avg_rating = round(float(stats.get("avg_rating") or 4.5), 1)
    total_reviews = int(stats.get("total_services") or 0)

    # Fill rate from current_load
    current_load = garage.get("current_load") or {}
    in_service = int(current_load.get("vehicles_in_service") or 0)
    waiting = int(current_load.get("vehicles_waiting") or 0)
    fill_rate = min(100, int(((in_service + waiting) / max(total_bays, 1)) * 100))
    remaining = max(0, total_bays - in_service - waiting)

    if fill_rate >= 80 or capacity_pct >= 80:
        status = "LIVE PEAK"
    elif fill_rate >= 40 or capacity_pct >= 40:
        status = "NORMAL"
    else:
        status = "SLOW"

    avg_time_mins = int(stats.get("avg_actual_processing_minutes") or 0)

    return {
        "status": status,
        "kpis": {
            "todays_cars": {"value": todays_count, "trend": car_trend, "capacity_percent": capacity_pct},
            "revenue": {"value": revenue_today, "trend": revenue_trend, "sparkline": sparkline},
            "match_score": {"value": avg_rating, "total_reviews": total_reviews},
            "fill_rate": {"value": fill_rate, "remaining_capacity": remaining},
        },
        "bottom_stats": {
            "efficiency": {
                "avg_service_time_seconds": avg_time_mins * 60,
                "trend_text": "Within normal range" if avg_time_mins > 0 else "No data yet",
            },
            "resources": {
                "water_usage_liters": todays_count * 50,
                "status": "Within blueprint limits",
            },
            "conversion": {
                "new_subscriptions": todays_count,
                "trend_text": f"+{todays_count} new leads today",
            },
        },
    }


# ── Capacity Chart ───────────────────────────────────────────────

async def get_capacity_chart(garage: dict, range_str: str) -> dict:
    garage_oid = garage["_id"]
    now = get_current_time()
    total_bays = max(int((garage.get("capacity") or {}).get("total_bays", 2)), 1)

    if range_str == "24H":
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        snapshots = await CapacitySnapshotModel.collection.find({
            "garage_id": garage_oid,
            "timestamp": {"$gte": today_start, "$lt": today_start + timedelta(days=1)},
        }).to_list(length=500)

        hour_loads: dict[int, list] = defaultdict(list)
        for s in snapshots:
            h = int(s.get("hour_of_day", 0))
            load = int(s.get("vehicles_in_service", 0)) + int(s.get("vehicles_waiting", 0))
            hour_loads[h].append(load)

        labels = [f"{h:02d}:00" for h in range(24)]
        data = []
        for h in range(24):
            if hour_loads[h]:
                avg = sum(hour_loads[h]) / len(hour_loads[h])
                data.append(min(100, int((avg / total_bays) * 100)))
            else:
                data.append(0)

        return {"range": "24H", "labels": labels, "data": data}

    else:  # 7D
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
        snapshots = await CapacitySnapshotModel.collection.find({
            "garage_id": garage_oid,
            "timestamp": {"$gte": week_start},
        }).to_list(length=2000)

        day_loads: dict[str, list] = defaultdict(list)
        for s in snapshots:
            ts = s.get("timestamp")
            if ts:
                day_key = ts.strftime("%Y-%m-%d")
                load = int(s.get("vehicles_in_service", 0)) + int(s.get("vehicles_waiting", 0))
                day_loads[day_key].append(load)

        labels = []
        data = []
        for i in range(6, -1, -1):
            d = now - timedelta(days=i)
            key = d.strftime("%Y-%m-%d")
            label = d.strftime("%a")
            labels.append(label)
            if day_loads[key]:
                avg = sum(day_loads[key]) / len(day_loads[key])
                data.append(min(100, int((avg / total_bays) * 100)))
            else:
                data.append(0)

        return {"range": "7D", "labels": labels, "data": data}


# ── Queue ────────────────────────────────────────────────────────

async def get_queue(garage: dict, filter_str: str, page: int, limit: int) -> dict:
    garage_oid = garage["_id"]
    now = get_current_time()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    cancelled_statuses = ["cancelled_by_customer", "cancelled_by_garage", "expired", "no_show"]

    # Build query
    query: dict = {"garage_id": garage_oid}
    if filter_str == "today":
        query["created_at"] = {"$gte": today_start, "$lt": today_end}
        query["status"] = {"$nin": cancelled_statuses}
    elif filter_str == "pending":
        query["status"] = "pending"
    # "all" → no extra filter

    total_items = await BookingModel.collection.count_documents(query)
    skip = (page - 1) * limit
    total_pages = max(1, -(-total_items // limit))  # ceiling division

    bookings = await BookingModel.collection.find(query).sort(
        "requested_time", 1
    ).skip(skip).limit(limit).to_list(length=limit)

    # Hero stats (always scoped to today)
    today_query = {
        "garage_id": garage_oid,
        "created_at": {"$gte": today_start, "$lt": today_end},
        "status": {"$nin": cancelled_statuses},
    }
    active_count = await BookingModel.collection.count_documents({
        **today_query,
        "status": {"$in": ["confirmed", "customer_arriving", "customer_arrived", "in_service"]},
    })
    pending_count = await BookingModel.collection.count_documents({
        "garage_id": garage_oid,
        "status": "pending",
    })
    total_bays = max(int((garage.get("capacity") or {}).get("total_bays", 2)), 1)

    today_total = await BookingModel.collection.count_documents(today_query)
    capacity_pct = min(100, int((today_total / max(total_bays * 8, 1)) * 100))

    # Batch-load users, vehicles, service types for enrichment
    customer_ids = [b["customer_id"] for b in bookings if b.get("customer_id")]
    vehicle_ids = [b["vehicle_id"] for b in bookings if b.get("vehicle_id")]
    service_codes = list({b.get("service_type_code", "") for b in bookings})

    user_docs = {}
    if customer_ids:
        for u in await UserModel.collection.find({"_id": {"$in": customer_ids}}).to_list(length=len(customer_ids)):
            user_docs[u["_id"]] = u

    vehicle_docs = {}
    if vehicle_ids:
        for v in await VehicleModel.collection.find({"_id": {"$in": vehicle_ids}}).to_list(length=len(vehicle_ids)):
            vehicle_docs[v["_id"]] = v

    stype_docs = {}
    if service_codes:
        for st in await ServiceTypeModel.collection.find({"code": {"$in": service_codes}}).to_list(length=len(service_codes)):
            stype_docs[st["code"]] = st

    gsvc_docs = {}
    if service_codes:
        for gs in await GarageServiceModel.collection.find({
            "garage_id": garage_oid,
            "service_type_code": {"$in": service_codes},
        }).to_list(length=len(service_codes)):
            gsvc_docs[gs["service_type_code"]] = gs

    items = []
    for b in bookings:
        cid = b.get("customer_id")
        vid = b.get("vehicle_id")
        code = b.get("service_type_code", "")
        user = user_docs.get(cid) if cid else None
        vehicle = vehicle_docs.get(vid) if vid else None
        stype = stype_docs.get(code)
        gsvc = gsvc_docs.get(code)

        customer_name = user.get("name", "Unknown") if user else "Unknown"

        vehicle_info = {
            "type": (vehicle.get("vehicle_type", "car") if vehicle else "car"),
            "name": (f"{vehicle.get('brand', '')} {vehicle.get('model', '')}".strip() if vehicle else ""),
            "plate": (vehicle.get("license_plate", "") if vehicle else ""),
        }

        duration_min = int((gsvc or {}).get("estimated_duration_minutes") or 30)
        rt = b.get("requested_time")
        eta = ""
        if rt:
            eta_dt = rt + timedelta(minutes=duration_min)
            eta = eta_dt.strftime("%H:%M")

        service_info = {
            "name": (stype.get("name", code) if stype else code),
            "description": (stype.get("description", "") if stype else ""),
            "eta": eta,
        }

        items.append({
            "id": b.get("booking_code", str(b["_id"])),
            "appointment_time": rt.isoformat() if rt else None,
            "customer_name": customer_name,
            "vehicle": vehicle_info,
            "service": service_info,
            "status": b.get("status", "pending"),
        })

    # AI insight
    ai_insight = _generate_ai_insight(bookings, now)

    return {
        "hero_stats": {
            "capacity_percent": capacity_pct,
            "active_bookings": active_count,
            "pending_approval": pending_count,
        },
        "ai_insight": ai_insight,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
        },
        "items": items,
    }


def _generate_ai_insight(bookings: list, now: datetime) -> dict:
    if not bookings:
        return {"title": "Queue Status", "message": "No bookings in this view. Ready to accept new customers."}

    hour_counts: dict[int, int] = defaultdict(int)
    for b in bookings:
        rt = b.get("requested_time")
        if rt:
            hour_counts[rt.hour] += 1

    if hour_counts:
        peak_hour = max(hour_counts, key=lambda h: hour_counts[h])
        peak_count = hour_counts[peak_hour]
        if peak_count >= 3:
            end_hour = (peak_hour + 3) % 24
            return {
                "title": "Coordination Insight",
                "message": (
                    f"High volume expected between {peak_hour:02d}:00 and {end_hour:02d}:00 today "
                    f"({peak_count} bookings). We recommend assigning an extra technician for that window."
                ),
            }

    return {
        "title": "Queue Status",
        "message": f"{len(bookings)} booking(s) in queue. Operations are running smoothly.",
    }


# ── Analytics ────────────────────────────────────────────────────

async def get_analytics(garage: dict, range_str: str) -> dict:
    garage_oid = garage["_id"]
    range_days = _parse_range_days(range_str)
    now = get_current_time()
    period_start = now - timedelta(days=range_days)
    prev_start = period_start - timedelta(days=range_days)
    cancelled_statuses = ["cancelled_by_customer", "cancelled_by_garage", "no_show"]

    all_docs = await BookingModel.collection.find({
        "garage_id": garage_oid,
        "created_at": {"$gte": period_start},
    }).to_list(length=10000)

    prev_docs = await BookingModel.collection.find({
        "garage_id": garage_oid,
        "created_at": {"$gte": prev_start, "$lt": period_start},
    }).to_list(length=10000)

    completed = [b for b in all_docs if b.get("status") == "completed"]
    cancelled = [b for b in all_docs if b.get("status") in cancelled_statuses]
    prev_completed = [b for b in prev_docs if b.get("status") == "completed"]

    gross_revenue = sum(int(b.get("price", 0)) for b in completed)
    prev_revenue = sum(int(b.get("price", 0)) for b in prev_completed)
    active_count = len([b for b in all_docs if b.get("status") not in (cancelled_statuses + ["expired"])])
    prev_active = len([b for b in prev_docs if b.get("status") not in (cancelled_statuses + ["expired"])])

    # Revenue trend
    rev_trend, rev_up = _compute_trend(gross_revenue, prev_revenue)
    booking_trend, booking_up = _compute_trend(active_count, prev_active)

    # Customer satisfaction
    rated = [b for b in completed if b.get("feedback", {}).get("rating")]
    avg_sat = (sum(b["feedback"]["rating"] for b in rated) / len(rated)) if rated else 0.0

    # Conversion rate
    total = len(all_docs)
    conversion = ((total - len(cancelled)) / max(total, 1)) * 100

    # Revenue chart
    labels, chart_data = _build_revenue_chart(completed, range_days, now)

    # Customer retention
    cust_counts = Counter(str(b.get("customer_id", "")) for b in all_docs if b.get("customer_id"))
    returning_count = sum(1 for cnt in cust_counts.values() if cnt > 1)
    new_count = len(cust_counts) - returning_count
    total_custs = len(cust_counts)
    returning_pct = int((returning_count / max(total_custs, 1)) * 100)

    # Service distribution (enrich code → name)
    svc_counts = Counter(b.get("service_type_code", "unknown") for b in all_docs)
    total_svc = sum(svc_counts.values()) or 1
    top_codes = [code for code, _ in svc_counts.most_common(5)]
    stype_map = {}
    if top_codes:
        for st in await ServiceTypeModel.collection.find({"code": {"$in": top_codes}}).to_list(length=10):
            stype_map[st["code"]] = st.get("name", st["code"])

    distribution = []
    total_so_far = 0
    for i, (code, count) in enumerate(svc_counts.most_common(3)):
        pct = int((count / total_svc) * 100)
        total_so_far += pct
        distribution.append({
            "name": stype_map.get(code, code),
            "percentage": pct if i < 2 else max(0, 100 - total_so_far + pct),
        })

    return {
        "metrics": {
            "gross_revenue": {"value": gross_revenue, "trend": rev_trend, "is_up": rev_up},
            "active_bookings": {"value": active_count, "trend": booking_trend, "is_up": booking_up},
            "customer_sat": {"value": round(avg_sat, 2), "trend": "MAX" if avg_sat >= 4.9 else f"{avg_sat:.1f}", "is_up": avg_sat >= 4.0},
            "conversion_rate": {"value": round(conversion, 1), "trend": f"{conversion:.1f}%", "is_up": conversion >= 80},
        },
        "revenue_chart": {"labels": labels, "data": chart_data},
        "customer_retention": {
            "returning_percentage": returning_pct,
            "returning_count": returning_count,
            "new_count": new_count,
        },
        "service_distribution": distribution,
    }


def _compute_trend(current: float, previous: float) -> tuple[str, bool]:
    if previous == 0:
        return ("+0%", True)
    delta = ((current - previous) / previous) * 100
    is_up = delta >= 0
    return (f"+{delta:.1f}%" if is_up else f"{delta:.1f}%", is_up)


def _build_revenue_chart(completed: list, range_days: int, now: datetime) -> tuple[list, list]:
    if range_days <= 7:
        # Daily
        day_rev: dict[str, int] = defaultdict(int)
        for b in completed:
            ts = (b.get("timestamps") or {}).get("service_completed_at") or b.get("created_at")
            if ts:
                day_rev[ts.strftime("%Y-%m-%d")] += int(b.get("price", 0))
        labels = []
        data = []
        for i in range(range_days - 1, -1, -1):
            d = now - timedelta(days=i)
            key = d.strftime("%Y-%m-%d")
            labels.append(d.strftime("%a"))
            data.append(day_rev.get(key, 0))
    elif range_days <= 30:
        # Weekly (last 4-5 weeks)
        week_rev: dict[str, int] = defaultdict(int)
        for b in completed:
            ts = (b.get("timestamps") or {}).get("service_completed_at") or b.get("created_at")
            if ts:
                week_start = ts - timedelta(days=ts.weekday())
                week_rev[week_start.strftime("%Y-%m-%d")] += int(b.get("price", 0))
        weeks = sorted(week_rev.keys())[-5:]
        labels = [f"W{i + 1}" for i in range(len(weeks))]
        data = [week_rev[w] for w in weeks]
    else:
        # Monthly
        month_rev: dict[str, int] = defaultdict(int)
        for b in completed:
            ts = (b.get("timestamps") or {}).get("service_completed_at") or b.get("created_at")
            if ts:
                month_rev[ts.strftime("%b")] += int(b.get("price", 0))
        months_ordered = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        labels = [m for m in months_ordered if m in month_rev][-5:]
        data = [month_rev[m] for m in labels]

    return labels or ["No data"], data or [0]


# ── Services Overview ────────────────────────────────────────────

async def get_services_overview(garage: dict) -> dict:
    garage_oid = garage["_id"]

    services_docs = await GarageServiceModel.collection.find({
        "garage_id": garage_oid, "is_available": True,
    }).to_list(length=100)

    active_count = len(services_docs)
    avg_duration = int(
        sum(d.get("estimated_duration_minutes", 30) for d in services_docs) / max(active_count, 1)
    )

    # Revenue efficiency: completed bookings this month / (services * 30 days) * 100
    now = get_current_time()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_completed = await BookingModel.collection.count_documents({
        "garage_id": garage_oid,
        "status": "completed",
        "timestamps.service_completed_at": {"$gte": month_start},
    })
    rev_efficiency = min(100, int((month_completed / max(active_count * 30, 1)) * 100))

    # Enrich services with service type info
    codes = [d.get("service_type_code", "") for d in services_docs]
    stype_map = {}
    if codes:
        for st in await ServiceTypeModel.collection.find({"code": {"$in": codes}}).to_list(length=50):
            stype_map[st["code"]] = st

    # Count bookings per service for popularity tags
    svc_counts = Counter()
    if codes:
        for b in await BookingModel.collection.find({
            "garage_id": garage_oid,
            "service_type_code": {"$in": codes},
        }, {"service_type_code": 1}).to_list(length=5000):
            svc_counts[b.get("service_type_code", "")] += 1

    most_popular_code = svc_counts.most_common(1)[0][0] if svc_counts else ""

    services = []
    for d in services_docs:
        code = d.get("service_type_code", "")
        stype = stype_map.get(code)
        tags = []
        if code == most_popular_code:
            tags.append("Popular")
        if (stype or {}).get("category") == "coating":
            tags.append("Premium")

        services.append({
            "id": str(d.get("_id") or ""),
            "name": (stype.get("name", code) if stype else code),
            "description": (stype.get("description", "") if stype else ""),
            "price_usd": int(d.get("price", 0)),
            "duration_minutes": int(d.get("estimated_duration_minutes", 30)),
            "icon_type": _ICON_MAP.get(code, "droplets"),
            "tags": tags,
        })

    return {
        "stats": {
            "active_services": active_count,
            "avg_completion_time_mins": avg_duration,
            "revenue_efficiency_percent": rev_efficiency,
        },
        "upsell_recommendation": {
            "title": "Seasonal Care Packages",
            "description": (
                "Bundle your services to increase your average booking value by 22%. "
                "Consider pairing wash + interior services as a package deal."
            ),
        },
        "services": services,
    }


# ── Service CRUD helpers ─────────────────────────────────────────

async def create_portal_service(
    garage: dict,
    service_type_code: str,
    price: int,
    duration_minutes: Optional[int],
    current_user: dict,
) -> dict:
    stype = stype_map_entry = await ServiceTypeModel.collection.find_one({"code": service_type_code})
    if not stype:
        raise HTTPException(status_code=404, detail=f"Service type '{service_type_code}' not found in catalog")

    result = await upsert_garage_service(
        garage_id=str(garage["_id"]),
        service_type_code=service_type_code,
        price=price,
        estimated_duration_minutes=duration_minutes,
        current_user=current_user,
    )

    code = result.get("service_type_code", "")
    return {
        "id": result["id"],
        "name": stype.get("name", code),
        "description": stype.get("description", ""),
        "price_usd": result["price"],
        "duration_minutes": result["estimated_duration_minutes"],
        "icon_type": _ICON_MAP.get(code, "droplets"),
        "tags": [],
    }


async def update_portal_service(
    service_id: str,
    price: Optional[int],
    duration_minutes: Optional[int],
    current_user: dict,
) -> dict:
    oid = convert_mongo_object_id(service_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid service ID")
    doc = await GarageServiceModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Service not found")
    if (current_user.get("tenant_id") != "super_admin" and
            doc.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Access denied")

    now = get_current_time()
    set_fields: dict = {"updated_at": now, "updated_by": current_user.get("username", "")}
    if price is not None:
        set_fields["price"] = int(price)
    if duration_minutes is not None:
        set_fields["estimated_duration_minutes"] = int(duration_minutes)

    await GarageServiceModel.collection.update_one({"_id": oid}, {"$set": set_fields})
    updated = await GarageServiceModel.collection.find_one({"_id": oid})

    code = updated.get("service_type_code", "")
    stype = await ServiceTypeModel.collection.find_one({"code": code})
    return {
        "id": str(updated["_id"]),
        "name": (stype.get("name", code) if stype else code),
        "description": (stype.get("description", "") if stype else ""),
        "price_usd": int(updated.get("price", 0)),
        "duration_minutes": int(updated.get("estimated_duration_minutes", 30)),
        "icon_type": _ICON_MAP.get(code, "droplets"),
        "tags": [],
    }


async def delete_portal_service(service_id: str, current_user: dict) -> bool:
    oid = convert_mongo_object_id(service_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid service ID")
    doc = await GarageServiceModel.collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Service not found")
    if (current_user.get("tenant_id") != "super_admin" and
            doc.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Access denied")

    now = get_current_time()
    await GarageServiceModel.collection.update_one(
        {"_id": oid},
        {"$set": {"is_available": False, "updated_at": now, "updated_by": current_user.get("username", "")}},
    )

    # Remove from garage.services_offered if no other active service of same type remains
    garage_oid = doc.get("garage_id")
    code = doc.get("service_type_code", "")
    still_active = await GarageServiceModel.collection.find_one({
        "garage_id": garage_oid,
        "service_type_code": code,
        "is_available": True,
        "_id": {"$ne": oid},
    })
    if not still_active and garage_oid:
        await GarageModel.collection.update_one(
            {"_id": garage_oid}, {"$pull": {"services_offered": code}}
        )
    return True


# ── Match Score ──────────────────────────────────────────────────

def get_score_data(garage: dict) -> dict:
    ta = garage.get("tier_assessment") or {}
    equipment = int(ta.get("equipment_score", 70))
    process = int(ta.get("process_score", 60))
    staff = int(ta.get("staff_score", 50))
    capacity = int(ta.get("capacity_score", 80))
    reliability = int(ta.get("reliability_score", 75))

    aggregate = int((equipment + process + staff + capacity + reliability) / 5)

    if aggregate >= 86:
        status_text = "ELITE"
    elif aggregate >= 71:
        status_text = "PERFORMING"
    elif aggregate >= 51:
        status_text = "OPTIMIZING"
    else:
        status_text = "NEEDS ATTENTION"

    tier = int(garage.get("tier", 1))
    current_tier = _TIER_NAMES.get(tier, "Basic")
    next_tier_num = min(tier + 1, 4)
    next_tier = _TIER_NAMES.get(next_tier_num, "Elite")

    stats = garage.get("stats") or {}
    current_rating = float(stats.get("avg_rating") or 4.0)
    target_req = _TIER_REQUIREMENTS.get(next_tier_num, {"avg_rating": 4.7, "training_certs": 8})
    current_certs = tier * 2 - 1

    # AI recommendation based on lowest score
    scores = {"equipment": equipment, "process": process, "staff": staff,
              "capacity": capacity, "reliability": reliability}
    lowest_key = min(scores, key=lambda k: scores[k])
    lowest_val = scores[lowest_key]
    rec_map = {
        "staff": ("Priority Upgrade: Staff Training",
                  f"Addressing the Staff score ({lowest_val}) could boost your aggregate efficiency by 8 points this month!"),
        "process": ("Optimize Workflow Processes",
                    f"Improving process efficiency ({lowest_val}) will reduce wait times and increase throughput."),
        "equipment": ("Equipment Maintenance Check",
                      f"Upgrading equipment condition ({lowest_val}) improves service quality and customer satisfaction."),
        "capacity": ("Expand Booking Capacity",
                     f"Improving capacity utilization ({lowest_val}) helps maximize revenue during peak hours."),
        "reliability": ("Boost Reliability Score",
                        f"Improving quality control ({lowest_val}) will increase customer return rate."),
    }
    rec_title, rec_desc = rec_map[lowest_key]

    total_bays = int((garage.get("capacity") or {}).get("total_bays", 2))
    current_load = garage.get("current_load") or {}
    active_bays = int(current_load.get("vehicles_in_service", 0))

    return {
        "aggregate_score": aggregate,
        "status_text": status_text,
        "technical_overview": {
            "comparison_text": f"{aggregate}% aggregate score",
            "active_bays": active_bays,
            "total_bays": total_bays,
            "throughput_vph": round(active_bays / max(total_bays, 1) * 2, 1),
        },
        "score_components": {
            "equipment": {"score": equipment, "description": "Condition of bays and high-pressure tech."},
            "process": {"score": process, "description": "Workflow linearity and wait-time reduction."},
            "staff": {"score": staff, "description": "Training levels and service speed metrics."},
            "capacity": {"score": capacity, "description": "Booking fill rate and downtime minimization."},
            "reliability": {"score": reliability, "description": "Quality control and customer return rate."},
        },
        "progression": {
            "current_tier": current_tier,
            "next_tier": next_tier,
            "requirements_for_next": {
                "training_certs": {"current": current_certs, "target": target_req["training_certs"]},
                "avg_rating": {"current": round(current_rating, 1), "target": target_req["avg_rating"]},
            },
        },
        "ai_recommendation": {"title": rec_title, "description": rec_desc},
    }
