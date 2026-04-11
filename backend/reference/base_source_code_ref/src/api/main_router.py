# -*- coding: utf-8 -*-
"""
Main Router — Tong hop tat ca feature routers.

Them router moi khi tao feature moi.
Import router tu views file cua tung feature.
"""
from fastapi import APIRouter

# Auth (login, logout, refresh, me — partially public)
# from app.api.auth.auth_views import auth_router

# Feature routers
from app.api.example_feature.product_views import product_router

main_router = APIRouter()

# === Auth ===
# main_router.include_router(auth_router)

# === Admin panel ===
# main_router.include_router(users_router)
# main_router.include_router(roles_router)
# main_router.include_router(stores_router)
# main_router.include_router(tenants_router)

# === Feature routers ===
main_router.include_router(product_router)
# main_router.include_router(order_router)
# main_router.include_router(report_router)
