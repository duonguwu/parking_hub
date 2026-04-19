# -*- coding: utf-8 -*-
"""Capacity utilities — real-time state, snapshots, predictor."""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median
from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.api.capacity.capacity_models import CapacitySnapshotModel
from app.api.booking.booking_models import BookingModel
from app.api.garage.garage_models import GarageModel
from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


@dataclass
class CapacityState:
    vehicles_in_service: float
    vehicles_waiting: float
    available_bays: int
    wait_minutes: int
    confidence: float = 1.0    # 0..1, lower = less data

    def to_dict(self) -> dict:
        return {
            "vehicles_in_service": round(self.vehicles_in_service, 1),
            "vehicles_waiting": round(self.vehicles_waiting, 1),
            "available_bays": self.available_bays,
            "wait_minutes": self.wait_minutes,
            "confidence": round(self.confidence, 2),
        }


def _now() -> datetime:
    return get_current_time()


# ── Real-time load update ────────────────────────────────────────

async def apply_event(garage_id: ObjectId, event: str) -> None:
    """
    Adjust garages.current_load counters based on a booking event.

    Events:
        arrived   → waiting += 1
        started   → in_service += 1, waiting -= 1
        completed → in_service -= 1
        cancel_at_garage → waiting -= 1  (only if they had arrived)
    """
    garage = await GarageModel.collection.find_one({"_id": garage_id})
    if not garage:
        return
    cur = dict(garage.get("current_load") or {})
    in_svc = int(cur.get("vehicles_in_service") or 0)
    waiting = int(cur.get("vehicles_waiting") or 0)

    if event == "arrived":
        waiting += 1
    elif event == "started":
        in_svc += 1
        waiting = max(0, waiting - 1)
    elif event == "completed":
        in_svc = max(0, in_svc - 1)
    elif event == "cancel_at_garage":
        waiting = max(0, waiting - 1)

    total_bays = int((garage.get("capacity") or {}).get("total_bays", 1))
    avg_proc = int((garage.get("capacity") or {}).get("avg_processing_time_minutes", 25))
    wait_min = estimate_wait(waiting, max(0, total_bays - in_svc), avg_proc)

    await GarageModel.collection.update_one(
        {"_id": garage_id},
        {"$set": {
            "current_load.vehicles_in_service": in_svc,
            "current_load.vehicles_waiting": waiting,
            "current_load.estimated_wait_minutes": wait_min,
            "current_load.last_updated": _now(),
        }},
    )


async def take_snapshot(garage_id: ObjectId) -> None:
    """Insert a capacity_snapshots row reflecting the current load."""
    garage = await GarageModel.collection.find_one({"_id": garage_id})
    if not garage:
        return
    cur = garage.get("current_load") or {}
    total_bays = int((garage.get("capacity") or {}).get("total_bays", 1))
    in_svc = int(cur.get("vehicles_in_service") or 0)
    ts = _now()
    doc = {
        "tenant_id": garage.get("tenant_id", "platform"),
        "garage_id": garage_id,
        "timestamp": ts,
        "vehicles_in_service": in_svc,
        "vehicles_waiting": int(cur.get("vehicles_waiting") or 0),
        "available_bays": max(0, total_bays - in_svc),
        "estimated_wait_minutes": int(cur.get("estimated_wait_minutes") or 0),
        "staff_on_duty": int(cur.get("staff_on_duty") or 0),
        "hour_of_day": ts.hour,
        "day_of_week": ts.weekday(),
        "created_at": ts, "updated_at": ts,
        "created_by": "system", "updated_by": "system",
    }
    await CapacitySnapshotModel.collection.insert_one(doc)


# ── Helpers ─────────────────────────────────────────────────────

def estimate_wait(waiting: float, available_bays: int, avg_processing_minutes: int) -> int:
    """
    Estimate wait (minutes) for a new customer arriving now.
    If bays available → 0. Else: rough FIFO queue at processing rate.
    """
    if available_bays > 0 and waiting <= 0:
        return 0
    if available_bays <= 0:
        available_bays = 1   # avoid div-by-zero; assume at least 1 bay processing
    return int((waiting / available_bays) * avg_processing_minutes)


# ── Capacity Predictor ──────────────────────────────────────────

