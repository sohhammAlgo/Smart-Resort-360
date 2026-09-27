export interface User {
  email?: string;
  employee_id?: string;
  role: "MANAGER" | "STAFF" | "ENGINEERING" | "GUEST";
  booking_id?: number;
  department?: string;
}

export interface Amenity {
  id: number;
  name: string;
  category: string;
  status: "FREE" | "BUSY" | "MAINTENANCE";
  capacity: number;
  description: string | null;
}

export interface WaitlistJoinResponse {
  waitlist_id: number;
  status: string;
}

export interface OfferActionResponse {
  offer_id: number;
  status: string;
  message: string;
}

export interface AlternativeAmenity {
  id: number;
  name: string;
  category: string;
  description: string | null;
  capacity: number;
  similarity_score?: number;
}

export interface Asset {
  asset_id: number;
  asset_type: string;
  room_or_location: string;
  installation_date: string;
  last_service_date: string;
  service_interval_days: number;
  linked_amenity_id: number | null;
}

export interface MaintenanceRisk {
  asset_id: number;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  calculated_at?: string;
}

export interface ServiceTicket {
  ticket_id: number;
  location: string;
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CANCELLED";
  source: string;
  issue_category?: string;
  department?: string;
  assigned_employee_id?: string | null;
}

export interface BuggyRequestResponse {
  request_id: number;
  status: string;
  eta_minutes: number;
  assigned_driver_id?: string | null;
}

export interface FolioItem {
  folio_id: number;
  category: string;
  description: string;
  amount: string;
  status: string;
}

export interface OccupancyForecast {
  occupancy_rate: number;
  occupied_rooms: number;
  total_rooms: number;
  forecast_date: string;
}

export interface DemandForecast {
  demand_level: string;
  multiplier: number;
  forecast_date: string;
}

export interface PricingRecommendation {
  recommended_price: number;
  occupancy_forecast: number;
  base_price: number;
}

export interface SentimentAnalysis {
  sentiment: string;
  score: number;
  key_aspects: string[];
}

export interface StaffingRecommendation {
  recommended_staff_count: number;
  occupancy_forecast_pct: number;
  notes: string;
}

export interface ScenarioSimulation {
  simulated_occupancy_pct: number;
  impact_summary: {
    pricing_multiplier: number;
    recommended_staff: number;
    risk_assessment: string;
  };
}
