// API client. Auth bằng HttpOnly cookie, không dùng localStorage.
import { API_BASE } from '@/config/app'

export const apiFetch = async (path: string, options?: RequestInit) => {
  return fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
  })
}

// ── Types ──────────────────────────────────────────────────────────────────

export interface User {
  user_id: string
  username: string
  name: string
  role: string
  tenant_id: string | null
  permissions?: string[]
}

export interface VehicleDiagnostics {
  default_vehicle_id: string
  license_plate: string
  brand: string
  model: string
  vehicle_type: string
  finish_degradation: number
  days_since_last_service: number
}

export interface GarageRecommendation {
  id: string
  name: string
  tier: string
  distance: string
  wait_time: string
  status: string
  score: number
  lat: number
  lng: number
}

export interface ActiveBooking {
  id: string
  booking_code: string
  status: string
  garage_id: string
  service_type_code: string
  price: number
  requested_time: string
}

export interface DashboardSummary {
  vehicle_diagnostics: VehicleDiagnostics | null
  smart_recommendations: GarageRecommendation[]
  active_booking: ActiveBooking | null
}

export interface NearbyGarage {
  id: string
  name: string
  lat: number
  lng: number
  score: number
  distance: string
  tier: string
  active: boolean
}

export interface GarageService {
  id: string
  code: string
  name: string
  desc: string
  category: string
  time_mins: number
  price_vnd: number
  is_popular: boolean
}

export interface GaragePortal {
  info: {
    name: string
    slug: string
    tier: string
    tier_num: number
    efficiency_score: number
    is_verified: boolean
    is_accepting_bookings: boolean
    address: { street: string; ward: string; district: string; city: string }
    description: string
    photos: string[]
    stats: {
      total_services: number
      avg_rating: number
      retention_rate: number
      on_time_rate: number
    }
    metrics: {
      equipment: number
      process: number
      staff: number
      capacity: number
      reliability: number
    }
  }
  amenities: string[]
  services: GarageService[]
  capacity_load: { time: string; load_percent: number }[]
}

export interface Booking {
  id: string
  booking_code: string
  tenant_id: string
  customer_id: string
  garage_id: string
  vehicle_id: string
  service_type_code: string
  price: number
  requested_time: string
  estimated_arrival: string
  status: string
  timestamps: Record<string, string | null>
  matching_context: { match_score: number; estimated_travel_minutes: number }
  feedback: { rating: number | null; quick_feedback: string | null; comment: string } | null
  cancellation_reason: string
  cancelled_by: string
}

export interface TrackingTimeline {
  status: string
  timestamp: string
  description: string
}

export interface BookingTracking {
  booking: Pick<Booking, 'id' | 'booking_code' | 'status' | 'service_type_code' | 'price' | 'garage_id'>
  timeline: TrackingTimeline[]
}

export interface Vehicle {
  id: string
  owner_user_id?: string
  license_plate: string
  brand: string
  model: string
  year: number
  color: string
  vehicle_type: string
  body_type: string
  size_class: string
  minimum_garage_tier?: number
  vetc_linked?: boolean
  is_default: boolean
  is_active?: boolean
}

export interface MatchResult {
  garage_id: string
  name: string
  tier: string
  rank: number
  total_score: number
  travel_minutes: number
  travel_distance_km: number
  predicted_arrival: string | null
  predicted_wait_minutes: number
  service_price: number | null
  location: { lat: number; lng: number }
  component_scores: Record<string, number>
  reasons: { type: string; text: string }[]
  trade_offs: { type: string; text: string }[]
}

export interface MatchSearchResponse {
  search_id: string
  session_id: string
  results_count: number
  matches: MatchResult[]
}

// ── Status / tier maps ────────────────────────────────────────────────────

export const BOOKING_STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending:               { label: 'Chờ xác nhận',   color: 'yellow' },
  confirmed:             { label: 'Đã xác nhận',    color: 'blue'   },
  customer_arriving:     { label: 'Đang đến',        color: 'blue'   },
  customer_arrived:      { label: 'Đã đến',          color: 'green'  },
  in_service:            { label: 'Đang phục vụ',    color: 'blue'   },
  completed:             { label: 'Hoàn thành',      color: 'green'  },
  cancelled_by_customer: { label: 'Đã hủy',          color: 'red'    },
  cancelled_by_garage:   { label: 'Gara hủy',        color: 'red'    },
  no_show:               { label: 'Không đến',       color: 'gray'   },
}

export const TIER_COLOR: Record<string, string> = {
  BASIC:    'bg-slate-100 text-slate-600',
  STANDARD: 'bg-indigo-100 text-indigo-700',
  PRO:      'bg-amber-100 text-amber-800',
  ELITE:    'bg-gradient-to-r from-amber-200 to-orange-200 text-amber-900',
}

// ── Auth API ──────────────────────────────────────────────────────────────