async def _pipeline_projection(
    garage: dict, confirmed_bookings: List[dict], at_time: datetime,
) -> CapacityState:
    """
    Project state at at_time by simulating current bookings forward.

    Simple model: assume any booking whose requested_time <= at_time and
    the service isn't expected to be done yet contributes to load.
    """
    avg_proc = int((garage.get("capacity") or {}).get("avg_processing_time_minutes", 25))
    total_bays = int((garage.get("capacity") or {}).get("total_bays", 1))

    in_svc = 0
    waiting = 0
    for b in confirmed_bookings:
        rt = b.get("requested_time")
        if rt is None:
            continue
        expected_end = rt + timedelta(minutes=avg_proc)
        if rt <= at_time <= expected_end:
            in_svc += 1
        elif rt <= at_time and expected_end < at_time:
            # Already finished by at_time
            continue
        # Future bookings ignored (they'll arrive after at_time)

    # Overflow: if in_svc > bays, excess waits
    if in_svc > total_bays:
        waiting += in_svc - total_bays
        in_svc = total_bays
    return CapacityState(
        vehicles_in_service=in_svc,
        vehicles_waiting=waiting,
        available_bays=max(0, total_bays - in_svc),
        wait_minutes=estimate_wait(waiting, max(1, total_bays - in_svc), avg_proc),
    )


def _decay_state(current: dict, minutes_ahead: float, avg_proc: int, total_bays: int) -> CapacityState:
    """
    Current state naturally decays: each bay processes ~avg_proc minutes/vehicle.
    After minutes_ahead minutes → roughly `minutes_ahead / avg_proc` fewer in_service.
    """
    in_svc = float(current.get("vehicles_in_service") or 0)
    waiting = float(current.get("vehicles_waiting") or 0)
    # Rate: each bay processes 1/avg_proc vehicles per minute
    processed = total_bays * (minutes_ahead / max(avg_proc, 1))
    # First drain from in_svc, then from waiting as bays free up
    new_in_svc = max(0.0, in_svc - processed)
    drain_remaining = processed - in_svc
    new_waiting = max(0.0, waiting - max(0.0, drain_remaining))
    return CapacityState(
        vehicles_in_service=new_in_svc,
        vehicles_waiting=new_waiting,
        available_bays=int(max(0, total_bays - round(new_in_svc))),
        wait_minutes=estimate_wait(new_waiting, int(max(1, total_bays - round(new_in_svc))), avg_proc),
    )


async def _historical_baseline(
    garage_id: ObjectId, hour: int, dow: int, total_bays: int, avg_proc: int,
) -> CapacityState:
    """Median of snapshots from last 4 weeks at same hour+dow."""
    cutoff = _now() - timedelta(weeks=4)
    docs = await CapacitySnapshotModel.collection.find({
        "garage_id": garage_id,
        "hour_of_day": hour,
        "day_of_week": dow,
        "timestamp": {"$gte": cutoff},
    }).to_list(length=300)

    if len(docs) < 5:
        return CapacityState(
            vehicles_in_service=0,
            vehicles_waiting=0,
            available_bays=total_bays,
            wait_minutes=0,
            confidence=0.3,
        )
    in_svc_m = median([d.get("vehicles_in_service", 0) for d in docs])
    wait_m = median([d.get("vehicles_waiting", 0) for d in docs])
    return CapacityState(
        vehicles_in_service=float(in_svc_m),
        vehicles_waiting=float(wait_m),
        available_bays=int(max(0, total_bays - round(in_svc_m))),
        wait_minutes=estimate_wait(wait_m, max(1, total_bays - round(in_svc_m)), avg_proc),
        confidence=min(1.0, len(docs) / 50.0),
    )


