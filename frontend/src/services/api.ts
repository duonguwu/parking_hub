// API client. Auth bằng HttpOnly cookie, không dùng localStorage.
import { API_BASE } from '@/config/app'

// Các path không được auto-refresh (tránh vòng lặp vô hạn)
const NO_REFRESH_PATHS = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout']

// Promise dùng chung: nhiều request cùng gặp 401 chỉ gọi /auth/refresh một lần
let refreshPromise: Promise<boolean> | null = null

const refreshAccessToken = (): Promise<boolean> => {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE}/auth/refresh`, { method: 'POST', credentials: 'include' })
      .then((r) => r.ok)
      .catch(() => false)
      .finally(() => { refreshPromise = null })
  }
  return refreshPromise
}

const rawFetch = (path: string, options?: RequestInit) =>
  fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
  })

// Bãi đang thao tác trong cổng chủ bãi (chủ có nhiều bãi, hoặc super_admin xem như chủ bãi)
const ACTIVE_GARAGE_KEY = 'ph_active_garage'
export const activeGarage = {
  get: (): string => localStorage.getItem(ACTIVE_GARAGE_KEY) || '',
  name: (): string => localStorage.getItem(`${ACTIVE_GARAGE_KEY}_name`) || '',
  set: (id: string, name = '') => {
    localStorage.setItem(ACTIVE_GARAGE_KEY, id)
    localStorage.setItem(`${ACTIVE_GARAGE_KEY}_name`, name)
  },
  clear: () => {
    localStorage.removeItem(ACTIVE_GARAGE_KEY)
    localStorage.removeItem(`${ACTIVE_GARAGE_KEY}_name`)
  },
}

/** Gắn garage_id vào các request của cổng chủ bãi khi đã chọn bãi. */
const withActiveGarage = (path: string): string => {
  const id = activeGarage.get()
  if (!id || !path.startsWith('/garage-portal') || path.startsWith('/garage-portal/garages') || path.includes('garage_id=')) return path
  return `${path}${path.includes('?') ? '&' : '?'}garage_id=${encodeURIComponent(id)}`
}

export const apiFetch = async (rawPath: string, options?: RequestInit) => {
  const path = withActiveGarage(rawPath)
  const res = await rawFetch(path, options)
  if (res.status !== 401 || NO_REFRESH_PATHS.some((p) => path.startsWith(p))) return res
  // Access token hết hạn → thử refresh một lần rồi gửi lại request
  const refreshed = await refreshAccessToken()
  return refreshed ? rawFetch(path, options) : res
}

/** Lấy thông báo lỗi từ response FastAPI (detail có thể là string hoặc mảng lỗi validate). */
export const errorText = (json: any, fallback: string): string => {
  const d = json?.detail ?? json?.message
  if (typeof d === 'string') return d
  if (Array.isArray(d) && d[0]?.msg) return d[0].msg
  return fallback
}

/** Gọi API, trả về `json.data`, ném Error với thông báo tiếng Việt khi lỗi. */
async function request<T>(path: string, fallback: string, options?: RequestInit): Promise<T> {
  const res = await apiFetch(path, options)
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(errorText(json, fallback))
  return json.data as T
}

const send = (method: string, body?: unknown): RequestInit =>
  ({ method, body: body === undefined ? undefined : JSON.stringify(body) })

/** Bỏ các giá trị rỗng rồi dựng query string. */
const qs = (params: Record<string, string | number | boolean | null | undefined>): string => {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '' || v === false) return
    q.set(k, String(v))
  })
  const s = q.toString()
  return s ? `?${s}` : ''
}

// ── Formatters ─────────────────────────────────────────────────────────────

/** Định dạng tiền VND: 25000 → "25.000đ" */
export const formatVnd = (n: number | null | undefined): string =>
  `${Math.round(n || 0).toLocaleString('vi-VN')}đ`

export const formatDateTime = (iso: string | null | undefined): string =>
  iso ? new Date(iso).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : '—'

export const formatTime = (iso: string | null | undefined): string =>
  iso ? new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '—'

export const formatDuration = (minutes: number): string => {
  if (minutes < 60) return `${Math.round(minutes)} phút`
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m ? `${h} giờ ${m} phút` : `${h} giờ`
}

export const UNIT_LABEL: Record<string, string> = {
  hour: 'giờ', night: 'đêm', day: 'ngày', workday: 'ngày làm việc', month: 'tháng', session: 'lượt',
}

// ── Types: phân loại bãi ───────────────────────────────────────────────────

export type LotType =
  | 'parking_building' | 'office_basement' | 'apartment_basement' | 'covered_garage'
  | 'outdoor_commercial' | 'transit_hub' | 'street' | 'residential'

export type Cover = 'basement' | 'full_roof' | 'partial_roof' | 'open'
export type AvailabilityStatus = 'available' | 'limited' | 'full' | 'unknown'

export const LOT_TYPE_LABEL: Record<string, string> = {
  parking_building: 'Nhà xe chuyên dụng',
  office_basement: 'Hầm toà nhà văn phòng',
  apartment_basement: 'Hầm chung cư',
  covered_garage: 'Nhà xe có mái',
  outdoor_commercial: 'Bãi ngoài trời',
  transit_hub: 'Đầu mối giao thông',
  street: 'Lòng đường / công cộng',
  residential: 'Chỗ nhỏ hộ dân',
}

export const COVER_LABEL: Record<string, string> = {
  basement: 'Hầm', full_roof: 'Mái che toàn phần', partial_roof: 'Mái che một phần', open: 'Ngoài trời',
}

export const GUARD_LABEL: Record<string, string> = { none: 'Không có bảo vệ', hours: 'Bảo vệ theo giờ', '24h': 'Bảo vệ 24/7' }
export const CCTV_LABEL: Record<string, string> = { none: 'Không camera', partial: 'Camera một phần', full: 'Camera toàn bãi' }
export const FLOOD_LABEL: Record<string, string> = { none: 'Không ngập', heavy_rain: 'Ngập khi mưa lớn', frequent: 'Hay ngập' }
export const PARKING_STYLE_LABEL: Record<string, string> = { self: 'Tự đỗ', attendant: 'Có người hướng dẫn', stacked: 'Đỗ chồng' }

export const INTEGRATION_LABEL: Record<number, string> = {
  1: 'Danh mục', 2: 'Có cập nhật', 3: 'Kết nối cảm nhận', 4: 'Kết nối đầy đủ',
}

/** Màu theo tình trạng chỗ trống — dùng chung cho marker, badge. */
export const AVAILABILITY_META: Record<AvailabilityStatus, { label: string; color: string; hex: string }> = {
  available: { label: 'Còn chỗ', color: 'text-success bg-success/10', hex: '#16a34a' },
  limited: { label: 'Sắp hết', color: 'text-warning bg-warning/10', hex: '#d97706' },
  full: { label: 'Hết chỗ', color: 'text-error bg-error/10', hex: '#dc2626' },
  unknown: { label: 'Chưa có dữ liệu', color: 'text-on-surface-variant bg-surface-container', hex: '#94a3b8' },
}

export interface Badge { key: string; label: string }

export interface Availability {
  has_data: boolean
  total_spots: number
  occupied: number | null
  held: number | null
  available: number | null
  occupancy_rate: number | null
  status: AvailabilityStatus
  source: string            // manual | checkin | simulated | camera
  updated_at: string | null
}

export interface Prediction {
  at: string
  expected_available: number
  occupancy_rate: number
  confidence: number
}

export interface LatLng { lat: number; lng: number }

/** Thẻ tóm tắt bãi — bản đồ, danh sách. */
export interface GarageCard {
  id: string
  name: string
  position: LatLng | null
  address: string
  district: string
  lot_type: LotType
  lot_type_label: string
  integration_level: number
  grade: number
  quality_score: number
  cover: Cover
  max_height_m: number | null
  ev_count: number
  guard: string
  flood_risk: string
  is_24h: boolean
  hourly_price: number | null
  distance_km: number | null
  availability: Availability
  badges: Badge[]
  status: string
  is_accepting_bookings: boolean
}

export interface GarageAttributes {
  cover?: Cover
  max_height_m?: number | null
  guard?: 'none' | 'hours' | '24h'
  guard_hours?: string
  cctv?: 'none' | 'partial' | 'full'
  ev_chargers?: { count?: number; power_kw?: number; connectors?: string[] }
  flood_risk?: 'none' | 'heavy_rain' | 'frequent'
  parking_style?: 'self' | 'attendant' | 'stacked'
  vehicle_types?: string[]
  large_vehicle_ok?: boolean
  lighting?: 'good' | 'basic' | 'poor'
  surface?: 'concrete' | 'asphalt' | 'gravel'
  fire_safety?: boolean
  restroom?: boolean
  payment_methods?: string[]
}

export interface GarageCapacity {
  total_spots: number
  walk_in_spots: number
  monthly_spots: number
  reservable_ratio: number
  grace_minutes: number
}

export interface DayHours { open: string; close: string; closed?: boolean }
export type OperatingHours = Partial<Record<
  'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday', DayHours
>> & { is_24h?: boolean }

export interface GarageStats {
  fulfillment_rate?: number
  no_show_rate?: number
  complaint_count?: number
  return_rate?: number
  avg_rating?: number
  rating_count?: number
  total_sessions?: number
}

/** Hồ sơ đầy đủ của bãi. */
export interface Garage {
  id: string
  tenant_id: string
  name: string
  slug: string
  position: LatLng | null
  entrance: LatLng | null
  address: { street?: string; ward?: string; district?: string; city?: string; province?: string }
  lot_type: LotType
  lot_type_label: string
  integration_level: number
  integration_label: string
  grade: number
  grade_score: number
  grade_assessment: { items?: Record<string, boolean>; note?: string; assessed_at?: string | null; assessed_by?: string }
  quality_score: number
  next_inspection_at: string | null
  capacity: GarageCapacity
  attributes: GarageAttributes
  occupancy: { occupied?: number; source?: string; updated_at?: string | null }
  availability: Availability | null
  operating_hours: OperatingHours
  services_offered: string[]
  description: string
  photos: string[]
  contacts: { phone?: string; zalo?: string; manager_name?: string }
  status: 'pending_review' | 'active' | 'suspended' | string
  is_verified: boolean
  is_accepting_bookings: boolean
  stats: GarageStats
  badges: Badge[]
  created_at: string | null
}

export interface GarageProfileUpdate {
  name?: string
  description?: string
  lot_type?: LotType
  address?: Record<string, string>
  contacts?: Record<string, string>
  operating_hours?: OperatingHours
  is_accepting_bookings?: boolean
  photos?: string[]
  capacity?: Partial<GarageCapacity>
  attributes?: GarageAttributes
  entrance?: LatLng
}

export interface ChecklistItem { key: string; group: string; points: number; label: string }

export interface Taxonomy {
  lot_types: { code: LotType; label: string }[]
  integration_levels: { level: number; name: string; desc: string }[]
  grade_checklist: ChecklistItem[]
  grade_groups: Record<string, string>
}

// ── Types: dịch vụ & giá ───────────────────────────────────────────────────

export interface PeakRule {
  days: number[]
  start: string
  end: string
  multiplier: number
}

export interface Pricing {
  mode: 'block' | 'flat'
  first_block_minutes?: number
  first_block_price?: number
  next_block_minutes?: number
  next_block_price?: number
  daily_cap?: number | null
  flat_price?: number
  flat_unit_minutes?: number | null
  peak_rules: PeakRule[]
}

export interface ServiceType {
  id: string
  code: string
  name: string
  category: 'parking' | 'subscription' | 'addon'
  unit: string
  icon: string
  description: string
  base_price_min: number
  base_price_max: number
  default_pricing: Pricing
  is_popular: boolean
  sort_order: number
  is_active?: boolean
  estimated_duration_minutes?: number
}

export interface Quote {
  amount: number
  minutes: number
  breakdown: { label: string; amount: number }[]
}

export interface PortalService {
  id: string
  service_type_code: string
  name: string
  description: string
  category: string
  unit: string
  icon: string
  price_vnd: number
  pricing: Pricing
  note: string
  bookings_30d: number
  tags: string[]
}

export interface PortalServicesOverview {
  stats: { active_services: number; bookings_30d: number; top_service: string }
  services: PortalService[]
  available_types: ServiceType[]
}

/** Dịch vụ hiển thị trên trang chi tiết bãi cho tài xế. */
export interface GarageService {
  id: string
  code: string
  name: string
  desc: string
  category: string
  unit: string
  icon: string
  sort_order: number
  time_mins: number
  price_vnd: number
  pricing: Pricing
  note: string
  is_popular: boolean
}

// ── Types: lượt đặt ────────────────────────────────────────────────────────

export type BookingStatus =
  | 'pending' | 'reserved' | 'checked_in' | 'checked_out'
  | 'cancelled' | 'rejected' | 'no_show' | 'expired'

export const ACTIVE_BOOKING_STATUSES: BookingStatus[] = ['pending', 'reserved', 'checked_in']

export const BOOKING_STATUS_MAP: Record<BookingStatus, { label: string; color: string }> = {
  pending:     { label: 'Chờ bãi xác nhận', color: 'yellow' },
  reserved:    { label: 'Đã giữ chỗ',       color: 'blue'   },
  checked_in:  { label: 'Đang gửi',         color: 'green'  },
  checked_out: { label: 'Đã ra bãi',        color: 'gray'   },
  cancelled:   { label: 'Đã huỷ',           color: 'red'    },
  rejected:    { label: 'Bãi từ chối',      color: 'red'    },
  no_show:     { label: 'Không đến',        color: 'gray'   },
  expired:     { label: 'Hết hạn',          color: 'gray'   },
}

/** Class Tailwind theo màu trạng thái. */
export const STATUS_COLOR_CLASS: Record<string, string> = {
  yellow: 'bg-warning/10 text-warning',
  blue: 'bg-primary/10 text-primary',
  green: 'bg-success/10 text-success',
  gray: 'bg-surface-container text-on-surface-variant',
  red: 'bg-error/10 text-error',
}

export interface Booking {
  id: string
  booking_code: string
  tenant_id: string
  customer_id: string | null
  garage_id: string
  vehicle_id: string | null
  license_plate: string
  service_type_code: string
  quoted_price: number
  final_price: number | null
  payment_status: 'unpaid' | 'paid'
  payment_method: string
  start_time: string
  end_time: string
  grace_until: string
  status: BookingStatus
  source: 'app' | 'walk_in' | 'matching' | string
  timestamps: Record<string, string | null>
  matching_context: Record<string, unknown>
  feedback: { rating?: number | null; quick_feedback?: string | null; comment?: string; complaint?: boolean }
  cancellation_reason: string
  cancelled_by: string
  // Có khi đi qua enrich_bookings
  garage_name?: string
  garage_address?: string
  garage_location?: LatLng
  service_name?: string
  customer_name?: string
  customer_phone?: string
  // Chỉ có ở tab "inside" của cổng chủ bãi
  current_charge?: number
  quote?: Quote
  price_breakdown?: Quote
}

export interface TrackingTimeline {
  status: string
  timestamp: string
  description: string
}

export interface BookingTracking {
  booking: Booking
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
  is_default: boolean
  is_active?: boolean
}

export interface User {
  user_id: string
  username: string
  name: string
  role: string
  tenant_id: string | null
  permissions?: string[]
}

// ── Types: app tài xế ──────────────────────────────────────────────────────

export interface DashboardSummary {
  default_vehicle: { id: string; license_plate: string; brand: string; model: string } | null
  active_bookings: Booking[]
  nearby: GarageCard[]
  stats: { total_sessions: number; total_spent: number; lots_visited: number }
}

export interface NearbyFilters {
  radius_km?: number
  lot_types?: LotType[]
  covered?: boolean
  ev?: boolean
  min_height_m?: number | null
  guard_24h?: boolean
  no_flood?: boolean
  min_grade?: number
  max_hourly_price?: number | null
  service_type?: string
  only_available?: boolean
  is_24h?: boolean
  q?: string
}

export interface GarageDetailData {
  garage: Garage
  services: GarageService[]
  hourly_today: { hour: number; rate: number; samples: number; from_history: boolean }[]
  forecast: (Prediction & { hours_ahead: number })[]
  reviews: { rating: number | null; comment: string; name: string; at: string }[]
}

export interface MatchResult {
  garage_id: string
  name: string
  tier: number
  rank: number
  total_score: number
  travel_minutes: number
  travel_distance_km: number
  predicted_arrival: string | null
  predicted_wait_minutes: number
  expected_available: number | null
  service_price: number | null
  location: LatLng
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

// ── Types: cổng chủ bãi ────────────────────────────────────────────────────

export interface PortalOverview {
  garage: {
    id: string; name: string; status: string
    integration_level: number; integration_label: string; is_accepting_bookings: boolean
  }
  availability: Availability
  inside_count: number
  pending_count: number
  upcoming: Booking[]
  revenue: { today: number; yesterday: number; sessions_today: number; unpaid_count: number }
  fill_24h: { time: string; rate: number }[]
}

export interface CapacityChart {
  range: '24H' | '7D'
  labels: string[]
  data: (number | null)[]
}

export type PortalBookingTab = 'upcoming' | 'pending' | 'inside' | 'history'

export interface PortalBookings {
  tab: PortalBookingTab
  counts: Record<'upcoming' | 'pending' | 'inside', number>
  integration_level: number
  pagination: Pagination
  items: Booking[]
}

export type BookingAction = 'confirm' | 'reject' | 'checkin' | 'checkout' | 'no_show' | 'cancel' | 'paid'

export interface PortalAnalytics {
  range: string
  metrics: {
    revenue: { value: number; trend: number | null }
    sessions: { value: number; trend: number | null }
    avg_duration_minutes: number
    avg_ticket: number
  }
  revenue_chart: { labels: string[]; data: number[] }
  source_split: { app: number; walk_in: number }
  services: { code: string; name: string; count: number; revenue: number }[]
  booking_status: Partial<Record<BookingStatus, number>>
  occupancy_by_hour: { labels: string[]; weekday: number[]; weekend: number[] }
  customers: { total: number; returning: number }
}

export interface PortalScore {
  quality_score: number
  has_enough_data: boolean
  stats: GarageStats
  integration: { level: number; name: string; desc: string }
  grade: {
    stars: number
    score: number
    groups: { key: string; label: string; score: number; max: number }[]
    items: (ChecklistItem & { passed: boolean })[]
    assessed_at: string | null
    note: string
  }
  badges: Badge[]
  next_inspection_at: string | null
  tips: string[]
}

// ── Types: admin ───────────────────────────────────────────────────────────

export interface Pagination { current_page: number; total_pages: number; total_items: number }

export interface AdminOverview {
  garages: { total: number; active: number; pending_review: number; suspended: number }
  spots: { total: number; network_occupancy: number | null; tracked_lots: number }
  bookings_30d: number
  revenue_30d: number
  fulfillment_30d: number
  by_district: { name: string; count: number }[]
  by_level: { level: number; label: string; count: number }[]
  by_type: { code: string; label: string; count: number }[]
  by_grade: { grade: number; count: number }[]
  daily: { date: string; bookings: number; revenue: number }[]
  top_garages: { id: string; name: string; sessions: number }[]
  users: Record<string, number>
}

export interface AdminGarageRow extends GarageCard {
  tenant_id: string
  grade_score: number
  is_verified: boolean
  total_spots: number
  next_inspection_at: string | null
  created_at: string | null
}

export interface AdminGarageList {
  items: AdminGarageRow[]
  pagination: Pagination
  districts: string[]
}

export interface AdminGarageDetail {
  garage: Garage
  suggested_checklist: Record<string, boolean>
  grade_preview: { score: number; grade: number; groups: Record<string, { score: number; max: number }> }
  owner: { name: string; email: string; phone: string; username: string } | null
  tenant: { name: string; status: string } | null
}

export interface AdminMeta {
  lot_types: { code: LotType; label: string }[]
  integration_levels: { level: number; name: string; desc: string }[]
  grade_groups: { key: string; label: string }[]
  grade_checklist: ChecklistItem[]
}

export interface AdminUser {
  id: string
  username: string
  name: string
  email: string
  phone: string
  role: string
  tenant_id: string | null
  garage_name: string
  is_active: boolean
  created_at: string | null
}

export const ROLE_LABEL: Record<string, string> = {
  super_admin: 'Quản trị cấp cao',
  platform_ops: 'Vận hành nền tảng',
  garage_owner: 'Chủ bãi',
  garage_manager: 'Quản lý bãi',
  garage_staff: 'Nhân viên bãi',
  customer: 'Tài xế',
  fleet_manager: 'Quản lý đội xe',
}

export const GARAGE_STATUS_LABEL: Record<string, string> = {
  pending_review: 'Chờ duyệt', active: 'Đang hoạt động', suspended: 'Tạm ngưng',
}

// ── Catalog API (public) ───────────────────────────────────────────────────

export const catalogApi = {
  serviceTypes: () => request<ServiceType[]>('/service-types', 'Không tải được danh mục dịch vụ'),

  taxonomy: () => request<Taxonomy>('/garage/taxonomy', 'Không tải được danh mục phân loại'),

  quote: (garageId: string, code: string, start: string, end: string) =>
    request<Quote>(
      `/garage-services/quote${qs({ garage_id: garageId, service_type_code: code, start_time: start, end_time: end })}`,
      'Không báo giá được',
    ),

  availability: (garageId: string, horizons: number[] = [30, 60, 120]) =>
    request<{ garage_id: string; current: Availability; predicted: Record<string, Prediction> }>(
      '/capacity/current_and_predicted', 'Không tải được chỗ trống',
      send('POST', { garage_id: garageId, horizons_min: horizons }),
    ),
}

// ── Auth API ───────────────────────────────────────────────────────────────

export const authApi = {
  login: async (username: string, password: string): Promise<User> => {
    const data = await request<{ user: User }>('/auth/login', 'Đăng nhập thất bại', send('POST', { username, password }))
    return data.user
  },

  register: async (data: { username: string; password: string; name: string; email: string; phone: string }): Promise<User> => {
    const res = await request<{ user: User }>('/auth/register', 'Đăng ký thất bại', send('POST', data))
    return res.user
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

// ── Customer (tài xế) API ──────────────────────────────────────────────────

export const customerApi = {
  dashboardSummary: (lat?: number, lng?: number) =>
    request<DashboardSummary>(`/customer/dashboard-summary${qs({ lat, lng })}`, 'Không tải được trang chủ'),

  nearbyGarages: async (lat: number, lng: number, filters: NearbyFilters = {}): Promise<GarageCard[]> => {
    const { lot_types, ...rest } = filters
    const data = await request<{ garages: GarageCard[] }>(
      `/customer/nearby${qs({ lat, lng, ...rest, lot_types: lot_types?.join(',') })}`,
      'Không tải được bãi đỗ quanh đây',
    )
    return data.garages ?? []
  },

  garageDetail: (garageId: string) =>
    request<GarageDetailData>(`/customer/garages/${garageId}/portal`, 'Không tải được thông tin bãi'),

  bookings: (status?: string) =>
    request<Booking[]>(`/customer/bookings${qs({ status })}`, 'Không tải được lượt đặt'),

  booking: (bookingId: string) =>
    request<Booking>(`/customer/bookings/${bookingId}`, 'Không tải được lượt đặt'),

  bookingTracking: (bookingId: string) =>
    request<BookingTracking>(`/customer/bookings/${bookingId}/tracking`, 'Không tải được lượt đặt'),

  createBooking: (data: {
    garage_id: string
    service_type_code: string
    start_time: string
    end_time?: string
    vehicle_id?: string
    license_plate?: string
    matching_context?: Record<string, unknown>
  }) => request<Booking>('/bookings/create', 'Không đặt được chỗ', send('POST', data)),

  cancelBooking: (id: string, reason = '') =>
    request<Booking>('/bookings/cancel', 'Không huỷ được lượt đặt', send('POST', { id, reason })),

  feedback: (id: string, data: { rating?: number; quick_feedback?: 'thumbs_up' | 'thumbs_down'; comment?: string; complaint?: boolean }) =>
    request<Booking>('/bookings/feedback', 'Không gửi được đánh giá', send('POST', { id, ...data })),

  vehicles: () => request<Vehicle[]>('/customer/vehicles', 'Không tải được danh sách xe'),

  addVehicle: (data: Partial<Vehicle>) =>
    request<Vehicle>('/customer/vehicles', 'Không thêm được xe', send('POST', data)),

  setDefaultVehicle: (vehicleId: string) =>
    request<unknown>(`/customer/vehicles/${vehicleId}/default`, 'Không đặt được xe mặc định', send('PUT')),
}

export const matchingApi = {
  search: (data: {
    current_location: LatLng
    service_type_code: string
    vehicle_id?: string
    vehicle_type?: string
    requested_time?: string
    max_travel_minutes?: number
    must_have_amenities?: string[]
    top_k?: number
  }) => request<MatchSearchResponse>('/match/search', 'Không tìm được bãi phù hợp', send('POST', data)),
}

// ── Garage owner (chủ bãi) API ─────────────────────────────────────────────

export const garageApi = {
  accessibleGarages: (q = '') =>
    request<{ id: string; name: string; district: string; status: string; lot_type: string }[]>(
      `/garage-portal/garages${qs({ q })}`, 'Không tải được danh sách bãi'),

  myGarage: () => request<Garage>('/garage-portal/garage', 'Không tải được hồ sơ bãi'),

  updateGarage: (data: GarageProfileUpdate) =>
    request<Garage>('/garage-portal/garage', 'Không lưu được hồ sơ bãi', send('PUT', data)),

  dashboardOverview: () =>
    request<PortalOverview>('/garage-portal/dashboard/overview', 'Không tải được tổng quan'),

  dashboardCapacity: (range: '24H' | '7D' = '24H') =>
    request<CapacityChart>(`/garage-portal/dashboard/capacity?range=${range}`, 'Không tải được biểu đồ lấp đầy'),

  setOccupied: (occupied: number) =>
    request<Availability>('/garage-portal/occupancy', 'Không cập nhật được chỗ trống', send('PUT', { occupied })),

  bookings: (tab: PortalBookingTab = 'upcoming', q = '', page = 1, limit = 20) =>
    request<PortalBookings>(`/garage-portal/bookings${qs({ tab, q, page, limit })}`, 'Không tải được lượt đặt'),

  bookingAction: (id: string, action: BookingAction, extra: { reason?: string; license_plate?: string; payment_method?: 'cash' | 'transfer' } = {}) =>
    request<Booking>(`/garage-portal/bookings/${id}/actions`, 'Không thực hiện được thao tác', send('POST', { action, ...extra })),

  walkIn: (license_plate: string, service_type_code = 'park_hourly') =>
    request<Booking>('/garage-portal/walk-ins', 'Không ghi nhận được xe vào', send('POST', { license_plate, service_type_code })),

  analytics: (range: '7D' | '30D' | '90D' = '30D') =>
    request<PortalAnalytics>(`/garage-portal/analytics?range=${range}`, 'Không tải được phân tích'),

  services: () => request<PortalServicesOverview>('/garage-portal/services', 'Không tải được dịch vụ'),

  createService: (data: { service_type_code: string; price?: number; pricing?: Pricing; note?: string }) =>
    request<PortalService>('/garage-portal/services', 'Không thêm được dịch vụ', send('POST', data)),

  updateService: (id: string, data: { price?: number; pricing?: Pricing; note?: string }) =>
    request<PortalService>(`/garage-portal/services/${id}`, 'Không lưu được bảng giá', send('PUT', data)),

  deleteService: (id: string) =>
    request<unknown>(`/garage-portal/services/${id}`, 'Không xoá được dịch vụ', send('DELETE')),

  score: () => request<PortalScore>('/garage-portal/score', 'Không tải được điểm chất lượng'),
}

// ── Admin API ──────────────────────────────────────────────────────────────

export const adminApi = {
  overview: () => request<AdminOverview>('/admin/overview', 'Không tải được tổng quan mạng lưới'),

  meta: () => request<AdminMeta>('/admin/meta', 'Không tải được danh mục'),

  garages: (filters: { status?: string; level?: number; lot_type?: string; district?: string; q?: string; page?: number; limit?: number } = {}) =>
    request<AdminGarageList>(`/admin/garages${qs(filters)}`, 'Không tải được danh sách bãi'),

  map: (filters: { status?: string; level?: number } = {}) =>
    request<GarageCard[]>(`/admin/map${qs(filters)}`, 'Không tải được bản đồ mạng lưới'),

  garage: (id: string) => request<AdminGarageDetail>(`/admin/garages/${id}`, 'Không tải được bãi'),

  updateGarage: (id: string, data: { status?: string; integration_level?: number; is_verified?: boolean; is_accepting_bookings?: boolean }) =>
    request<AdminGarageDetail>(`/admin/garages/${id}`, 'Không cập nhật được bãi', send('PATCH', data)),

  saveAssessment: (id: string, items: Record<string, boolean>, note = '') =>
    request<AdminGarageDetail>(`/admin/garages/${id}/assessment`, 'Không lưu được kết quả kiểm định', send('PUT', { items, note })),

  users: (filters: { role?: string; q?: string; page?: number; limit?: number } = {}) =>
    request<{ items: AdminUser[]; pagination: Pagination }>(`/admin/users${qs(filters)}`, 'Không tải được người dùng'),

  setUserActive: (id: string, is_active: boolean) =>
    request<{ id: string; is_active: boolean }>(`/admin/users/${id}`, 'Không cập nhật được tài khoản', send('PATCH', { is_active })),

  serviceTypes: () => request<ServiceType[]>('/admin/service-types', 'Không tải được danh mục dịch vụ'),

  createServiceType: (data: Partial<ServiceType>) =>
    request<ServiceType>('/admin/service-types', 'Không thêm được dịch vụ', send('POST', data)),

  updateServiceType: (code: string, data: Partial<ServiceType>) =>
    request<ServiceType>(`/admin/service-types/${code}`, 'Không lưu được dịch vụ', send('PATCH', data)),
}