export const authApi = {
  login: async (username: string, password: string): Promise<User> => {
    const res = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || json.message || 'Login failed')
    return json.data.user as User
  },

  register: async (data: {
    username: string
    password: string
    name: string
    email: string
    phone: string
  }): Promise<User> => {
    const res = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || json.message || 'Register failed')
    return json.data.user as User
  },

  me: async (): Promise<User | null> => {
    try {
      const res = await apiFetch('/auth/me')
      if (!res.ok) return null
      const json = await res.json()
      return json.data as User
    } catch {
      return null
    }
  },

  logout: async () => {
    await apiFetch('/auth/logout', { method: 'POST' })
  },
}

// ── Customer API ──────────────────────────────────────────────────────────

export const customerApi = {
  dashboardSummary: async (lat?: number, lng?: number): Promise<DashboardSummary> => {
    const params = lat && lng ? `?lat=${lat}&lng=${lng}` : ''
    const res = await apiFetch(`/customer/dashboard-summary${params}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load dashboard')
    return json.data as DashboardSummary
  },

  nearbyGarages: async (lat: number, lng: number, radiusKm = 10): Promise<NearbyGarage[]> => {
    const res = await apiFetch(`/customer/nearby?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load nearby garages')
    return (json.data?.garages ?? json.data ?? []) as NearbyGarage[]
  },

  garagePortal: async (garageId: string): Promise<GaragePortal> => {
    const res = await apiFetch(`/customer/garages/${garageId}/portal`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load garage')
    return json.data as GaragePortal
  },

  bookings: async (status?: string): Promise<Booking[]> => {
    const params = status ? `?status=${status}` : ''
    const res = await apiFetch(`/customer/bookings${params}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load bookings')
    return (json.data ?? []) as Booking[]
  },

  bookingTracking: async (bookingId: string): Promise<BookingTracking> => {
    const res = await apiFetch(`/customer/bookings/${bookingId}/tracking`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load tracking')
    return json.data as BookingTracking
  },

  vehicles: async (): Promise<Vehicle[]> => {
    const res = await apiFetch('/customer/vehicles')
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load vehicles')
    return (json.data ?? []) as Vehicle[]
  },

  addVehicle: async (data: Partial<Vehicle>): Promise<Vehicle> => {
    const res = await apiFetch('/customer/vehicles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to add vehicle')
    return json.data as Vehicle
  },

  setDefaultVehicle: async (vehicleId: string) => {
    const res = await apiFetch(`/customer/vehicles/${vehicleId}/default`, { method: 'PUT' })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to set default')
    return json
  },

  createBooking: async (data: {
    garage_id: string
    service_type_code: string
    requested_time: string
    vehicle_id: string
    matching_context?: Record<string, unknown>
  }) => {
    const res = await apiFetch('/bookings/create', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to create booking')
    return json.data
  },
}

export const matchingApi = {
  search: async (data: {
    current_location: { lat: number; lng: number }
    service_type_code: string
    vehicle_id?: string
    vehicle_type?: string
    requested_time?: string
    max_travel_minutes?: number
    top_k?: number
  }): Promise<MatchSearchResponse> => {
    const res = await apiFetch('/match/search', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Match search failed')
    return json.data as MatchSearchResponse
  },
}

// ── Garage Owner API ──────────────────────────────────────────────────────

export const garageApi = {
  dashboardOverview: async () => {
    const res = await apiFetch('/garage-portal/dashboard/overview')
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load dashboard overview')
    return json.data
  },

  dashboardCapacity: async (range: string = '24H') => {
    const res = await apiFetch(`/garage-portal/dashboard/capacity?range=${range}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load capacity chart')
    return json.data
  },

  queue: async (filter: string = 'all', page: number = 1, limit: number = 10) => {
    const res = await apiFetch(`/garage-portal/queue?filter=${filter}&page=${page}&limit=${limit}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load queue')
    return json.data
  },

  updateBookingStatus: async (id: string, status: string) => {
    const res = await apiFetch(`/garage-portal/queue/bookings/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to update booking status')
    return json.data
  },

  analytics: async (range: string = '30D') => {
    const res = await apiFetch(`/garage-portal/analytics?range=${range}`)
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load analytics')
    return json.data
  },

  services: async () => {
    const res = await apiFetch('/garage-portal/services')
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load services')
    return json.data
  },

  createService: async (data: { service_type_code: string; price_usd: number; duration_minutes: number }) => {
    const res = await apiFetch('/garage-portal/services', {
      method: 'POST',
      body: JSON.stringify(data)
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to create service')
    return json.data
  },

  updateService: async (id: string, data: { price_usd?: number; duration_minutes?: number }) => {
    const res = await apiFetch(`/garage-portal/services/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to update service')
    return json.data
  },

  deleteService: async (id: string) => {
    const res = await apiFetch(`/garage-portal/services/${id}`, {
      method: 'DELETE'
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to delete service')
    return json.data
  },

  score: async () => {
    const res = await apiFetch('/garage-portal/score')
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Failed to load score')
    return json.data
  }
}
