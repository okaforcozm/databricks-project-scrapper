export interface Region {
  id: string;
  name: string;
  code: string;
  countries: string[];
}

export interface FamilySize {
  id: string;
  label: string;
  adults: number;
  children: number;
  multiplier: number;
}

export interface Seniority {
  id: string;
  label: string;
  description: string;
  multiplier: number;
}

export interface CostType {
  id: 'flights' | 'accommodation' | 'shipping';
  label: string;
  icon: string;
  description: string;
}

export interface FlightCostData {
  origin: string;
  destination: string;
  familySize: string;
  cost: number;
  currency: 'USD';
  isPeakCost: boolean;
  lastUpdated: string;
}

export interface AccommodationCostData {
  origin: string;
  destination: string;
  familySize: string;
  cost: number;
  currency: 'USD';
  provider: 'Alto Vita' | 'Silverdoor' | 'Other';
  isPeakCost: boolean;
  lastUpdated: string;
}

export interface ShippingCostData {
  origin: string;
  destination: string;
  containerType: '20ft' | '40ft';
  cost: number;
  currency: 'USD';
  service: 'FCL' | 'LCL';
  transitTime: string;
  lastUpdated: string;
}

export interface CostMatrix {
  flights: Record<string, Record<string, Record<string, number>>>;
  accommodation: Record<string, Record<string, Record<string, number>>>;
  shipping: Record<string, Record<string, Record<string, number>>>;
}

export interface EvidenceData {
  id: string;
  costType: CostType['id'];
  source: string;
  url?: string;
  screenshot?: string;
  extractedData: any;
  timestamp: string;
  verified: boolean;
}

export interface CostSummary {
  costType: CostType['id'];
  origin: string;
  destination: string;
  totalRoutes: number;
  avgCost: number;
  minCost: number;
  maxCost: number;
  outliers: number;
  lastUpdated: string;
}

export interface DashboardFilters {
  originRegion: string;
  destinationRegion: string;
  seniority?: string;
  familySize?: string;
  containerType?: string;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  category?: string;
  color?: string;
} 