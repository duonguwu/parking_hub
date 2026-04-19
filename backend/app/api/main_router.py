# -*- coding: utf-8 -*-
"""Main Router — Aggregate all feature routers."""
from fastapi import APIRouter

from app.api.auth.auth_views import auth_router
from app.api.tenant.tenant_views import tenant_router
from app.api.user.user_views import user_router
from app.api.garage.garage_views import garage_router
from app.api.vehicle.vehicle_views import vehicle_router

# Phase 2
from app.api.service_type.service_type_views import service_type_router
from app.api.garage_service.garage_service_views import garage_service_router
from app.api.booking.booking_views import booking_router
from app.api.capacity.capacity_views import capacity_router
from app.api.matching.matching_views import matching_router

main_router = APIRouter()

# ── Auth (partially public) ──
main_router.include_router(auth_router)

# ── Admin ──
main_router.include_router(tenant_router)
main_router.include_router(user_router)

# ── Domain features ──
main_router.include_router(garage_router)
main_router.include_router(vehicle_router)

# ── Phase 2: Core Operations ──
main_router.include_router(service_type_router)
main_router.include_router(garage_service_router)
main_router.include_router(booking_router)
main_router.include_router(capacity_router)
main_router.include_router(matching_router)
