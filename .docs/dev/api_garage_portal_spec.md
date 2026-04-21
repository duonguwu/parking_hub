# WashMind Garage Owner Portal - API Specification

This document outlines the required REST API endpoints, request parameters, and response structures needed to power the WashMind Garage Owner Portal frontend, based on the implementation of the UI mockups.

## Base URL
`/api/v1/garage` (Authenticated via `garage_owner`, `garage_manager`, or `garage_staff` roles)

---

## 1. Garage Dashboard (`/garage`)

The Dashboard aggregates high-level operations, real-time queue data, and daily insights.

### 1.1 Get Dashboard Overview
`GET /api/v1/garage/dashboard/overview`

**Response (`200 OK`)**:
```json
{
  "status": "LIVE PEAK", // e.g., LIVE PEAK, NORMAL, SLOW
  "kpis": {
    "todays_cars": { "value": 42, "trend": "+12%", "capacity_percent": 84 },
    "revenue": { "value": 3200, "trend": "UP", "sparkline": [40, 60, 30, 80, 100] },
    "match_score": { "value": 4.9, "total_reviews": 128 },
    "fill_rate": { "value": 94, "remaining_capacity": 6 }
  },
  "bottom_stats": {
    "efficiency": { "avg_wash_time_seconds": 1122, "trend_text": "-2m from yesterday" },
    "resources": { "water_usage_liters": 1240, "status": "Within blueprint limits" },
    "conversion": { "new_subscriptions": 14, "trend_text": "+4 new leads today" }
  }
}
```

### 1.2 Get Capacity Chart
`GET /api/v1/garage/dashboard/capacity?range=24H` (or `7D`)

**Response (`200 OK`)**:
```json
{
  "range": "24H",
  "labels": ["00:00", "01:00", "02:00", "...", "23:00"],
  "data": [10, 8, 5, 5, 12, 25, 40, 65, 85, 95, 100, 90, 75, 60, 70, 80, 92, 70, 50, 35, 20, 15, 10, 5]
}
```

---

## 2. Booking Queue Management (`/garage/queue`)

Detailed view of the operational queue with actionable states.

### 2.1 Get Queue Summary & Active Bookings
`GET /api/v1/garage/queue?filter=today` (filters: `all`, `today`, `pending`)

**Response (`200 OK`)**:
```json
{
  "hero_stats": {
    "capacity_percent": 84,
    "active_bookings": 12,
    "pending_approval": 4
  },
  "ai_insight": {
    "title": "Coordination Insight",
    "message": "High volume expected between 10:00 AM and 01:00 PM today. We recommend assigning an extra technician..."
  },
  "pagination": { "current_page": 1, "total_pages": 6, "total_items": 24 },
  "items": [
    {
      "id": "WM-90210",
      "appointment_time": "2024-10-24T09:00:00Z",
      "customer_name": "Marcus Thorne",
      "vehicle": {
        "type": "car", 
        "name": "BMW M3",
        "plate": "ABC-1234"
      },
      "service": {
        "name": "Full Ceramic Coating",
        "description": "Interior + Exterior",
        "eta": "14:30"
      },
      "status": "in_progress" // pending, confirmed, in_progress, completed
    }
  ]
}
```

### 2.2 Update Booking Status
`PATCH /api/v1/garage/queue/bookings/{booking_id}`

**Body Request**:
```json
{ "status": "confirmed" } // or "completed", "cancelled"
```

---

## 3. Analytics & Growth (`/garage/analytics`)

Detailed financial and operational reporting.

### 3.1 Get Analytics Dashboard
`GET /api/v1/garage/analytics?range=30D`

**Response (`200 OK`)**:
```json
{
  "metrics": {
    "gross_revenue": { "value": 42800, "trend": "+12.4%", "is_up": true },
    "active_bookings": { "value": 1204, "trend": "+5.2%", "is_up": true },
    "customer_sat": { "value": 4.92, "trend": "MAX", "is_up": true },
    "conversion_rate": { "value": 18.4, "trend": "-2.1%", "is_up": false }
  },
  "revenue_chart": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
    "data": [4000, 6000, 3000, 8000, 10000]
  },
  "customer_retention": {
    "returning_percentage": 70,
    "returning_count": 842,
    "new_count": 362
  },
  "service_distribution": [
    { "name": "Deep Detail Wash", "percentage": 42 },
    { "name": "Ceramic Coating", "percentage": 28 },
    { "name": "Interior Sanitization", "percentage": 30 }
  ]
}
```

---

## 4. Service Management (`/garage/services`)

CRUD endpoints for the garage's available packages and configurations.

### 4.1 Get Services Overview
`GET /api/v1/garage/services`

**Response (`200 OK`)**:
```json
{
  "stats": {
    "active_services": 12,
    "avg_completion_time_mins": 145,
    "revenue_efficiency_percent": 94
  },
  "upsell_recommendation": {
    "title": "Seasonal Care Packages",
    "description": "Bundle your services to increase your average booking value by 22%..."
  },
  "services": [
    {
      "id": "srv_123",
      "name": "Premium Hand Wash",
      "description": "Multi-stage foam treatment, hand wash...",
      "price_usd": 45.00,
      "duration_minutes": 45,
      "icon_type": "droplets", // Mapped to frontend Icons (e.g. Droplets, SprayCan)
      "tags": ["Popular"]
    }
  ]
}
```

### 4.2 Create/Update/Delete Service
- `POST /api/v1/garage/services`
- `PUT /api/v1/garage/services/{service_id}`
- `DELETE /api/v1/garage/services/{service_id}`

---

## 5. Match Score & Transparency (`/garage/score`)

Displays the breakdown of the AI Matching Engine's rating for this specific garage.

### 5.1 Get Diagnostic Score
`GET /api/v1/garage/score`

**Response (`200 OK`)**:
```json
{
  "aggregate_score": 72,
  "status_text": "OPTIMIZING",
  "technical_overview": {
    "comparison_text": "12% above regional average",
    "active_bays": 8,
    "total_bays": 10,
    "throughput_vph": 1.4
  },
  "score_components": {
    "equipment": { "score": 85, "description": "Condition of bays and high-pressure tech." },
    "process": { "score": 62, "description": "Workflow linearity and wait-time reduction." },
    "staff": { "score": 45, "description": "Training levels and service speed metrics." },
    "capacity": { "score": 92, "description": "Booking fill rate and downtime minimization." },
    "reliability": { "score": 78, "description": "Quality control and customer return rate." }
  },
  "progression": {
    "current_tier": "Standard",
    "next_tier": "Pro",
    "requirements_for_next": {
      "training_certs": { "current": 3, "target": 5 },
      "avg_rating": { "current": 4.2, "target": 4.5 }
    }
  },
  "ai_recommendation": {
    "title": "Priority Upgrade: Staff Training",
    "description": "Addressing the Staff score (45) could boost your aggregate efficiency by 8 points this month!"
  }
}
```
