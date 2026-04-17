# -*- coding: utf-8 -*-
"""Main Router — Aggregate all feature routers."""
from fastapi import APIRouter

from app.api.auth.auth_views import auth_router
from app.api.tenant.tenant_views import tenant_router
from app.api.user.user_views import user_router
from app.api.garage.garage_views import garage_router
from app.api.vehicle.vehicle_views import vehicle_router

main_router = APIRouter()

# ── Auth (partially public) ──
main_router.include_router(auth_router)

# ── Admin ──
main_router.include_router(tenant_router)
main_router.include_router(user_router)

# ── Domain features ──
main_router.include_router(garage_router)
main_router.include_router(vehicle_router)

# ── Future Phase 2+ ──
# main_router.include_router(booking_router)
# main_router.include_router(matching_router)
# main_router.include_router(service_type_router)