async def predict_capacity(garage_id: str, at_time: datetime) -> CapacityState:
    """
    Blend 3 components by how far ahead we're predicting.
    See phase2 doc §4.2.
    """
    oid = convert_mongo_object_id(garage_id) if isinstance(garage_id, str) else garage_id
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")

    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    total_bays = int((garage.get("capacity") or {}).get("total_bays", 1))
    avg_proc = int((garage.get("capacity") or {}).get("avg_processing_time_minutes", 25))
    current = garage.get("current_load") or {}

    minutes_ahead = max(0.0, (at_time - _now()).total_seconds() / 60.0)

    # Component 1: Pipeline projection
    conf_bookings = await BookingModel.collection.find({
        "garage_id": oid,
        "status": {"$in": ["confirmed", "customer_arriving", "customer_arrived", "in_service"]},
        "requested_time": {
            "$gte": _now() - timedelta(minutes=avg_proc * 2),
            "$lte": at_time + timedelta(minutes=30),
        },
    }).to_list(length=200)
    pipeline = await _pipeline_projection(garage, conf_bookings, at_time)

    # Component 2: Baseline
    baseline = await _historical_baseline(
        oid, at_time.hour, at_time.weekday(), total_bays, avg_proc,
    )

    # Component 3: Current state decay
    decayed = _decay_state(current, minutes_ahead, avg_proc, total_bays)

    # Blend weights by horizon
    if minutes_ahead < 15:
        w = {"pipeline": 0.7, "decayed": 0.2, "baseline": 0.1}
    elif minutes_ahead < 60:
        w = {"pipeline": 0.5, "decayed": 0.1, "baseline": 0.4}
    else:
        w = {"pipeline": 0.2, "decayed": 0.0, "baseline": 0.8}

    in_svc = (w["pipeline"] * pipeline.vehicles_in_service +
              w["decayed"] * decayed.vehicles_in_service +
              w["baseline"] * baseline.vehicles_in_service)
    waiting = (w["pipeline"] * pipeline.vehicles_waiting +
               w["decayed"] * decayed.vehicles_waiting +
               w["baseline"] * baseline.vehicles_waiting)

    in_svc_int = round(in_svc)
    available = max(0, total_bays - in_svc_int)
    wait_min = estimate_wait(waiting, max(1, available), avg_proc)

    # Combined confidence
    conf = w["pipeline"] * pipeline.confidence + w["baseline"] * baseline.confidence + w["decayed"] * 1.0
    return CapacityState(
        vehicles_in_service=in_svc,
        vehicles_waiting=waiting,
        available_bays=available,
        wait_minutes=wait_min,
        confidence=min(1.0, conf),
    )


# ── Manual update endpoint logic ────────────────────────────────

async def manual_update_load(
    garage_id: str, vehicles_in_service: int, vehicles_waiting: int,
    current_user: dict,
) -> bool:
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    # tenant enforcement: only garage's own tenant or super_admin
    if (current_user.get("tenant_id") != "super_admin" and
            garage.get("tenant_id") != current_user.get("tenant_id")):
        raise HTTPException(status_code=403, detail="Not your garage")

    total_bays = int((garage.get("capacity") or {}).get("total_bays", 1))
    avg_proc = int((garage.get("capacity") or {}).get("avg_processing_time_minutes", 25))
    wait_min = estimate_wait(
        vehicles_waiting, max(1, total_bays - vehicles_in_service), avg_proc,
    )
    await GarageModel.collection.update_one(
        {"_id": oid},
        {"$set": {
            "current_load.vehicles_in_service": int(vehicles_in_service),
            "current_load.vehicles_waiting": int(vehicles_waiting),
            "current_load.estimated_wait_minutes": wait_min,
            "current_load.last_updated": _now(),
        }},
    )
    await take_snapshot(oid)
    return True


async def get_current_and_predicted(garage_id: str, horizons_min: List[int] = None) -> dict:
    """Public — current load + predicted at N horizons."""
    horizons_min = horizons_min or [15, 30, 60]
    oid = convert_mongo_object_id(garage_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid garage id")
    garage = await GarageModel.collection.find_one({"_id": oid})
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    current = garage.get("current_load") or {}
    future = {}
    for mins in horizons_min:
        pred = await predict_capacity(str(oid), _now() + timedelta(minutes=mins))
        future[f"t+{mins}min"] = pred.to_dict()
    return {
        "garage_id": str(oid),
        "current": {
            "vehicles_in_service": int(current.get("vehicles_in_service") or 0),
            "vehicles_waiting": int(current.get("vehicles_waiting") or 0),
            "estimated_wait_minutes": int(current.get("estimated_wait_minutes") or 0),
            "last_updated": str(current.get("last_updated") or ""),
        },
        "predicted": future,
    }
