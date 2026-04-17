# -*- coding: utf-8 -*-
"""
Common Enums — Operation and Resource types for standardized API responses.

Usage:
    from app.api.shared.schemas import Operation, Resource
    return api_response(operation=Operation.RETRIEVED, resource=Resource.GARAGES, data=data)
"""
from enum import Enum


class Operation(str, Enum):
    RETRIEVED = "retrieved"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CHECKED = "checked"
    VALIDATED = "validated"
    PROCESSED = "processed"
    SYNCHRONIZED = "synchronized"


class Resource(str, Enum):
    # ── Auth ──
    AUTH = "auth"
    TOKEN = "token"

    # ── Tenant ──
    TENANTS = "tenants"
    TENANT = "tenant"

    # ── User ──
    USERS = "users"
    USER = "user"

    # ── Role ──
    ROLES = "roles"
    ROLE = "role"

    # ── Garage ──
    GARAGES = "garages"
    GARAGE = "garage"
    GARAGE_CAPACITY = "garage capacity"

    # ── Vehicle ──
    VEHICLES = "vehicles"
    VEHICLE = "vehicle"

    # ── Service ──
    SERVICE_TYPES = "service types"
    SERVICE_TYPE = "service type"
    GARAGE_SERVICES = "garage services"
    GARAGE_SERVICE = "garage service"

    # ── Booking ──
    BOOKINGS = "bookings"
    BOOKING = "booking"

    # ── Matching ──
    MATCH_RESULTS = "match results"
